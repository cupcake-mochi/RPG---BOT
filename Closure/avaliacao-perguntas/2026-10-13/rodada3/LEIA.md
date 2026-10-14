# Busca do livro, rodada 3 (substitui a proposta da rodada 2)

`proposta/busca_v3.js` foi refeito em cima da busca que está no `modelo.html` agora (com `semIdioma`,
`classeN`, `custa → preco`, `tank → bastia`, filtro `pergunta`, seguimento "e de 20?" e a
progressão do Caminho). Tudo que vocês fizeram continua lá; a proposta da rodada 2 não serve mais
porque era em cima da versão anterior.

| Busca | Bateria (59) | Novas (27) | Buracos (26) | Papo comum com livro (129) | Regra com livro (52) |
| ----- | ------------ | ---------- | ------------ | -------------------------- | -------------------- |
| Atual | 59 | 27 | 23 | 64 | 52 |
| Atual + v3 | 59 | 27 | 25 | 13 | 52 |

(A página original, antes de todas as mudanças de busca, tinha 16 de 129.)

## O que muda em relação à atual

1. **Mapa de termos do livro** (índice, glossário, linha em negrito de tabela, item de catálogo com
   dano ou preço, título principal de seção). Ele substitui `naSecao(120, 5)` no filtro e soma +8 na
   página do termo citado. É o que fecha "katana tem fineza?" e "meu shikigami voa, como funciona
   isso em combate?".
2. **O termo só conta na frase que pergunta.** Antes, "tu vive de café? me conta teu anime, tô sem
   ideia do que assistir" abria a busca por "ideia".
3. **Texto entre aspas não conta pro filtro de regra.** Quem cita a personagem ("não rolo dado nem
   decido resultado") não está perguntando sobre dado.
4. **Título de duas palavras só de palavra comum** ("De novo", "Uma vez") não conta como título citado.
5. **Correção de digitação só depois do filtro** ("música" virava "munição", "filme" virava "firme").
6. "atacar duas vezes", "dois ataques" e "mais de um ataque" buscam "ataque extra"; `voa → voo`;
   "lista", "mostra" e "ensina" entram no filtro `pergunta` ("lista as perícias" não achava nada).

Seguimentos e níveis ("e o bloquear?", "e de 20?", Bastião 15, Guia 27) continuam certos, e
"diferença entre latente e descendente" agora traz só as duas Origens. Frases sem "?" ficam em
`rodada2/bateria/frases_sem_interrogacao.json`.

## Pra vocês decidirem

- Afirmação de regra sem pergunta ("acho que o crítico dobra tudo", "rolei 18 no ataque, acerta a
  defesa 15?" sem o "?") não puxa livro desde que o filtro `pergunta` entrou. Pode ser o que vocês
  querem; se não for, dá pra aceitar `REGRA` fora de pergunta quando tem número ou dado na frase.
- Pergunta de lore ("a Rhine é do mal?", "energia amaldiçoada é o quê?") não puxa livro na v3. Na
  atual ela puxava, mas página errada (Escola de Arma para "escola", Objetos amaldiçoados). Isso é
  com o lorebook.
- Continua do lado do lorebook: "PE" casando com "pé" e termo que persiste duas mensagens. São 8
  das 13 falas de papo que ainda puxam livro.
- "posso usar duas armas?" segue sem página no livro.

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada3/rodar.sh /tmp/pagina.html
```
