# Busca do livro, rodada 6 (conversas 12 e 13 + bateria cega holdout5)

`proposta/busca_v6.js` é a v5 que está no `modelo.html` (com o TITULO_COMUM maior), com as mudanças
abaixo. Ela substitui o mesmo trecho do livro; `proposta/aplicar6.py ENTRADA.html SAIDA.html` faz a troca.

| Bateria | Atual (v5) | v6 |
| ------- | ---------- | -- |
| bateria / holdout / holdout2 / holdout3 / holdout4 | 59 / 27 / 35 / 35 de 37 / 27 de 30 | iguais |
| **holdout5 (nova, cega: 38 de regra + 12 de papo)** | **29/38, papo 3/12** | 31/38, papo 3/12 |
| conversa 12 (9 de regra + 1 de papo) | 1/9, papo 1/1 | 8/9, papo 0/1 |
| conversa 13 (1 + 1) | 0/1, papo 1/1 | 1/1, papo 0/1 |
| buracos / rodada 10 / conversa 11 | 26 / 10 / 2 | iguais |
| conversas reais: papo com livro / regra com livro | 8/129, 52/52 | iguais |

**Medida honesta:** a `bateria/holdout5.json` (w01 a w50) foi escrita por um agente que só leu o
livro. **Antes de qualquer mudança desta rodada, v5 e v6 deram 29/38 e papo 3/12**, ou seja, o que eu
corrigi das conversas 12 e 13 não muda nada numa bateria nova. Depois corrigi 2 dos 9 erros dela
(w03 "da pra curar os amigos?" e w11 "qnto eu consigo pular com força 3?"); a partir daqui ela também
deixou de ser cega.

## O que muda

1. **Interjeição antes do seguimento:** "pera, ...", "hm, e ataque?", "Ué, e a Abertura...",
   "ah ta, e...": o seguimento continua valendo. "pera" sozinho também marca seguimento.
2. **Frase que pergunta uma coisa só** ("hm, e ataque?") dá +12 na seção com esse título, mesmo com
   palavra que o livro usa em toda parte. Antes vinha "Limites de dano".
3. **Digitação em palavra longa:** "decanso" acha Descansos (a raiz de 6 letras escondia a letra que faltou).
4. **"quanto" saiu do `REGRA`** (já está no `PERG`): "faz quanto tempo que vc tá no plantão?" não
   abre mais a busca. Pergunta de regra com "quanto" continua achando pelo termo ou pela palavra de regra.
5. **`arma\w*` virou `arma|armas|armad\w*`:** "o manual do armário tinha 40 páginas" puxava o livro.
6. **Material de mesa e "quero ser":** "(quero|quiser|posso|da pra) ser", "caneta" e "lápis" entram no
   `REGRA`. "médico" vira Medicina só depois que a busca abriu ("tu é médica?" continua sendo papo
   com a personagem).
7. **Tabela por Classe:** "custa"/"preço" casa com a coluna "Pontos / PE" e a classe tem que ser da
   própria pergunta (a herdada não conta). "quanto custa um feitiço de Classe 1 no Rápido?" traz Pontos e preços.
8. **Pronome:** "dele" e "dela" saíram da lista que herda com peso cheio ("a Medicina do cara...
   dele" fala de outra pessoa). Continua com "nele", "nela", "nisso", "disso", "com ele".
9. Sinônimos: pular/pulo → salto, curar/curo → cura, caneta → lápis.

## Ainda aberto

- conversa 12, d8 "a besta de uma mão ataca com a mesma perícia que a besta grande?": vem Munição e
  Armas de disparo; a regra do atributo do ataque (Ataques) não vem.
- holdout5:
  - pedido de Caminho pela fantasia: "quero ser tipo um ninja" (Incursor) e "personagem q invoca
    bichos" (Evocador). Isso combina mais com uma intenção no lorebook do que com a busca;
  - seguimentos curtos: "e quanto custa?" depois do escudo médio, "e sem correr antes?" depois de
    salto, "e a derrubado?" depois de Lento, "e no nível 9?" depois de XP. Tentei dar peso cheio ao
    assunto herdado quando a pergunta só tem número ou uma palavra, mas isso quebrou "e no nivel 23?"
    (holdout2), "e se for 30m?" e "e pra entidade?" (holdout3), então tirei.
- Papo que puxa livro na holdout5 (do lado do lorebook/IDIOMA): "minha classe de faculdade... nível
  de cansaço máximo", "vc q fez o ritual de iniciação do bot?", "obg guia, vc salvou nossa campanha".

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada6/rodar.sh /tmp/pagina.html
```
