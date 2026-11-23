# Pente fino da consulta do livro (23/11/2026)

## O problema

No #guias-do-ciclo, a Kal'tsit respondeu “quais o benefícios de ser do tamanho
grande?” com “Não tenho essa parte do livro aqui comigo agora”. O trecho existe
(`origens--corpo-ninhada-gemeos`), mas a busca não abriu o livro.

Duas causas, as duas na busca (`ferramentas/pagina_teste/modelo.html`):

1. **Portão léxico.** A busca só abre o livro quando a mensagem tem um termo do
   índice, um nome de família ou título, ou uma palavra de regra (`REGRA`) junto
   de pergunta. “tamanho grande” não passava em nenhum.
2. **Limite de frequência do índice.** `poeTermo` descarta termos que aparecem
   em mais de 40 páginas. Nomes de regra muito usados, como Destreza,
   Deslocamento, Pesada e Restrição, ficavam de fora justamente por serem
   importantes.

A auditoria antiga (`auditar_consulta_livro.py`) não pegava isso porque pergunta
“No livro, como funciona {título}?”: “livro” e “como funciona” abrem o portão
sozinhos. Por isso ela dava 498/498.

## O que mudou (busca v12)

- **CONCEITO.** É o conjunto de nomes de uma palavra que o próprio livro define:
  título, subtítulo, cabeçalho, abertura em negrito, linha de tabela em negrito
  e link de glossário. Uma pergunta com um desses nomes abre o livro. Palavras
  comuns demais (`CONCEITO_COMUM`: “efeito”, “corpo”, “energia”…) ficam de fora,
  senão conversa comum puxava trecho.
- **Glossário e tabela sem limite de frequência.** Um nome de uma palavra que
  está em CONCEITO não sofre o corte de 40 páginas quando vem do glossário ou
  de linha de tabela em negrito (`limDef`).
- **“tamanho” virou palavra de regra** (`REGRA`).
- **Três erros de ranking:**
  - “Arma Vinculada” caía no Vínculo do Evocador, porque “vinculada” puxava a
    família. Uma palavra dentro de um nome composto definido não puxa mais
    família.
  - “colar de ar” não achava os acessórios. Um título curto sem conteúdo
    próprio entra no índice quando tem 3 palavras ou mais.
  - “ação padrão” caía em Esconder. Um grupo de 3 ou mais definições que só
    repete um rótulo, quando o índice aponta outra página, não compete mais.

## Números

Rodados com `ferramentas/auditar_consulta_pente.py`: 2131 tópicos das 576
páginas, 3 jeitos de perguntar, Kal'tsit e Closure, mais 49 mensagens de
conversa comum. Relatório completo, por capítulo e por página:
[CONSULTA-PENTE-FINO-2026-11-23-relatorio.md](CONSULTA-PENTE-FINO-2026-11-23-relatorio.md).

| | ok | parcial | falha | perguntas sem trecho | conversa com livro |
|---|---|---|---|---|---|
| antes | 1908 | 92 | 131 | 387 | 9 de 49 |
| agora | 1959 | 72 | 100 | 295 | 13 de 49 |

Kal'tsit e Closure tiveram resultado igual em todos os tópicos.

As 4 conversas novas que puxam trecho foram aceitas, porque o trecho só entra
como apoio e a persona continua respondendo a conversa: “duração do filme”,
“destreza pra tocar piano”, “tamanho da sala” e “especialização na faculdade”.

As cerca de 100 falhas que sobram são, na maior parte, subtítulos genéricos
(“limites”, “resolução”, “família: Área”) ou palavras soltas ambíguas. Ninguém
pergunta esses termos sozinhos. A lista por página no relatório serve pra
conferir, não como meta.

## Testes novos

Em `src/testes/test_consulta_natural.py`:

- nome de regra frequente sem palavra de regra (tamanho grande, destreza,
  deslocamento, pesada, restrição, duração de feitiço), nas duas personas;
- nome composto, rótulo e título curto (Arma Vinculada, colar de ar, ação
  padrão);
- 8 mensagens de conversa comum com nome do livro que continuam sem trecho;
- paridade entre o motor do bot e o da página com 2 mensagens novas.

## Como repetir

```
python3 ferramentas/auditar_consulta_pente.py --saida src/var/pente.md
python3 ferramentas/auditar_consulta_pente.py --saida src/var/pente.md --comparar nucleo-antigo.js
```

Precisa do Node: `ferramentas/prompt_do_site/lote.js` carrega o núcleo uma vez
e monta os ~13 mil pedidos em cerca de 1 minuto. No QuickJS levaria horas.

## Conferência no servidor e ajuste de tamanho (PR seguinte)

Com a busca v12 no ar (PR #137, deploy às 19h03), a mesma pergunta do
problema já trouxe a Carcaça Grande, mas a Kal'tsit avisou que “as regras gerais
com os benefícios exatos dessa categoria de tamanho não vieram”. A Carcaça Grande
manda “aplicar as regras gerais de tamanho”, e essas regras estão em **Espaço e
posição** (`geral--espacos`, tabela Tamanho × espaço no mapa). No lugar delas
vinha Lâminas, por causa da “espada grande”.

Ajuste: “tamanho” e “tamanhos” puxam “espaço” depois que a busca já abriu
(`DEPOIS`, como “médico” → medicina). Agora a pergunta traz Espaço e posição e
a Carcaça Grande. O pente fino deu os mesmos números gerais e nenhuma conversa
comum nova com trecho. A única troca foi em “qual o tamanho da sua sala?”, que
já recebia trecho e agora recebe Espaço e posição no lugar da Sala de Trégua.

O `auditar_consulta_pente.py` passou a remontar o núcleo a partir do
`modelo.html` em toda rodada. Antes ele usava o cache de `src/var/site`, que
podia estar velho.
