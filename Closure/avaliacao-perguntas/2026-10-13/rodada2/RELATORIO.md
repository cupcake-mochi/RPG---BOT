# Buracos da busca do livro, rodada 2 (13/10/2026)

Base: a página como está agora (Closure v0.26 / Kal'tsit v0.21, com os ajustes de busca que a
thread da personalidade já fez: raiz própria de "iniciativa", `LINHA`, `TPRIN`, `EXEMPLO`, verbos
em `SINONIMO` e `REGRA`). A proposta é **um delta em cima dessa busca**, não a v2 antiga.

## Resultado

| Busca | Bateria (59) | Perguntas novas (27) | Buracos (26) | Papo comum que puxa livro (129) | Pergunta de regra com livro (52) |
| ----- | ------------ | -------------------- | ------------ | ------------------------------- | -------------------------------- |
| Página original (v0.23, antes da v2) | 38 | 20 | 11 | 16 | 45 |
| Página atual | 59 | 27 | 23 | **67** | 52 |
| Atual + busca v3 | 59 | 27 | 25 | **22** | 52 |

"Papo comum" são 129 falas reais das conversas da rodada 9 (`dados/personagem/kaltsit/avaliacao/2026-10-13-conversa/rodada9`)
que não têm nada de regra ("tu ouve música?", "tá de pé amanhã?"), rotuladas à mão em
`bateria/conversas.json` junto com 52 falas que são pergunta de regra e 19 ambíguas.

**Erro meu da rodada 1:** a busca v2 fez o livro entrar em conversa comum muito mais vezes
(16 → 67 de 129). Os culpados foram a correção de digitação antes do filtro ("música" virava
"munição", "gosto" virava "gasto", "filme" virava "firme") e o filtro de "palavra rara de título"
pegando palavra de papo. A bateria da rodada 1 só tinha 8 frases de papo, por isso não apareceu.
Com livro no contexto em papo comum, a personagem tende a puxar regra do nada.

## O que muda (`proposta/busca_v3.js`)

1. **Correção de digitação só depois do filtro.** Antes do filtro a pergunta usa só palavra que já
   existe no livro; a correção entra quando a mensagem já tem cara de regra.
2. **Mapa de termos do próprio livro.** O índice e o glossário ligam cada termo à página que o
   define (`[Agarrar](#geral--manobras)`, 465 links). Junto entram a linha em negrito de tabela
   (`| **Esquivar** |`), nome de item de catálogo com dano ou preço (`| Katana (espada curva) |`) e
   o título principal de cada seção, inteiro e em partes ("Agarrar, derrubar e empurrar" também vale
   "derrubar"). Termo citado na pergunta dá +8 na página dele (+4 por palavra a mais).
3. **Filtro "palavra rara de título" virou "pergunta com termo do livro".** Só abre a busca se a
   mensagem tem cara de pergunta (`?`, "como", "posso", "qual"...) e cita um termo do mapa. Título
   de uma palavra que é papo comum ("tempo", "começo", "novo", "caminho") fica fora do mapa.
4. **"atacar duas vezes", "dois ataques", "mais de um ataque"** passam a buscar também "ataque extra".
5. `voa` → `voo` em `SINONIMO`.

Seguimentos que vocês acabaram de corrigir continuam iguais ("e o bloquear?", "e de 20?", Bastião
nível 15, Guia nível 27); "diferença entre latente e descendente" agora traz só as duas páginas,
sem a página geral de Origens (`bateria/seguimentos.json`).

## Respostas (Haiku, um caso por vez, conferidas no livro)

- "qual o dano da katana?" → 1d8 Cortante, Versátil e Fineza.
- "como funciona iniciativa" → d20 + Destreza, empate por Destreza, depois jogador antes do inimigo.
- "esquiva funciona como" → Ação Padrão, desvantagem nos ataques contra você e vantagem em TR Físico até seu próximo turno.
- "como eu agarro alguém?" → troca um ataque da Ação Atacar, TR Físico CD 8 + Força + maestria.
- "posso derrubar um inimigo?" → mesma manobra, alvo fica Derrubado.
- "posso atacar duas vezes no turno?" → Ataque Extra no nível 7 (deixou de dizer que é do Bastião e da Vanguarda).
- "posso voar?" → só com capacidade que conceda voo; salto não conta.

Arquivo: `respostas/v3_haiku_buracos.json`. Mesmo limite de antes: Haiku como substituto do Gemini.

## O que fica aberto

- **"posso usar duas armas?"** não acha. O livro não tem seção de "duas armas"; o mais perto são
  as propriedades Leve e a Ação Atacar. Vale uma entrada no lorebook se for pergunta comum.
- **Lorebook (de vocês), 8 das 22 falas de papo que ainda puxam livro:**
  - a chave "PE" casa com "pé" ("tá de pé", "pé de café"), porque a comparação tira acento e caixa.
    Sugestão: chave curta em maiúscula só casa em maiúscula, ou casar "PE" com acento preservado;
  - termo do lorebook acionado duas mensagens atrás continua valendo ("Estabilizar" numa fala sobre
    dormir), porque `ativar` olha as duas últimas mensagens.
- 8 falas entram por palavra do filtro `REGRA` dita em papo ("arma", "mestre", "dado", "descanso").
  Já era assim na página original; não mexi.
- O "não achei no livro agora" repetido é do prompt; com a busca achando mais, ele aparece menos,
  mas o texto em si é de vocês.

## Reproduzir

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada2/bateria/rodar.sh /tmp/pagina.html
```

`proposta/aplicar3.py ENTRADA.html SAIDA.html` troca o bloco `// ---------- livro:` até
`// ---------- estado da conversa` pela v3 (no `modelo.html` é o mesmo trecho).
`bateria/causa.js PAGINA.html bateria/conversas.json` diz por que cada fala de papo puxou livro;
`bateria/termos.js PAGINA.html "pergunta"` mostra quais termos do mapa a pergunta cita.
