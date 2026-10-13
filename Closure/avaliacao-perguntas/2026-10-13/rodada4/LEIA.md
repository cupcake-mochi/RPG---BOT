# Busca do livro, rodada 4

`proposta/busca_v4.js` substitui o trecho `// ---------- livro:` até `// ---------- estado da conversa`
do `modelo.html` atual (que é a v3 que vocês aplicaram). `proposta/aplicar4.py ENTRADA.html SAIDA.html`
faz a troca numa página montada. Nada fora desse trecho muda.

| Bateria | Atual (v3) | v4 |
| ------- | ---------- | -- |
| bateria (59) | 59 | 59 |
| holdout rodada 2 (27) | 27 | 27 |
| holdout2 (35 + 10 papo) | 35, papo 0 | 35, papo 0 |
| holdout3 (37 + 8 papo) | 28, papo 1 | 35, papo 1 |
| holdout4 (30 + 10 papo, nova) | 23, papo 2 | 27, papo 2 |
| buracos (26) | 26 | 26 |
| frases da rodada 10 (10) | 7 | 10 |
| conversas reais: papo com livro (129) / regra com livro (52) | 9 / 52 | 9 / 52 |

**Sobre a medida honesta:** usei a holdout3 e as frases da rodada 10 pra achar os erros, então
elas deixaram de ser cegas. Escrevi a `holdout4.json` (u01 a u40) com um agente que só leu o
livro, sem ver código nem as outras baterias. Na primeira passada ela deu **23/30 nas duas
versões**: as correções da holdout3 não generalizaram sozinhas. Corrigi 4 dos 7 erros dela
(crit, dois 10 duas vezes, "e se passar do limite?"), então agora ela também deixou de ser cega.
A próxima bateria escrita às cegas é que vai dizer quanto disso vale de verdade.

## O que muda

1. **Gíria e sigla:** stun → Atordoado, clash → Disputa de domínios, crit → crítico,
   zerou/zerado → zero, hp e pv → vida, morrer/morreu → morte, consertar → reparo,
   começo/começar → inicial ("quantos pv eu começo?" acha a Vida inicial dos Caminhos).
2. **Duplo 10 e duplo 1:** "dois 10", "10 e 10" buscam também Aparar; "dois 1", "1 e 1" buscam Brecha.
3. **Seguimento:**
   - um pronome que aponta pra trás ("e se eu tiver desvantagem **nele**?") herda o assunto com peso cheio e nunca vira assunto novo;
   - "assunto novo" agora exige um termo do livro de fora do Caminho anterior ("e o bloquear?"), então "e se passar do limite?" continua em Carga;
   - "e se for 30m?" funciona ("for", "tiver", "nele" saíram da contagem de palavras próprias, e "30m" vira "30 m");
   - a anterior conta como pergunta de regra também quando citou um termo do livro ("qnto eu pulo com força 3?" seguido de "e com força 5?").
4. **Caminho por apelido:** "pro meu tank, o revestimento 3 dá qnto de defesa?" não fica preso às páginas do Bastião quando o termo citado é de fora dele. Com o nome escrito ("habilidade do guia") continua preso como antes.
5. **Nome em negrito abrindo parágrafo** ("**Passagem.** Uma vez por dia...") soma na nota, mas não abre a busca sozinho, porque muitos são palavra comum ("Tudo", "Canto"). Cabeçalho de nível ("**Nível 27.**") fica de fora, porque já tem bônus próprio.
6. **Título de seção inteiro com 2+ palavras** na pergunta vale +8 (era +3): "Reparo do corpo".
7. **Afirmação com número** abre com palavra de regra ("rolei 18 no ataque, acerta a defesa 15");
   "acho que" e "será que" contam como pergunta ("acho que o crítico dobra tudo").

Seguimentos e níveis conferidos de novo: "e o bloquear?", "e de 20?", Bastião 15, Guia 27,
latente e descendente.

## O que sobra

- holdout3: t14 (Corpo Amaldiçoado traz Descansos e a página da Origem, sem "Reparo do corpo");
  t17 (shikigami a zero traz Vida a zero e Derrota, sem "Queda e destruição" das invocações);
  t44 "meu ritual de toda manhã", que puxa Ritual.
- holdout4: u05 "to agarrado e n sei como sair" (Contenções não vem); u22 arma de fogo no começo
  (a regra está em Dinheiro inicial, que fica em 3º); u29 "e como ação bônus?" depois de energia
  reversa (vem Turnos). Falsos positivos: "ritual de limpeza na casa nova" e "o guia de
  restaurantes" (no livro o Caminho é "o Guia", masculino; o IDIOMA de vocês só cobre o feminino).

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada4/rodar.sh /tmp/pagina.html
```
