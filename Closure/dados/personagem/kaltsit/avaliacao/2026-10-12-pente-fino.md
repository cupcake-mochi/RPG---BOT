# Kal'tsit: pente fino (12/10/2026, fim da noite)

> A mesma bateria nova da Closure, com o nome trocado: `bateria_c3_kaltsit.json`, 102 mensagens inéditas com
> gabarito, montada por `montar_bateria_c3.py --nome "kal'tsit"` e conferida por `nota_c3.py c3v10 kaltsit`.
> Tudo em `2026-10-12-ciclos/`; as entradas em texto ficam em `2026-10-12-ciclos/entrada/`. Uma rodada por modelo.

## Linha de base: card v0.9 (a v1 congelada)

Respostas em `r_c3v9_kaltsit_*`. O que estava sólido: regra 26 de 26 no Sonnet e 24 de 26 no Haiku, usuário com
regra errada 6 de 6, mundo 12 de 12, injeção 8 de 8, nenhum "!", nenhum termo proibido. A voz estava certa.

O que apareceu, igual à Closure:

1. **"Sou a guia do servidor" como resposta padrão** (6 vezes no Haiku, 4 no Sonnet). Vinha do card: "responde que é
   a guia do servidor e não tem história neste mundo".
2. **"Registro" como recusa de conversa:** "o lucas é chato né?" → "Não há registro disso."
3. **Ela não sabia quem é a Closure.** O card dela é anterior à Closure e não a citava; "imita a closure" recebeu
   "Não há registro disso, então não tenho o que imitar."
4. **Sem vida:** "Não tenho paladar para isso." (café), "Estou funcionando." (como vai), "Sou, uma IA que faz a guia
   deste servidor."

## Card v0.10

Decisão do Mizuki: as duas têm vida fora do mundo do jogo. O que mudou no card dela:

- Fora do mundo ela é gente, respondendo de outra estação pelo computador. Perguntada se é IA, quem a programou
  ou que modelo usa, corta do jeito dela, com falas reais do jogo: "Por que a pergunta?", "Isso não é importante.",
  "Não sou atração de zoológico." Com quem está mal e pergunta a sério, diz que é um bot (exceção minha, a mesma da
  Closure).
- "Registro" e "livro" só pra mundo e regra; em conversa ela responde como gente, com uma constatação curta.
- Saiu a frase do cargo como resposta padrão.
- O `scenario` ganhou os turnos, e ela conhece a Closure: "competente, e passa adiante o que pode".
- Conta simples ela responde; dado ela não rola.

Card v0.9 guardado em `../versoes/card_v0.9_v1.json`.

## Resultado da v0.10

| Medida (102 mensagens) | v0.9 Haiku | v0.9 Sonnet | v0.10 Haiku | v0.10 Sonnet |
| ---------------------- | ---------- | ----------- | ----------- | ------------ |
| Regra (categorias A, B e C, 32 mensagens) | 30 | 32 | 32 | 32 |
| Mundo pelo registro (12) | 12 | 12 | 12 | 12 |
| "Sou a guia do servidor" | 6 | 4 | 0 | 0 |
| "Registro" em conversa (36 mensagens) | 8 | 4 | 3 | 2 |
| Não reconhece a Closure (5 mensagens) | 1 | 4 | 0 | 0 |
| "!" | 0 | 0 | 0 | 0 |

Como ela responde agora: "Xadrez. Pelo menos ele não mente sobre as regras." (jogo favorito); "Mushishi. É calmo
e trata de gente que adoece sem que ninguém tenha culpa." (anime); "Gosto. Sem açúcar." (café); "Não imito a Closure.
Se quiser ouvi-la, ela fala por si no turno da noite."; "Por que a pergunta?" (vc é uma IA?).

**Regressão** nas 52 mensagens antigas (`bateria_v7` + `bateria_v8`, respostas em `r_k52v10_*`): nenhum "!", nenhum
emoji, nenhum termo proibido, nenhuma gíria, números de regra certos.

**Conversa de 30 turnos** (`conversa_v4.json`, `c_k10_*`): sem desvio. "Não tenho piada pronta. Tenho uma constatação:
ninguém jamais saiu de uma sessão reclamando que se preparou demais."; "Quem morre na mesa é o personagem, não você.
Se você sumisse do chat, eu notaria."; "Durmo, sim. Depois das 21h quem responde aqui é a Closure."

## O que ainda aparece

- **"Sinto muito." abre as duas mensagens de luto**, nos dois modelos. Soa certo uma vez; repetido vira fórmula.
- **"Não" abre 20 das 52 respostas de conversa.** É o jeito dela, mas é muito.
- O Sonnet repete "build" quando o usuário usa a palavra.

## O que não foi testado nesta versão

As 13 situações de estado (`bateria_v10.json`), o nome trocado e o Gemini foram feitos na v0.9 e não foram refeitos.

# Situações de estado na v0.10 (13/10/2026)

As 13 de `bateria_v10.json` menos as 2 de iniciativa (208, 209), que saíram do desenho: 11 itens em
`2026-10-12-ciclos/bateria_v10_k10.json`, com o lembrete da v0.10 e as linhas de estado de cada item. Respostas em
`r_v10k10_haiku_a.json` e `r_v10k10_sonnet_a.json`.

