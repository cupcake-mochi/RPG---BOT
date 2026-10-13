# Busca do livro, rodada 8 (bateria cega holdout6)

`proposta/busca_v8.js` = a v7 que está no `modelo.html` + as mudanças abaixo. `proposta/aplicar8.py` faz a troca.

**Medida honesta primeiro:** a `bateria/holdout6.json` (x01 a x50, 38 de regra + 12 de papo, 12
seguimentos) foi escrita por um agente que só leu o livro. Com a página como está agora (v7),
**ela deu 34/38 e papo 4/12**. Nas cegas anteriores: holdout4 23/30 (77%), holdout5 29/38 (76%),
holdout6 34/38 (89%). Ou seja, o ganho das rodadas 6 e 7 generalizou. Depois disso corrigi o que ela
mostrou, então ela deixou de ser cega.

| Bateria | Atual (v7) | v8 |
| ------- | ---------- | -- |
| holdout6 | 34/38, papo 4/12 | 37/38, papo 2/12 |
| todas as outras | | iguais (59, 27, 35, 35/37, 27/30, 38/38, 26, 10/10, conversas 11 a 13) |
| conversas reais: papo com livro / regra com livro | 8/129, 52/52 | iguais |

## O que muda

1. **"e o grau 2?" depois de "salário do grau 4":** se a palavra própria do seguimento já estava na
   pergunta anterior, é o mesmo assunto com outro número; não vira assunto novo, e o termo repetido
   não ganha o bônus de termo citado (que levava pros Graus de equipamento).
2. **Intenção sem "?":** "tem como", "tem desconto" e "quero/vou fazer/criar/montar/comprar/fabricar"
   entram no `PERG`. "quero fazer uma espada minha, tem desconto pra fabricar..." acha Fabricação.
3. **"domínios" no plural** entra no `REGRA`; vence/venceu → vitória. "qnd dois dominios se
   encontram quem vence?" acha Disputa de domínios.
4. **"regra" saiu do `PERG`:** "essa regra da casa do meu mestre é uma cilada kkk" não é pergunta.
5. **Título de duas palavras com palavra comum** ("Na mesa"): palavra do `TITULO_COMUM` não conta
   como conteúdo do título. "bom dia galera, quem vai na mesa hj?" não puxa livro.
6. **Trilha com nome comum** ("Assassino", "Muro", "Punho") só abre a busca em pergunta ou com
   número: "vi um filme de assassino ontem" não abre; "o assassino ganha o que no nivel 3?" e
   "como funciona o muro?" continuam.

## Pra vocês (lorebook/IDIOMA)

- holdout6 x42 "ontem fiz um ritual de acordar cedo e funcionou kkk": a entrada Ritual do lorebook entra.
- holdout6 x48 "o bot disse \"você precisa de CD 20\" mas eu n lembro disso kkk": o termo CD entra
  pelo texto entre aspas (a busca já ignora aspas; o `ativar` não).
- "e a oripatia, dá pra curar?": a busca acha só "cura" (oripatia não está no livro) e traz as páginas
  de Cura. Como é pergunta de mundo, talvez o lorebook com a entrada de oripatia baste e a busca não
  devesse abrir; não mexi.

## Ainda aberto

- holdout6 x10 "como faço p ter uma maldição de verdade como invocação, derrotar e prender?": a
  resposta é Domar (entidades); a pergunta não usa nenhuma palavra da seção.

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada8/rodar.sh /tmp/pagina.html
```
