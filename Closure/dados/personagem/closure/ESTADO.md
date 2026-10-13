# Closure: onde paramos (12/10/2026)

Pra retomar em conversa nova. Tudo abaixo já está salvo nesta pasta.

## Decisões do Mizuki

- Mesma função da Kal'tsit (guia de mundo e regras, fora da história, mesmo lorebook), mas
  brincalhona. Plantão das 21h às 9h. As duas nunca falam uma com a outra; a Closure pode
  provocar a Kal'tsit falando dela.
- Sem kkkk, sem "chefe", iene no lugar de LMD, risada só "haha"/"hehe" e rara. Pode reclamar de sono.
- Terceira pessoa ("a Closure...") fica, rara e só se gabando (no jogo: ~7 de 1.557 falas EN).
- Energia: v0.5 "amei"; pediu "um pouquinho" menos; v0.7 ficou seca no cumprimento; v0.8 = v0.7 com
  cumprimento animado ("Opa, oi!"). "!" fica como está; se mexer, é pra cima.
- "Opa" virou bordão na bateria: a v0.10 cita duas formas ("Opa, oi!", "Ei, oi!").
- Mesmo bot que a Kal'tsit: sem nome na mensagem responde quem está de plantão; chamada pelo nome fora do
  turno, responde curto. Aniversário dela: 10 de dezembro (o da ficha do jogo).

- Pente fino (12/10): conta simples de fora do jogo ela responde; perguntada se é IA ou quem a fez, desconversa
  como gente ("o ideal é ter vida": está em outra estação, respondendo pelo computador); dado ela não rola.

## Etapas (`docs/PLANO-PERSONALIDADE.md`)

| Etapa | Estado | Arquivo |
| ----- | ------ | ------- |
| 0–1 corpus e canon | feita | `canon.md`, `voz.md`, `voz-contagem.md` |
| 2 glossário | feita | `glossario.md` |
| 3 card | **v0.19** (13/10): v0.11 a v0.19 saíram do pente fino (v0.15 a v0.17: naturalidade; v0.18 e v0.19: recusa em primeira pessoa, começando por "não" ou pelo motivo, regra no lembrete) | `card.json`, `card.md`, gerador `ferramentas/gerar_card_closure.py`; testes em `avaliacao/2026-10-12-card.md` e `avaliacao/2026-10-12-pente-fino.md` |
| 4 exemplos | **feita:** 36 trocas (34 de fala real, 2 escritas), 3 no card. Revisada pelo Mizuki (5, 18, 21 e 33 ajustados); falta ele confirmar a comparação nova do 33 | `exemplos.md`, banco em `../../corpus_closure/respostas_sem_lore_en.jsonl` |
| 5 lorebook | usar o da Kal'tsit (`../kaltsit/lorebook.json`) | — |
| 6 vida | **feita, revisada pelo Mizuki em 12/10 à noite:** só as diferenças pra Kal'tsit; 15 situações de estado passaram no Haiku e no Sonnet; chamada pelo nome fora do turno e aniversário em 10 de dezembro | `vida.md` |
| 7 avaliação | em andamento: conversa de 30 turnos e nome trocado feitos na v0.10; falta o Gemini 3.8 Flash (cota do dia acabou) | `avaliacao/2026-10-12-etapa7.md` |
| 7b pente fino | **rodadas 1 a 3 feitas:** bateria nova de 102 inéditas com gabarito (`bateria_c3.json`); v0.11 tirou as muletas ("plantão da madrugada" 14 → 0), v0.12 variou as saídas, v0.13 tratou o "pelo registro" repetido (6 → 4 no Haiku) e a distorção de lore; falta: três rodadas por mensagem, canal com várias pessoas, conversa de 60 turnos e Gemini | `avaliacao/2026-10-12-pente-fino.md` |
| 7c pente fino (13/10) | **canal com várias pessoas** (14 situações, Haiku 13, Sonnet 14) e **conversa de 60 turnos** nas duas; v0.14 só se assume bot quando a pessoa está mal e pergunta a sério. Três rodadas, naturalidade e recusa feitas (v0.19, sistema_closure_v19.txt). Página de teste no ar (`ferramentas/pagina_teste/`). Falta: Gemini e o Mizuki aprovar a v0.19 | `avaliacao/2026-10-12-pente-fino.md`, `conversa_c5.json`, `bateria_c4_canal.json` |
| 8 v1 | depois da 6 e da 7 | — |

## Pra testar de novo

Bateria `../kaltsit/avaliacao/2026-10-12-ciclos/bateria_c1.json` (58), prompt montado
`sistema_closure_v19.txt` e `lembrete_closure_v19.txt` na mesma pasta; entradas em texto na subpasta `entrada/`; respostas `r_c*_*.json`
(v0.8 `r_c8_*`, v0.9 `r_c9_*`, v0.10 `r_c10_*` com `sistema_closure_v10.txt`). Contagem: `python3 nota_closure.py c9 c10`.
O gerador sobrescreve `sistema_closure_v1.txt` toda vez: copie pra `_vN` antes de testar.
