"""Cadastro confiável do operador, fora da planilha do jogador e fora do Git.

Execute --help para inspecionar/aprovar uma definição exata ou alterar uma regra.
Somente hashes e identificação da aprovação são retidos, nunca a ficha recebida.
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RAIZ/'src'))
from closure_bot.ficha_corretor import Referencias, Resultado, RegrasDaCampanha
from closure_bot.ficha_configuracao import (ContextoB47, carregar_campanha, regras_autorizadas,
                                           conferir_efeitos, impressao_exata, valor)
from closure_bot.ficha_custom import preparar_custom
from closure_bot.ficha_leitor import de_xlsx, de_csv


def gravar(arquivo,dados):
    arquivo.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=arquivo.parent,delete=False) as f:
        json.dump(dados,f,ensure_ascii=False,indent=2);f.write('\n')
        temporario=f.name
    os.replace(temporario,arquivo)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('acao',choices=['inspecionar','aprovar','regra'])
    parser.add_argument('--servidor',required=True,help='ID do servidor/campanha no Discord')
    parser.add_argument('--cadastro',type=Path,default=RAIZ/'src/var/ficha-campanhas.json')
    parser.add_argument('--ficha',type=Path,help='ANALISE.csv ou ficha.xlsx calculada; não será copiada')
    parser.add_argument('--campo',help='custom.melhoria.1, custom.forma.1, efeito.1 etc.')
    parser.add_argument('--por',help='identificação do mestre que autorizou, obrigatória para aprovar')
    parser.add_argument('--nome',help='nome sem prefixo regra.: atributos_pontos, vida_rolada etc.')
    parser.add_argument('--valor',help='valor JSON: 10, 0, ou \"Sim\"')
    args=parser.parse_args()
    if not args.servidor.isdecimal():parser.error('--servidor precisa ser um ID numérico')
    dados=json.loads(args.cadastro.read_text()) if args.cadastro.exists() else {}
    cadastro=dados.setdefault(args.servidor,{})
    if args.acao=='regra':
        if args.nome is None or args.valor is None:parser.error('regra exige --nome e --valor')
        regras=dict(cadastro.get('regras',{}));regras[args.nome]=json.loads(args.valor)
        regras_autorizadas(RegrasDaCampanha(valores=regras))
        cadastro['regras']=regras
        gravar(args.cadastro,dados)
        print('Regra autorizada salva no cadastro do bot. Não altera a ficha ou produção.')
        return 0
    if args.ficha is None:parser.error('inspecionar/aprovar exige --ficha')
    ficha=de_csv(args.ficha.read_text(encoding='utf-8')) if args.ficha.suffix.lower()=='.csv' else de_xlsx(args.ficha)
    formato=valor(ficha,'formato.versao')
    if formato not in (11,12):parser.error('aprovação por esta ferramenta exige B47 formato 11 ou R53 formato 12')
    _,aprovados=carregar_campanha(args.cadastro,args.servidor)
    # Formato 12: Melhorias/Restrições herdam do catálogo R53, então a impressão é a mesma que o bot confere.
    ctx=ContextoB47(aprovados=aprovados,r53=formato==12);r=Resultado('aprovada')
    preparar_custom(ficha,Referencias.do_livro(RAIZ/'dados'),ctx,r)
    conferir_efeitos(ficha,ctx,r)
    candidatos={d.chave:(d.impressao,d.valida) for d in ctx.registros.values()}
    for efeitos in ctx.efeitos.values():
        for e in efeitos:
            campos={'caixa':e.caixa,'como':e.como,'valor':e.valor,'tipo_de_fonte':e.tipo_de_fonte,'fonte':e.fonte}
            k=f'efeito.{e.indice}'
            candidatos[k]=(impressao_exata('efeito',e.fonte,campos),not any(p.campo.startswith(k+'.') or p.campo==k for p in r.problemas))
    if args.acao=='inspecionar':
        for k,(sha,valida) in candidatos.items():
            print(k,sha,'definição válida' if valida else 'INVÁLIDA; corrigir antes da aprovação')
        return 0
    if not args.campo or not args.por:parser.error('aprovar exige --campo e --por; execute inspecionar antes')
    if args.campo not in candidatos:parser.error('definição não encontrada ou efeito inválido/desligado')
    sha,valida=candidatos[args.campo]
    if not valida:parser.error('definição inválida; aprovação não substitui validação mecânica')
    cadastro.setdefault('aprovados',{})[sha]=args.por+' · '+datetime.now(timezone.utc).isoformat()
    gravar(args.cadastro,dados)
    print(f'Aprovação salva para {args.campo}: {sha}. Uma alteração relevante exige nova aprovação.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
