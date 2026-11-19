# Publicação da consulta R68

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **19/11/2026 às
10:02:49**, horário de Brasília. O runtime é o merge
`4f4c5f6ccc15496d3ebd8d576123b7b82941fffc` da
[PR #106](https://github.com/cupcake-mochi/RPG---BOT/pull/106).
A consulta passou para **R68/v0.379**, com 576 trechos. A análise segue na R53.
Este registro é só documental: não republicar por causa dele.

## Git e testes

- O CI da PR passou no commit `5d4add1` (1.031 testes, OK, um pulado).
  O merge saiu com a árvore idêntica a esse commit.
- A preparação, a auditoria (498/498) e a pendência da Técnica Máxima estão em
  [Consulta R68](CONSULTA-R68-2026-11-19.md).

## Discloud

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (09:58) | 188 | 3440659 | `5692dab9b762792a09df752d63b902bdd8afd7e6fe66ad135cf291909fd639ae` |
| Pacote (`ferramentas/empacotar.py`, main `4f4c5f6`) | 93 | 1863430 | `099cdfabb6306520fa70afcbcb1112a256cb9ef7e1a3f45b7216389eb960b6a8` |
| Backup depois do envio (10:03) | 188 | 3442734 | `6f5838833655591021e94f99358bdb9d55d62f80973dcc7348426c9d5a7ee263` |

- O pacote foi montado no Windows, a partir de um checkout com
  `core.autocrlf=false`. Como da última vez, o empacotador regerou
  `src/var/site/nucleo.js` com CRLF, e essa entrada foi normalizada para LF.
  Nenhum arquivo de texto do pacote tem CRLF. Os 93 arquivos são iguais ao
  commit e ao núcleo testado, sem `.env`, bancos, campanha ou dados de jogador.
- Comparado ao que estava instalado antes, o pacote mudava só três arquivos:
  `nucleo.js`, `MANIFESTO.json` e `livro.jsonl`.
- O envio foi feito pelo Commit do app existente, com o build automático. O ZIP
  foi anexado pela extensão do Claude no navegador do Mizuki.
- No backup de depois, os **93/93 arquivos do pacote estão instalados iguais**,
  sem nenhum ausente ou divergente.
- `.env` e campanha estão iguais ao backup de antes (hash). Os dois bancos deram
  `integrity_check` `ok`. As 18 tabelas, 2 no primeiro e 16 no segundo, têm o
  mesmo dump e as mesmas contagens antes e depois. A comparação foi por
  contagens e hashes, sem expor valores.
- Os backups e o pacote ficam fora do Git, em armazenamento local privado.

## Conferência em produção

- Logs: online em **7 servidores** às 10:02:49, com zero erros e só os avisos
  de voz já conhecidos (PyNaCl/davey).
- Discord, 10:06, tópico Testes: `GC:ping` respondeu “No ar (42 ms). Regras:
  Ciclo Maldito v0.379, versão do livro: R68, 576 trechos de referência.”
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1572961253289369636)
- `GC:livro` respondeu com o painel do livro e o link do PDF.
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1572961369735823431)

## Pendências reais

- Respostas conversacionais do modelo sobre a R68 não foram ensaiadas, para não
  fazer chamada paga. A recuperação de fontes foi conferida localmente.
- A análise da ficha não segue a Técnica Máxima R67/R68. Detalhes em
  [Consulta R68](CONSULTA-R68-2026-11-19.md#pendência-a-análise-da-ficha-não-segue-a-técnica-máxima-r67).
