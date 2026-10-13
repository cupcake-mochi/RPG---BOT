# Busca do livro, rodada 5 (casos da conversa 11)

`proposta/busca_v5.js` é a v4 que está no `modelo.html` com 5 mudanças pequenas. Ela substitui o mesmo
trecho do livro; `proposta/aplicar5.py ENTRADA.html SAIDA.html` faz a troca.

| Bateria | Atual (v4) | v5 |
| ------- | ---------- | -- |
| bateria / holdout / holdout2 / buracos / rodada 10 | 59 / 27 / 35 / 26 / 10 | iguais |
| holdout3 / holdout4 | 35/37 / 27/30, papo 0 | iguais |
| casos da conversa 11 (`rodada2/bateria/conversa_rodada11.json`): regra / papo com livro | 1/2, 5/5 | **2/2, 0/5** |
| conversas reais: papo com livro / regra com livro | 9/129, 52/52 | 8/129, 52/52 |

## O que muda

1. **Tabela por Classe.** Página com tabela que começa em `| Classe |` ganha +6 quando a pergunta
   cita "classe N", e +3 por palavra da pergunta no cabeçalho ("PE", "pontos"). "quantos PE custa
   um feitiço de classe 1?" passa a trazer **Pontos e preços** em primeiro (3 PE).
2. **Aspas fora do termo citado.** Já não contavam pro filtro de regra; agora também não contam como
   termo do livro. "\"quase dormindo em pé, mas ainda aguento\" kkk como assim?" não puxa Vida a zero.
3. **"ganhou", "ganha" saíram do `REGRA`.** "você ganhou alguma coisa com o bug?" e "consigo ganhar
   de um cara que joga desde criança" abriam a busca. "o que eu ganho no nível 5?" e "o que o guia
   ganha no 27?" continuam certos (nível e Caminho já abrem).
4. **"o que é" saiu do `REGRA`.** Pergunta de mundo ("o que é energia amaldiçoada?") fica com o
   lorebook. "o que é integridade/legado/maestria/xp/expansão de domínio?" continuam achando a
   página, porque são termos do livro.
5. **A mensagem anterior só passa assunto se perguntava ou tinha número.** "sofá no escritório, que
   vida" deixou de passar "vida" pra "e vc toca alguma coisa?". "quando" entrou no `PERG`, pra
   "quando eu tomo dano primeiro cai a vida ou a integridade" seguir valendo de anterior.

6. **Palavra comum que é termo de uma palavra só** ("mesa", "ideia", "ver", "peso", "altura",
   "campanha"...) entrou na lista `TITULO_COMUM`: não abre a busca sozinha. "tu cochila até no meio
   de mesa? conta uma dessas" parou de puxar Seu primeiro feitiço. Pergunta de regra com essas
   palavras ("qual o peso da katana?") continua achando pelo filtro de regra.

O caso 2 ("e se eu for o último a agir, eu perco o turno?" depois de iniciativa) já estava resolvido
na v4.

## Ainda aberto

- "o que é PE?" traz uma página de Talismã antes da âncora do lorebook (igual na v3 e na v4). PE
  aparece em quase todo o livro; se for pergunta comum, vale a entrada do lorebook ter a página certa.
- Os mesmos da rodada 4: t14, t17, u05, u22, u29 e os falsos positivos de "ritual" e "o guia de
  restaurantes".

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada5/rodar.sh /tmp/pagina.html
```
