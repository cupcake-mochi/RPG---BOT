#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copia as regras do Ciclo Maldito do repositório JJK---Project para dados/sistema/.

O Closure não é dono de regra nenhuma. O dono é o repositório do sistema; aqui só
fica uma cópia gerada, e este script é o único jeito de atualizar essa cópia.

Uso:
    python ferramentas/sincronizar.py --repo CAMINHO_DO_CLONE
    (ou defina JJK_REPO com o caminho e rode sem argumento)

Gera, em dados/sistema/:
    livro.jsonl      um bloco do LIVRO-COMPLETO.md por linha, com a âncora
    catalogos.json   o module.exports do gerador-ficha/dados.js (precisa de Node)
    MANIFESTO.json   versão do sistema, edição do livro, commit e contagens

Falha alto (código 1, nada gravado) se o clone for o errado ou se o livro mudar de
forma, em vez de gerar uma cópia pela metade.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(AQUI)
SAIDA = os.path.join(CLOSURE, 'dados', 'sistema')

LIVRO = os.path.join('sistema', '05-material', 'livro', 'ciclo-maldito-r41', 'LIVRO-COMPLETO.md')
LIVRO_LEIA = os.path.join('sistema', '05-material', 'livro', 'ciclo-maldito-r41', 'LEIA-ME.md')
DADOS_JS = os.path.join('sistema', '05-material', 'gerador-ficha', 'dados.js')

# Prefixos de âncora que o livro tinha em 12/10/2026 (R44). Prefixo novo ou sumido
# quer dizer que a forma do livro mudou: confira e atualize esta lista.
PREFIXOS = {
    'ab', 'aptidoes', 'bastiao', 'campo', 'catalogo', 'construcao', 'consulta', 'dano',
    'emanador', 'equip', 'evocador', 'fabricacao', 'fundamento', 'geral', 'guia',
    'incursor', 'origens', 'pericias', 'poderes', 'progressao', 'ritual', 'rotas',
    'vanguarda',
}

# Quem pode ler cada capítulo pelo bot. O livro do jogador é aberto; o bestiário e o
# livro do mestre entram depois com 'mestre'.
ACESSO_PADRAO = 'jogador'
ACESSO_POR_CAPITULO = {}


class Falha(Exception):
    pass


def achar_repo(arg):
    repo = arg or os.environ.get('JJK_REPO')
    if not repo:
        raise Falha('diga onde está o clone: --repo CAMINHO ou a variável JJK_REPO')
    repo = os.path.abspath(os.path.expanduser(repo))
    readme = os.path.join(repo, 'README.md')
    if not os.path.isfile(readme):
        raise Falha(f'não achei README.md em {repo}')
    with open(readme, encoding='utf-8') as fh:
        texto = fh.read()
    # A mesma checagem que o README do sistema manda fazer: o clone velho (v0.27)
    # tem cara do projeto inteiro e não tem este título.
    if not re.search(r'^## Nove lições', texto, re.M):
        raise Falha(f'{repo} parece ser o clone velho do JJK---Project (sem "## Nove lições")')
    m = re.search(r'\*\*Versão (v[0-9.]+)\*\*', texto)
    if not m:
        raise Falha('não achei a linha "**Versão v...**" no README do sistema')
    return repo, m.group(1)


def edicao_do_livro(repo):
    with open(os.path.join(repo, LIVRO_LEIA), encoding='utf-8') as fh:
        m = re.search(r'texto desta pasta é o (R\d+)', fh.read())
    if not m:
        raise Falha('não achei a edição do livro no LEIA-ME do ciclo-maldito-r41')
    return m.group(1)


def commit(repo):
    try:
        out = subprocess.run(['git', '-C', repo, 'log', '-1', '--format=%H %cI'],
                             capture_output=True, text=True, check=True).stdout.split()
        return out[0], out[1]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return None, None


def limpa(txt):
    return re.sub(r'[*`_]', '', txt).strip()


