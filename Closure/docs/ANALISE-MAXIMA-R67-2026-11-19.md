# Análise da Técnica Máxima na R67

Fecha a pendência aberta em [Consulta R68](CONSULTA-R68-2026-11-19.md). As
duas fichas oficiais (Era e Ciclo) receberam a rodada da Técnica Máxima R67 em
19/11/2026, e a ANALISE foi exportada às 11:23 (formato 13, `em_dia`). Agora o
bot confere a Máxima pela mesma conta da planilha.

## O que mudou

- **Modelo R53 copiado de novo** de `cupcake-mochi/Ficha---RPG-JJK@76bc66788fb6f75faa3b778f03939017d9d65420`
  (PR 136 da ficha, ramo `claude/rodada-r67-0b8c4f`). É o mesmo código que foi
  instalado nas oficiais. A cópia anterior era do `4b22da5`, da PR 4.
  - `formulas.py` e `catalogo.json` são idênticos aos da ficha. O sha256 fica
    fixado em `testes/test_r53.py`.
  - `modelo.py` tem os mesmos três ajustes de antes: imports relativos e o
    catálogo lido ao lado do arquivo.
  - `formas_custom.py` e `contextos.json` não mudaram. A R67 não alterou a
    modalidade nem as classes dos 249 cartões. O que mudou nas montagens foi só
    o aviso de nível das Liberações, que fica dentro da planilha.
- **Casos de referência** (`testes/dados/r53-casos.json`) copiados do
  `r53/testes/casos.json` da ficha no mesmo commit: são 96 casos, eram 89.
  - A cura da Máxima de domada caiu para 14/16/19d8 nos níveis 17/21/26, igual
    ao exemplo do livro. Antes era 19/22/26d8.
  - Entraram 7 casos da R67, todos no nível 17:
    - Explosão tirando a Forma dos dados: 19d8.
    - Cura em Aura: 16d8.
    - PV temporários, individual (63) e em Aura (48, exemplo do livro).
    - Sem dano com reforço de Controle (+2 na CD).
    - Sem função marcada: cartão inválido.
    - Domada com Explosão: 14d8, exemplo do livro.

Com isso, o cartão `maxima.1` e as Máximas de entidade seguem a regra da R67:
- a Forma e a base da função saem dos dados;
- os pontos de 8/12/16 pagam só as Melhorias;
- a vida temporária é aceita;
- a Máxima sem dano vira Efeito Próprio principal de até Pesada, com o reforço
  de Controle.

## O que ficou como estava

- **`ficha_magia.conferir_maxima`** só roda em ficha que não é R53, ou seja, no
  formato 11 (B47). Essa planilha antiga ainda calcula a Máxima pela tabela
  cheia. Se o corretor passasse para a R67, toda Máxima dela viraria erro sem
  que o jogador tivesse o que corrigir. As oficiais estão no formato 13 e não
  passam por ele.
- **O livro e a consulta** continuam na R68/v0.379, como já estavam.

## Testes

- `test_r53` com os 96 casos, `test_b47_maxima` e `test_ficha_efeitos` passaram.
- Bateria completa no Windows, rodada também na main `a2a8cc3` para comparar: 780 testes nas duas, com os mesmos
  153 erros de ambiente (`tzdata`, `discord`, `aiohttp`, `os.killpg`, `fcntl`, `quickjs` faltando no Windows) e nenhuma
  falha. O ramo não acrescentou erro nenhum. A bateria de verdade é a do CI no Linux.
- Pacote (`ferramentas/empacotar.py`): 93 arquivos, sem `.env`, com os três arquivos do modelo iguais aos do ramo.

## Não rodou

- O CI no Linux ainda não rodou: o ramo só existe no PC.
- Nenhuma publicação na Discloud. Também não analisei as oficiais no Discord
  com o código novo.
- Nenhuma pergunta à Kal'tsit ou à Closure, porque essas chamam o modelo pago.
