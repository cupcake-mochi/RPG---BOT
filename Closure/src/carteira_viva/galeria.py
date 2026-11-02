"""Aplicação da galeria: projeções explícitas, membros e capacidades atuais."""
import asyncio
from .segredos import AcessoNegado,Conflito,ErroCarteira
from .provedores import MembroAusente
from .permissoes import Membro


class Galeria:
    def __init__(self,dados,provedores,consultas,imagens):
        self.dados,self.provedores,self.consultas,self.imagens=dados,provedores,consultas,imagens

    async def banco(self,metodo,*args,**kw):
        return await self.dados.chamar('cadastro.'+metodo,*args,**kw)

    async def membro(self,s,u):
        return await self.provedores.membro(s,u)

    async def modelos(self,s,u):
        return await self.banco('modelos',await self.membro(s,u))

    async def configurar_modelo(self,s,u,*,escolha,revisao):
        if escolha not in ('oficiais','era','ciclo'):
            raise ErroCarteira('Escolha o modelo personalizado pelo Picker.')
        return await self.banco('configurar_modelo',await self.membro(s,u),escolha=escolha,revisao=revisao)

    async def criar_por_modelo(self,s,u,*,modelo,parametros=None):
        return await self.banco('criar_por_modelo',await self.membro(s,u),modelo=modelo,parametros=parametros)

    async def _dono(self,m,pid):
        dono=await self.banco('dono_personagem',m,pid)
        try: return await self.membro(m.servidor,dono)
        except MembroAusente:
            await self.banco('registrar_saida',m.servidor,dono)
            raise AcessoNegado('O responsável não está mais neste servidor.') from None

    async def listar(self,s,u,*,dono=None,depois=''):
        if ((dono is not None and (not isinstance(dono,str) or not dono.isdigit() or len(dono)>22)) or
                not isinstance(depois,str) or (depois and (len(depois)!=32 or any(c not in '0123456789abcdef' for c in depois)))):
            raise ErroCarteira('Jogador ou página inválidos.')
        m=await self.membro(s,u);dono=dono or u
        try:
            alvo=await self.membro(s,dono)
        except MembroAusente:
            await self.banco('registrar_saida',s,dono)
            return {'cartoes':[],'proximo':None}
        await self.banco('registrar_retorno',alvo)
        cards=await self.banco('listar',m,dono=dono,depois=depois,limite=21)
        proximo=cards[19]['id'] if len(cards)>20 else None
        cards=[await self.banco('cartao_galeria',m,c['id']) for c in cards[:20]]
        cards=[c|{'responsavel_nome':alvo.nome} for c in cards]
        await self.membro(s,u)
        return {'cartoes':cards,'proximo':proximo}

    async def cartao(self,s,u,pid,*,atualizar=True):
        m=await self.membro(s,u);await self._dono(m,pid)
        card=await self.banco('cartao_galeria',m,pid)
        aviso=None
        if atualizar and card['capacidades']['ver_detalhes']:
            try: await self.consultas.atualizar(s,u,pid)
            except ErroCarteira: aviso='atualizacao_indisponivel'
        m=await self.membro(s,u);dono=await self._dono(m,pid)
        return (await self.banco('cartao_galeria',m,pid))|{'aviso':aviso,'responsavel_nome':dono.nome}

    async def cartao_salvo(self,s,u,pid):
        return await self.cartao(s,u,pid,atualizar=False)

    async def detalhes(self,s,u,pid,*,analisar=False):
        m=await self.membro(s,u);await self._dono(m,pid)
        if analisar:
            analise=await self.consultas.analisar(s,u,pid)
            lid=analise['origem']['leitura_id']
        else:
            leitura=await self.consultas.atualizar(s,u,pid)
            lid=leitura['leitura_id'];analise=None
        m=await self.membro(s,u);await self._dono(m,pid)
        d=await self.banco('detalhes',m,pid)
        if not d['leitura'] or d['leitura']['id']!=lid: raise Conflito('Outra leitura substituiu este resultado.')
        return {'cartao':await self.banco('cartao_galeria',m,pid),'arquivo':d['arquivo'],'revisao':d['revisao'],
                'leitura':d['leitura'],'analise':analise}

    async def editar(self,s,u,pid):
        m=await self.membro(s,u);await self._dono(m,pid)
        return await self.banco('perfil_editavel',m,pid)

    async def preparar(self,s,u,pid,*,alteracoes,campos_publicos,remover_imagem=False,base_esperada=None):
        m=await self.membro(s,u);await self._dono(m,pid)
        return await self.banco('preparar_cartao',m,pid,alteracoes=alteracoes,campos_publicos=campos_publicos,
                               imagem='' if remover_imagem else None,base_esperada=base_esperada)

    async def confirmar(self,s,u,pid,*,previa):
        m=await self.membro(s,u);await self._dono(m,pid)
        return await self.banco('confirmar_cartao',m,pid,previa)

    async def cancelar(self,s,u,pid,*,previa):
        m=await self.membro(s,u)
        await self.banco('cancelar_cartao',m,pid,previa)
        return {'ok':True}

    async def enviar_imagem(self,s,u,pid,dados):
        m=await self.membro(s,u);await self._dono(m,pid)
        await self.banco('pode_enviar_imagem',m,pid)
        atual=await self.banco('perfil_editavel',m,pid)
        dados=await self.imagens.validar(dados)
        m=await self.membro(s,u);await self._dono(m,pid)
        # Permissão é reconferida depois da decodificação antes de persistir.
        await self.banco('perfil_editavel',m,pid)
        mid=await asyncio.to_thread(self.imagens.salvar,s,pid,dados)
        await self.banco('registrar_imagem',m,pid,mid)
        return await self.banco('preparar_cartao',m,pid,alteracoes={},
                               campos_publicos=set(atual['campos_publicos'])|{'imagem_id'},imagem=mid,base_esperada=atual['base'])

    async def imagem(self,s,u,pid,*,previa=None):
        m=await self.membro(s,u);await self._dono(m,pid)
        mid=await self.banco('imagem_cartao',m,pid,previa=previa)
        if not mid: raise ErroCarteira('Cartão sem imagem pública.')
        b=await asyncio.to_thread(self.imagens.ler,s,pid,mid)
        m=await self.membro(s,u);await self._dono(m,pid)
        if mid!=await self.banco('imagem_cartao',m,pid,previa=previa): raise Conflito('A imagem mudou.')
        return b

    async def limpar(self):
        ativos=await self.banco('imagens_ativas')
        await asyncio.to_thread(self.imagens.limpar,set(ativos))

    async def analise_salva(self,s,u,pid):
        a=await self.consultas.analise_salva(s,u,pid)
        m=await self.membro(s,u);await self._dono(m,pid)
        d=await self.banco('detalhes',m,pid)
        if not d['leitura'] or d['leitura']['id']!=a['origem']['leitura_id']:
            raise Conflito('A leitura mudou. Analise novamente.')
        return {'cartao':await self.banco('cartao_galeria',m,pid),'arquivo':d['arquivo'],'revisao':d['revisao'],'leitura':d['leitura'],'analise':a}

    async def cargo_revisor(self,s,u,*,cargo,permitir):
        if not isinstance(cargo,str) or not cargo.isdigit() or len(cargo)>22 or type(permitir) is not bool:
            raise ErroCarteira('Cargo inválido.')
        m=await self.membro(s,u)
        await self.banco('alterar_revisor',m,cargo,permitir)
        return {'ok':True}
