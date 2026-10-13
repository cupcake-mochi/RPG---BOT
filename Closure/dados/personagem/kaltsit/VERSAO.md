# Kal'tsit: versão vigente

> Etapa 8 do `docs/PLANO-PERSONALIDADE.md`. Qualquer mudança de card, exemplo, lorebook, modelo ou
> parâmetro roda a avaliação de novo (`avaliacao/`) e muda uma variável por vez.

## v1.2 (13/10/2026): card v0.11, depois da conversa de 60 turnos

| Peça | Arquivo | Versão | sha256 (12 primeiros) |
| ---- | ------- | ------ | --------------------- |
| Card | `card.json` | card v0.11 | `ac544acb7537` |

O resto é igual à v1.1. Duas mudanças no card: "Certo." sozinho não em respostas seguidas (o Haiku respondeu só
"Certo." 5 vezes em 60 turnos; na v0.11, 0), e ela só diz que é bot quando a pessoa está mal e pergunta a sério,
não quando chama de bot de passagem. Detalhe em `avaliacao/2026-10-12-pente-fino.md`. Card da v1.1 em
`versoes/card_v0.10_v1.1.json`.

## v1.1 (12/10/2026, fim da noite): card v0.10, depois do pente fino

| Peça | Arquivo | Versão | sha256 (12 primeiros) |
| ---- | ------- | ------ | --------------------- |
| Card | `card.json` | card v0.10 | `b8a87d57a7fb` |
| Lorebook | `lorebook.json` | 32 de mundo + 53 de sistema; chaves do "Origíneo" e redação da "Escola Jujutsu" revistas | `428afb037a61` |
| Exemplos | `exemplos.md` | 23 trocas, 7 no card (sem mudança) | `09b7dfbc4e96` |
| Vida | `vida.md` | aniversário revisto | `1fed9932b447` |
| Glossário | `glossario.md` | fechado (sem mudança) | `1358be692b70` |

O que mudou no card e por quê: `avaliacao/2026-10-12-pente-fino.md`. Testado em 102 mensagens inéditas, nas 52
antigas e na conversa de 30 turnos, com Haiku e Sonnet. Situações de estado (11, sem as 2 de iniciativa) e nome
trocado refeitos na v0.10 em 13/10, sem regressão. **Não refeito:** o Gemini. O card da v1 está em `versoes/card_v0.9_v1.json`.

## v1 (12/10/2026)

| Peça | Arquivo | Versão | sha256 (12 primeiros) |
| ---- | ------- | ------ | --------------------- |
| Card | `card.json` | card v0.9 | `0afc9b230527` |
| Lorebook | `lorebook.json` | 32 de mundo + 53 de sistema; chaves da entrada "Origíneo" ampliadas em 12/10 à noite | `58dc265ad11d` |
| Exemplos | `exemplos.md` | 23 trocas, 7 no card | `09b7dfbc4e96` |
| Vida | `vida.md` | desenho (código depois da fase 1); aniversário revisto em 12/10 à noite | `1fed9932b447` |
| Glossário | `glossario.md` | fechado | `1358be692b70` |

Geradores: `ferramentas/gerar_card_kaltsit.py`, `ferramentas/gerar_lorebook_kaltsit.py`;
acionamento do lorebook: `ferramentas/ativar_lorebook.py`; bateria no Gemini:
`ferramentas/gemini_bateria.py`.

Modelo: Gemini 3.8 Flash (principal) e 3.1 Flash-Lite (reserva), segundo a `docs/DECISOES.md`.
O Flash-Lite acerta lore e regra, mas a voz dele é mais fria e burocrática
(`avaliacao/2026-10-12-gemini.md`).

### O que a v1 passou

- Baterias de 38 + 14 mensagens (Haiku, Sonnet, Gemini 3.8 Flash, 3.1 Flash-Lite): sem "!",
  emoji ou termo proibido; números de regra certos; isca de Arknights sem eco.
- Conversa de 30 turnos sem desvio; card com nome trocado com a mesma voz.
- 13 situações de estado (plantão, carga, paciência, intimidade) com o bloco 4 da `vida.md`.

### O que fica aberto

- Nota dos jogadores no canal de teste (substitui o teste cego, `avaliacao/2026-10-12-etapa7.md`).
- Uma frase do exemplo do clã Mirai foi copiada 2 vezes em 30 turnos; trocar pela reserva se
  repetir nos logs.
- O bot ainda cita livro, ficha e mestre mais do que as falas do jogo citariam. Isso só incomoda
  se os jogadores reclamarem.

### Revisão da v1 em 12/10/2026 à noite

Só o `vida.md` mudou (era `50026731a832`): o aniversário deixou de ser a estreia do bot. O servidor comemora em
23 de janeiro e ela nunca confirma a data. Card, lorebook, exemplos e glossário são os mesmos, com os mesmos
hashes. A linha nova do bloco 4 foi testada com o card v0.9 em 3 redações, Haiku e Sonnet (a terceira ficou: ela reage
com falas reais dela, curtas); a bateria completa não foi refeita, porque nada do prompt fixo mudou.

O `lorebook.json` também mudou nessa noite (era `2bcf046c1707`): 9 chaves novas na entrada "Origíneo", sem mexer no
conteúdo de nenhuma entrada. Efeito: perguntas sobre o corpo de um infectado morto passam a acionar essa entrada.
