# Modelos de ficha

## Modelos oficiais atuais · 25/10/2026

O Mizuki confirmou em 25/10/2026 que os **dois** modelos abaixo são oficiais.
A Closure e a Kal'tsit oferecem os dois, com estes nomes, quando alguém pede a
ficha; se a pessoa citar um deles pelo nome, só esse vai. O jogador usa
**Arquivo → Fazer uma cópia** no modelo que a mesa indicar.

| Nome mostrado | Planilha |
|---|---|
| Ficha · Era da Revolução | [1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k](https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit) |
| Ficha · Ciclo Maldito | [1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit) |

Fonte: `r53/OFICIAIS.md` do repositório da ficha (main após o PR #17). Os links
aparecem nos guias de criação PT/EN (`guias_ficha.py`, `recursos/guias-en.json`),
nas respostas diretas de link (`recursos_publicos.py`) e no contexto de recursos
públicos das duas personagens.

A antiga `1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro` é **histórica**: aparece
só em relatórios antigos e em testes que usam o link como exemplo de formato.
Não deve voltar a ser oferecida como modelo.

## Versões que não se confundem

| O que | Valor em 25/10/2026 | Onde aparece |
|---|---|---|
| Versão pública da ficha | **1.0** | `FICHA!H4` e número da carteira (`CARTEIRA!AH2`) |
| Contrato técnico da ficha | R53, ANALISE 12 / montagem esquema 2 | metadados de DADOS e ANALISE, lidos pelo bot |
| Versão do bot (Guias do Ciclo) | 1.0.3 publicada; código do Git à frente | `README.md`, `CHANGELOG.md`, `docs/FILA-ATUAL.txt` |
| Revisão do livro | Publicada: R57 (v0.367, 25/10). Lida pelo bot: R53 (v0.366) | `dados/sistema/MANIFESTO.json`, `/ping`; pendência em `docs/FICHAS-OFICIAIS-1.0.md` |

O rótulo 1.0 é só apresentação e não acompanha as revisões do livro. Ele não
significa que regras de uma edição nova entraram na ficha ou no bot. O leitor do
bot continua conferindo `formato.versao` 12 e os metadados R53; nenhum endereço
ou tipo do contrato mudou com o PR #17 da ficha.

## Manutenção

Os modelos são somente leitura para a manutenção do bot. Ensaios de
preenchimento usam cópias descartáveis, nunca fichas de jogadores. Em 24/10 a
`1MQqh…` tinha sido registrada só como base técnica do servidor; esse registro
foi substituído pela confirmação de 25/10 acima.
