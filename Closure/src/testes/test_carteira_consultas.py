"""Serviço completo com banco cifrado real, Google/Discord fictícios e motor real."""
import asyncio
import copy
from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from carteira_viva.consultas import Consultas
from carteira_viva.fluxos import DadosAsync
from carteira_viva.motor import Motor
from carteira_viva.permissoes import Membro
from carteira_viva.provedores import ErroProvedor
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from closure_bot.ficha_corretor import conferir
from closure_bot.ficha_leitor import Campo, FichaIlegivel, de_csv
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_web import ProvedorFicticio, F1, F2
from testes.test_carteira_leitura import da_grade, grade, linhas_ficha, ARQUIVO
from testes.test_r53 import completa_r53 as _completa_r53, csvfile_texto, gravar
from testes.test_b47_integracao import completa, trocar
from testes.test_b47_revisao import aprovar_tudo

RAIZ=Path(__file__).resolve().parents[2]


def completa_r53():
    # A fixture anterior usa o nome curto do discovery. Mantém execução também
    # por módulo sem alterar o helper histórico ou o sys.path do serviço.
    import sys
    from testes import test_b47_integracao
    with patch.dict(sys.modules, {"test_b47_integracao": test_b47_integracao}):
        return _completa_r53()


class GoogleFicticio(ProvedorFicticio):
    def __init__(self, cfg, agora):
        super().__init__(cfg, agora)
        self.ficha={"formato.versao":Campo(12,"","cabeçalho"),"nome":Campo("Fictício","","entrada")}
        self.leituras=0; self.bloqueio=None; self.entrou=asyncio.Event(); self.erro=None
        self.admin=False
    async def membro(self, servidor, usuario):
        return replace(await super().membro(servidor, usuario), administrador=self.admin)
    async def ler_analise(self, acesso, arquivo):
        self.leituras+=1; self.entrou.set()
        if self.bloqueio: await self.bloqueio.wait()
        if self.erro: raise self.erro
        return copy.deepcopy(self.ficha), str(self.leituras)


class ConsultasTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory(); p=Path(self.tmp.name)
        self.clock=[180000.]; self.agora=lambda:self.clock[0]
        self.cfg=configuracao(p/"db.sqlite3",servidores=frozenset({"111","333"}))
        self.dados=DadosAsync(self.cfg,agora=self.agora); await self.dados.iniciar()
        self.prov=GoogleFicticio(self.cfg,self.agora)
        self.campanhas=p/"campanhas.json"; self.campanhas.write_text("{}")
        self.motor=Motor(RAIZ/"dados",self.campanhas)
        self.s=Consultas(self.dados,self.prov,self.motor,agora=self.agora,esperas=(0,0))
        self.m=Membro("111","222")
        self.cid=await self.b("conectar",self.m,conta="ficticia",cliente=self.cfg.google_id,refresh_token="refresh_ficticio")
        self.p=await self.b("cadastrar",self.m,conexao=self.cid,arquivo=F1,nome="Exemplo",contrato="analise-12",responsabilidade=True,pedido="cadastro")
        self.pid=self.p["id"]
    async def asyncTearDown(self):
        await self.s.fechar(); await self.dados.fechar(); self.tmp.cleanup()
    async def b(self,metodo,*args,**kw): return await self.dados.chamar("cadastro."+metodo,*args,**kw)
    async def detalhes(self): return await self.b("detalhes",self.m,self.pid)
    async def trocar(self):
        return await self.b("trocar_arquivo",self.m,self.pid,arquivo=F2,conexao=self.cid,contrato="analise-12",revisao=1,pedido="troca")

    async def test_cache_curto_e_analise_explicita_rele(self):
        a=await self.s.atualizar("111","222",self.pid); b=await self.s.atualizar("111","222",self.pid)
        self.assertFalse(a["cache"]); self.assertTrue(b["cache"]); self.assertEqual(self.prov.leituras,1)
        self.clock[0]+=61
        await self.s.atualizar("111","222",self.pid); self.assertEqual(self.prov.leituras,2)
        await self.s.analisar("111","222",self.pid); self.assertEqual(self.prov.leituras,3)

    async def test_pedidos_repetidos_coalescem(self):
        self.prov.bloqueio=asyncio.Event()
        ts=[asyncio.create_task(self.s.atualizar("111","222",self.pid)) for _ in range(8)]
        await self.prov.entrou.wait(); await asyncio.sleep(.02); self.prov.bloqueio.set()
        saidas=await asyncio.gather(*ts)
        self.assertEqual(self.prov.leituras,1); self.assertEqual(self.prov.renovacoes,1)
        self.assertEqual(len({x["leitura_id"] for x in saidas}),1)

    async def test_nao_dono_nao_consulta_google(self):
        with self.assertRaises(AcessoNegado): await self.s.atualizar("111","999",self.pid)
        self.assertEqual(self.prov.leituras,0)

    async def test_admin_revisor_e_remocao_do_cargo(self):
        await self.b("configurar",replace(self.m,administrador=True),revisores=("revisor",))
        original=self.prov.membro
        async def revisor(s,u): return replace(await original(s,u),cargos=frozenset({"revisor"}))
        self.prov.membro=revisor
        await self.s.analisar("111","999",self.pid)
        self.prov.membro=original
        with self.assertRaises(AcessoNegado): await self.s.analise_salva("111","999",self.pid)
        self.prov.admin=True
        self.assertIn("resultado",await self.s.analise_salva("111","999",self.pid))

    async def test_saida_durante_leitura_nao_salva(self):
        self.prov.bloqueio=asyncio.Event()
        t=asyncio.create_task(self.s.atualizar("111","222",self.pid)); await self.prov.entrou.wait()
        self.prov.presente=False; self.prov.bloqueio.set()
        with self.assertRaises(AcessoNegado): await t
        self.assertIsNone((await self.detalhes())["leitura"])

    async def test_troca_durante_leitura_descarta_resultado_antigo(self):
        self.prov.bloqueio=asyncio.Event()
        t=asyncio.create_task(self.s.atualizar("111","222",self.pid)); await self.prov.entrou.wait()
        await self.trocar(); self.prov.bloqueio.set()
        with self.assertRaises(Conflito): await t
        d=await self.detalhes(); self.assertEqual(d["arquivo"],F2); self.assertIsNone(d["leitura"])

    async def test_reautorizacao_durante_leitura_descarta(self):
        self.prov.bloqueio=asyncio.Event()
        t=asyncio.create_task(self.s.atualizar("111","222",self.pid)); await self.prov.entrou.wait()
        await self.b("conectar",self.m,conta="ficticia",cliente=self.cfg.google_id,refresh_token="novo_ficticio")
        self.prov.bloqueio.set()
        with self.assertRaises(Conflito): await t
        self.assertIsNone((await self.detalhes())["leitura"])

    async def test_revogacao_bloqueia_snapshot_anterior(self):
        await self.s.atualizar("111","222",self.pid)
        self.prov.falha_renovacao=True
        with self.assertRaises(ErroProvedor): await self.s.atualizar("111","222",self.pid,forcar=True)
        with self.assertRaises(ErroCarteira): await self.detalhes()

    async def test_falha_nao_retorna_cache_antigo(self):
        await self.s.analisar("111","222",self.pid)
        self.prov.erro=FichaIlegivel("erro ficticio")
        with self.assertRaises(FichaIlegivel): await self.s.atualizar("111","222",self.pid,forcar=True)
        d=await self.detalhes(); self.assertIsNone(d["leitura"]); self.assertIsNone(d["analise"])

    async def test_analise_campanha_mudou_nao_reutiliza(self):
        await self.s.analisar("111","222",self.pid)
        self.campanhas.write_text(json.dumps({"111":{"nome":"outra campanha"}}))
        with self.assertRaises(Conflito): await self.s.analise_salva("111","222",self.pid)

    async def test_campanha_corrompida_ou_ausente_nao_cai_no_padrao(self):
        for valor in ("{", "[]", '{"111":[]}'):
            self.campanhas.write_text(valor)
            with self.subTest(valor=valor),self.assertRaises(ErroCarteira): self.motor.campanha("111")
        self.campanhas.unlink()
        with self.assertRaises(ErroCarteira): self.motor.campanha("111")

    async def test_isolamento_servidor_e_cartao_sem_snapshot(self):
        await self.s.analisar("111","222",self.pid)
        card=await self.b("cartao",self.m,self.pid)
        for chave in ("arquivo","leitura","analise","resultado","refresh_token"): self.assertNotIn(chave,card)
        with self.assertRaises(ErroCarteira): await self.s.analise_salva("333","222",self.pid)

    async def test_metadados_e_limites_do_motor_preservados(self):
        self.prov.ficha= completa_r53()
        esperado=asdict(conferir(self.prov.ficha,self.motor.referencias))
        a=await self.s.analisar("111","222",self.pid)
        self.assertEqual(a["resultado"],esperado); self.assertEqual(a["mecanica"],"R53")
        self.assertEqual(a["origem"]["arquivo"],F1); self.assertEqual(a["origem"]["revisao"],1)
        self.assertEqual(a["campanha"]["servidor"],"111"); self.assertTrue(a["resultado"]["nao_conferido"])

    async def test_paridade_simples_avancada_custom_incompleta_e_adulterada(self):
        simples=completa_r53()
        avancada=copy.deepcopy(simples); gravar(avancada,"feitico.1",1)
        custom=trocar(completa(),origem="Origem fictícia",custom__1__tipo="Origem",custom__1__nome="Origem fictícia",
                      custom__1__campo__base_do_livro="Latente",custom__1__campo__rota="Fundamento",custom__1__mestre_viu=1)
        aprovacoes=aprovar_tudo(custom).impressoes
        adulterada=copy.deepcopy(simples); adulterada["vida_max"]=Campo(999,"","resultado")
        incompleta=copy.deepcopy(simples); incompleta.pop("nivel")
        for nome,f,aprovados in [("simples",simples,{}),("avancada",avancada,{}),("custom_sem",custom,{}),("custom_com",custom,aprovacoes),("incompleta",incompleta,{}),("adulterada",adulterada,{})]:
            with self.subTest(nome=nome):
                self.campanhas.write_text(json.dumps({"111":{"nome":"Campanha QA","aprovados":aprovados}}))
                normalizada=da_grade(grade(linhas_ficha(f)),ARQUIVO)
                self.assertEqual(normalizada,de_csv(csvfile_texto(f)))
                self.prov.ficha=normalizada
                ctx=self.motor.campanha("111")
                esperado=asdict(conferir(normalizada,self.motor.referencias,ctx.regras,ctx.aprovados))
                a=await self.s.analisar("111","222",self.pid)
                self.assertEqual(a["resultado"],esperado)
                if nome=="adulterada": self.assertTrue(any(p["campo"]=="vida_max" for p in a["resultado"]["problemas"]))

    async def test_transicao_nao_aprova_e_leitura_nao_mistura(self):
        with patch("closure_bot.ficha_r53.transicoes",return_value={"feitico.1":"salvando"}):
            a=await self.s.analisar("111","222",self.pid)
        self.assertEqual(self.prov.leituras,3); self.assertEqual(a["origem"]["em_transicao"],1)
        self.assertNotEqual(a["resultado"]["veredito"],"aprovada")

    async def test_campanha_muda_no_motor_nao_salva(self):
        original=self.motor.conferir
        def mudar(f,c):
            r=original(f,c); self.campanhas.write_text('{"111":{"nome":"mudou"}}'); return r
        self.motor.conferir=mudar
        with self.assertRaises(Conflito): await self.s.analisar("111","222",self.pid)
        self.assertIsNone((await self.detalhes())["analise"])

    async def test_resultado_excessivo_nao_e_truncado_ou_salvo(self):
        self.motor.conferir=lambda f,c:{"veredito":"pendente","nao_conferido":["x"*(2*1024*1024)]}
        with self.assertRaisesRegex(ErroCarteira,"limite de resposta"): await self.s.analisar("111","222",self.pid)
        self.assertIsNone((await self.detalhes())["analise"])

    async def test_motor_novo_nao_reutiliza_analise_antiga(self):
        await self.s.analisar("111","222",self.pid)
        self.motor.revisao="outra_revisao"
        with self.assertRaises(Conflito): await self.s.analise_salva("111","222",self.pid)

    async def test_refresh_rotacionado_e_salvo_sem_trocar_identidade(self):
        async def renovar(refresh):
            self.assertEqual(refresh,"refresh_ficticio")
            return self.prov.token_google({"access_token":"ficticio", "refresh_token":"novo_refresh_ficticio", "expires_in":3600})
        self.prov.renovar=renovar
        await self.s.atualizar("111","222",self.pid)
        ref=await self.b("reservar_leitura",self.m,self.pid)
        cred=await self.b("_credencial",self.m,ref)
        self.assertEqual(cred.refresh_token,"novo_refresh_ficticio"); self.assertEqual(cred.conta,"ficticia")

    async def test_refresh_simultaneo_da_mesma_conta_serializado(self):
        p=await self.b("cadastrar",self.m,conexao=self.cid,arquivo=F2,nome="Segundo",contrato="analise-12",responsabilidade=True,pedido="segundo")
        self.prov.admin=True; em_uso=0; maximo=0; tokens=[]
        async def renovar(refresh):
            nonlocal em_uso,maximo
            em_uso+=1; maximo=max(maximo,em_uso); tokens.append(refresh)
            await asyncio.sleep(.02); em_uso-=1
            return self.prov.token_google({"access_token":"ficticio","refresh_token":"rotacionado","expires_in":3600})
        self.prov.renovar=renovar
        await asyncio.gather(self.s.atualizar("111","222",self.pid),self.s.atualizar("111","999",p["id"]))
        self.assertEqual(maximo,1); self.assertEqual(tokens,["refresh_ficticio","rotacionado"])

    async def test_credencial_ilegivel_invalida_snapshot_antigo(self):
        await self.s.analisar("111","222",self.pid)
        original=self.s._banco
        async def falhar(metodo,*args,**kw):
            if metodo=="_credencial": raise ErroCarteira("Falha fictícia ao abrir a credencial")
            return await original(metodo,*args,**kw)
        self.s._banco=falhar
        with self.assertRaises(ErroCarteira): await self.s.atualizar("111","222",self.pid,forcar=True)
        self.assertIsNone((await self.detalhes())["leitura"])