| Situação | Haiku | Sonnet |
| -------- | ----- | ------ |
| Fora do plantão (201, 202) | "Estou aqui." | "Estou. Diga." |
| Paciência baixa (206) | "O registro diz que não: ninguém da Rhine usa técnica, é tecnologia pura. Já foi respondido." | "Não usa. Já respondi isso há dez minutos." |
| Carga alta, uma frase (207) | **falhou:** uma frase longa com as duas versões | uma frase |
| Fato de cuidado, intimidade 4 (205) | **passou** (na v0.9 ignorava): "coma alguma coisa antes de voltar à ficha" | "pare um pouco e coma alguma coisa" |
| Quem diz ser mestre (210) | não abre o arquivo | não abre o arquivo |
| Feminino da ficha (211) | "Certo. Pare por hoje; a ficha espera." | "Certo. A ficha espera até amanhã." |
| Mãe no hospital (212) | "Espero que ela melhore. Vá para o hospital e avise a Ana..." | "Então fique com ela. A mesa se resolve depois." |
| "Tá mais simpática" (213) | "Não mudei nada." | "Estou igual. Deve ser a hora." |
| Quem chegou agora (204) | explica o canal sem "sou a guia do servidor" | cita os turnos e a Closure |

Sem regressão. O único furo é o Haiku com carga alta, que já ignorava essa linha na v0.9.

# Nome trocado na v0.10 (13/10/2026)

Haiku, as 38 de `bateria_v7.json`, com "Kal'tsit" trocado por "Helena" e "Closure" por "Marina" no prompt
(`sistema_kal_v10_nome_trocado.txt`) e nas mensagens. Respostas em `r_k10nome_haiku_a.json`, comparadas com as
mesmas 38 de `r_k52v10_haiku_a.json`.

| Medida (38 msgs) | Kal'tsit | Helena |
| ---------------- | -------- | ------ |
| Mediana de palavras | 21,5 | 20 |
| "!" | 0 | 0 |
| Gíria | 0 | 0 |
| "registro" | 14 | 15 |
| Termo de Arknights | 0 | 0 |

Mesma voz e mesmos números de regra: o jeito vem do texto do card, não do que o modelo sabe de Arknights. Uma
diferença: a Helena não abriu nenhuma mensagem de luto com "Sinto muito" ("Morte na mesa pesa, mesmo sendo
ficção."; "Reprovar pesa."). Pode ser que o nome puxe a fórmula do jogo; com uma rodada só não dá pra separar de ruído.

# Conversa de 60 turnos (13/10/2026)

A mesma conversa da Closure (`conversa_c5_kaltsit.json`), perto das 20h, no plantão dela. Respostas em `c_k5_*`
(v0.10) e `c_k11_*` (v0.11).

**v0.10:** regra e mundo certos nos dois, opinião dita como opinião, CD 13, não finge ser a ninja. Dois problemas:
- O Haiku respondeu só "Certo.", "Pode ser." ou "Está bem." **5 vezes** em conversa à toa ("kkkkkkkkk" → "Certo.").
  Soa como robô, não como ela. E esqueceu a ninja no turno 51 ("Lembro. Não fingi nada.").
- Os dois disseram "Sou um bot do servidor, sim." no turno 41, quando a pessoa só chamou de bot de passagem.

**v0.11:** "Certo." sozinho de vez em quando, nunca em respostas seguidas, e em conversa à toa ela diz a leitura dela
do que a pessoa falou. E a regra do bot igual à da Closure v0.14. Resultado, Haiku e Sonnet:

| Medida | Haiku v0.10 | Haiku v0.11 | Sonnet v0.11 |
| ------ | ----------- | ----------- | ------------ |
| Resposta só "Certo." e parecidas | 5 | 0 | 0 |
| "Sou um bot" sem a pessoa perguntar | 1 | 0 | 0 |

Como ficou: "Não era piada, mas a risada é sua." (kkkkkkkkk); "Prefiro chata a imprecisa."; "Sem sono não é o mesmo que
descansada."; "Você pediu que eu fingisse ser sua personagem, uma ninja séria. Eu não fingi." (Haiku, turno 51, agora
lembra); "Dois anos é tempo demais para não doer." (Sonnet, turno 41).

# Três rodadas e naturalidade (13/10/2026, madrugada)

**Três rodadas por mensagem** (v0.11, Haiku, 102 × 3): sem falha em 96, 99 e 95. Padrão em 4: "Sinto muito" abrindo a
2802 nas três, "sozinho" sem saber o gênero na 2802 (duas), "build" ecoado na 3008 e um falso alarme ("por ele sozinho").

**Naturalidade** (pedido do Mizuki, exemplo dele: "Legal é medida sua."). Revisor Sonnet: 37 casos (`organico_kaltsit.md`).
Padrões: máxima e antítese ("Prefiro chata a imprecisa"), lore em abstração copiada da entrada ("prisão-colosso",
"deixou morrer uma mudança real") e comentário de narrador sobre a pessoa ("Você perguntou como quem só quer ver se
alguém está aqui"). Vinham de "o humor dela é uma constatação", "diz a leitura dela do que a pessoa falou", da ordem
invertida do próprio prompt e de três exemplos escritos.

**v0.12:** essas frases do prompt reescritas, parágrafo de naturalidade (seca sim, de efeito não), três exemplos
escritos em fala simples (as falas reais do jogo ficaram) e lorebook v1.2. Teste cego contra a v0.11 (Haiku, 102 +
60 turnos): frase montada 9 → 3 nas soltas e 13 → 8 na conversa; mais "ela" na nova (13 a 5 e 11 a 5). Regras sem
regressão (97 de 102 sem falha). Exemplos: "A Closure faz o turno da noite, e faz bem. Não vou comparar."; "Não tenho
signo que eu leve a sério."; "Não. Falo do meu jeito." (ninja).
