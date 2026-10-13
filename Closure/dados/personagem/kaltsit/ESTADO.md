# Kal'tsit: onde paramos (13/10/2026, noite)

Pra retomar em conversa nova. Tudo abaixo já está salvo nesta pasta.

## Decisões do Mizuki

- Kal'tsit primeiro, Closure depois. Personalidade **clássica** (Esperanta fica pra depois).
- **Fora da história**: guia do servidor pro mundo e as regras do Ciclo Maldito, sem existir no
  mundo. Nada do arco da Balança Quebrada nem lore de Arknights entra no bot.
- Glossário: reescrever em pt-BR bem escrito, não traduzir; "Sem problema" pra consolo; "técnica"
  minúscula; existem as escolas de Tóquio e Kyoto; o Ozpin dirige só a de Tóquio.
- Exemplos aprovados; lorebook pode usar a aba Mestres; testes seguem nos modelos daqui (o Gemini
  já deu prova suficiente).
- **Guia de plantão** das 9h às 21h (Closure das 21h às 9h). Só aparece quando chamada, sem post
  espontâneo. Aniversário: ela nunca diz a data; o servidor comemora em 23 de janeiro (`vida.md`).

## Etapas (`docs/PLANO-PERSONALIDADE.md`)

| Etapa | Estado | Arquivo |
| ----- | ------ | ------- |
| 0 canon | feita | `canon.md`, `dados/corpus_kaltsit/` |
| 1 voz | feita | `voz.md`, `validacao-voz.md` |
| 2 glossário | **fechada** (Mizuki aprovou as 10 falas) | `glossario.md`, `glossario-teste-claude.md` |
| 3 card | feita (v0.6 depois de 4 ciclos de teste; v0.7 troca um exemplo; v0.8 manda citar regra como "o livro"; v0.9 responde à pessoa) | `card.json`, `card.md`, gerador em `ferramentas/gerar_card_kaltsit.py` |
| 4 exemplos | feita (Mizuki aprovou) | `exemplos.md` (23 trocas, 7 no card) |
| 5 lorebook | feita (entradas da aba Mestres aprovadas; Gemini já testado, seguimos com os modelos daqui) | `lorebook.json`, `lorebook.md`, gerador `ferramentas/gerar_lorebook_kaltsit.py`, acionamento `ferramentas/ativar_lorebook.py` |
| 6 vida | feita (desenho): plantão 9h–21h, Closure 21h–9h; só aparece quando chamada; aniversário comemorado em 23 de janeiro, sem ela confirmar. Código depois da fase 1 | `vida.md` |
| 7 avaliação | feita; o teste cego virou nota dos jogadores no canal de teste (fase 1) | `avaliacao/2026-10-12-etapa7.md`, `avaliacao/teste-cego/` (folha e gabarito), `avaliacao/2026-10-12-gemini.md`; chave em `Closure/.env` |
| 8 v1 | **congelada** | `VERSAO.md` |
| pente fino | **card v0.24** (13/10): v0.24 conta o clima como quem olhou a previsão; v0.14 a v0.23 saíram do pente fino em loop pela página de teste (sem espelhar quem fala, falta do livro dita sem frase pronta), com lorebook v1.9 e busca v8; primeiro teste real no Gemini 3.8 Flash pela Vertex sem erro de regra (`../../../pesquisa/validacao/2026-10-13-16h55-modelo-gemini-3.8-flash.md`); falta o Mizuki aprovar pra virar v1.3; card v0.13: três rodadas, polimento de naturalidade e recusa em primeira pessoa; **v1.2, card v0.11** (13/10): conversa de 60 turnos; v1.1, card v0.10 (12/10, fim da noite): 102 mensagens inéditas; ela ganhou vida fora do mundo, conhece a Closure e parou de responder "sou a guia do servidor" | `avaliacao/2026-10-12-pente-fino.md`, `VERSAO.md` |

## Pra fechar a etapa 4

- O Mizuki revisa os 3 exemplos escritos (1, 18, 21 do `exemplos.md`) e as reescritas mais livres (4, 11, 17).
- Teste do card v0.7: `avaliacao/2026-10-12-ciclos/bateria_v7.json` (38 mensagens, 4 novas de pessoa mal e provocação).

## Contexto da etapa 4 (já usado)

- Ler `avaliacao/2026-10-12-ciclos.md`, seção "O que passa pra frente".
- O Mizuki precisa revisar os 3 exemplos escritos nos ciclos (não vêm de fala real).
- Banco de falas: `dados/corpus_kaltsit/respostas_sem_lore_en.jsonl` (881, filtro v2).
- Bateria pronta pra repetir no Gemini: `avaliacao/2026-10-12-ciclos/bateria_v4.json` e
  `conversa_v3.json`.