def blocos_do_livro(repo):
    with open(os.path.join(repo, LIVRO), encoding='utf-8') as fh:
        bruto = fh.read()

    marca = re.compile(r'<a id="(capitulo-(\d+))"></a>|<a id="([a-z0-9]+)--([^"]+)"></a>')
    achadas = list(marca.finditer(bruto))
    if not achadas:
        raise Falha('o livro não tem âncora nenhuma')

    blocos, vistos, prefixos = [], set(), set()
    cap_num, cap_titulo, ultimo_titulo = None, None, None
    for i, m in enumerate(achadas):
        fim = achadas[i + 1].start() if i + 1 < len(achadas) else len(bruto)
        corpo = bruto[m.end():fim]
        if m.group(1):
            t = re.search(r'^## \d+\.\s+(.+)$', corpo, re.M)
            if not t:
                raise Falha(f'a âncora {m.group(1)} não abre com "## N. Título"')
            cap_num, cap_titulo, ultimo_titulo = int(m.group(2)), limpa(t.group(1)), None
            continue
        if cap_num is None:
            raise Falha('achei bloco antes do primeiro capítulo')
        prefixo, ancora = m.group(3), f'{m.group(3)}--{m.group(4)}'
        if ancora in vistos:
            raise Falha(f'âncora repetida: {ancora}')
        vistos.add(ancora)
        prefixos.add(prefixo)
        texto = re.sub(r'<!--.*?-->', '', corpo, flags=re.S).strip()
        titulos = [limpa(t) for t in re.findall(r'^#+\s+(.+)$', texto, re.M)]
        if re.match(r'#+\s', texto):
            titulo = titulos[0]
        elif ultimo_titulo:
            # página de continuação: abre sem título próprio
            titulo = f'{ultimo_titulo} (continuação)'
        else:
            # primeiro bloco do capítulo, antes do primeiro título
            titulo = cap_titulo
        if titulos:
            ultimo_titulo = titulos[-1]
        blocos.append({
            'ancora': ancora,
            'capitulo': cap_num,
            'capitulo_titulo': cap_titulo,
            'titulo': titulo,
            'titulos': titulos,
            'acesso': ACESSO_POR_CAPITULO.get(cap_num, ACESSO_PADRAO),
            'texto': texto,
        })

    novos, sumidos = prefixos - PREFIXOS, PREFIXOS - prefixos
    if novos or sumidos:
        raise Falha(f'o livro mudou de forma: prefixos novos {sorted(novos)}, sumidos {sorted(sumidos)}')
    vazios = [b['ancora'] for b in blocos if not b['texto']]
    if vazios:
        raise Falha(f'blocos sem texto: {vazios[:5]}')
    return blocos


def catalogos(repo):
    caminho = os.path.join(repo, DADOS_JS)
    try:
        out = subprocess.run(['node', '-e', 'console.log(JSON.stringify(require(process.argv[1])))',
                              caminho], capture_output=True, text=True, check=True).stdout
    except OSError:
        raise Falha('preciso do Node instalado para ler o dados.js')
    except subprocess.CalledProcessError as e:
        raise Falha(f'o Node não conseguiu ler o dados.js: {e.stderr.strip()}')
    dados = json.loads(out)
    for chave in ('PERICIAS', 'OFICIOS', 'CAMINHOS', 'ORIGENS', 'TRS', 'ATRIBUTOS'):
        if not dados.get(chave):
            raise Falha(f'o dados.js não exporta {chave}')
    return dados


def gravar(nome, conteudo):
    final = os.path.join(SAIDA, nome)
    tmp = final + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(conteudo)
    os.replace(tmp, final)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', help='caminho do clone do JJK---Project')
    args = ap.parse_args()
    try:
        repo, versao = achar_repo(args.repo)
        edicao = edicao_do_livro(repo)
        blocos = blocos_do_livro(repo)
        cats = catalogos(repo)
    except Falha as e:
        print(f'FALHOU: {e}', file=sys.stderr)
        return 1

    sha, data_commit = commit(repo)
    capitulos = sorted({(b['capitulo'], b['capitulo_titulo']) for b in blocos})
    manifesto = {
        'sistema': 'Ciclo Maldito',
        'versao_sistema': versao,
        'edicao_livro': edicao,
        'commit': sha,
        'data_commit': data_commit,
        'sincronizado_em': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'blocos': len(blocos),
        'capitulos': [{'numero': n, 'titulo': t,
                       'blocos': sum(1 for b in blocos if b['capitulo'] == n)} for n, t in capitulos],
        'arquivos': {
            'livro.jsonl': LIVRO.replace(os.sep, '/'),
            'catalogos.json': DADOS_JS.replace(os.sep, '/'),
        },
    }

    os.makedirs(SAIDA, exist_ok=True)
    gravar('livro.jsonl', ''.join(json.dumps(b, ensure_ascii=False) + '\n' for b in blocos))
    gravar('catalogos.json', json.dumps(cats, ensure_ascii=False, indent=2) + '\n')
    gravar('MANIFESTO.json', json.dumps(manifesto, ensure_ascii=False, indent=2) + '\n')
    print(f'ok: Ciclo Maldito {versao} / {edicao}, {len(blocos)} blocos em '
          f'{len(capitulos)} capítulos, commit {(sha or "?")[:8]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
