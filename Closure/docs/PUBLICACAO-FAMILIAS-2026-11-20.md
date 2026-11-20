# Publicação do conserto das Famílias repetidas

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **20/11/2026 às
00:02:42**, horário de Brasília. O runtime é o merge
`56b02cf44b6ba294ebb13d49df576855007980f8` da
[PR #113](https://github.com/cupcake-mochi/RPG---BOT/pull/113).

A consulta continua na R68/v0.379. O que muda: numa ficha com cartão ou Máxima,
os erros "regra · familias livres" e "regra · familias fechadas" apareciam
duas vezes no painel do `GC:ficha`. Isso acontecia porque
`ficha_magia.escolhas_familias` e `ficha_b47.conferir_b47` chamam
`conferir_familias` cada um. Agora o `conferir_b47` tira os itens repetidos,
mas só os iguais em todos os campos (regra, campo, esperado, encontrado e
âncora). Erro diferente continua aparecendo.

## Git e testes

- O CI da PR passou no commit `ee86b4f`, com 1.038 testes, OK e um pulado. No
  `Closure/src`, o merge é idêntico a esse commit.
- O teste novo é o `test_b47_familias_repetidas.py`.

## Discloud

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (00:01) | 188 | 3453048 | `0c84282a07a10f07381500ae00b577f9cb1b72039bd444dbe979633a896e1446` |
| Pacote (`ferramentas/empacotar.py`, commit `56b02cf`) | 93 | 1866658 | `504ae361a593344305c58158deccf923ac000280830b61c4b9aa5d70accc0719` |
| Backup depois do envio (00:03) | 188 | 3453317 | `6b09eabf75b38f1a49d7a7d9f8ddcac097eed97948fb3b9e5ba51a9e38507c5d` |

- **Montagem do pacote.** Foi feita num clone novo com `core.autocrlf=false`.
  O `nucleo.js` foi normalizado para LF, como nas outras vezes. Os 92 arquivos
  versionados são iguais ao commit, e nenhum arquivo de texto tem CRLF.
- **O que estava instalado.** O backup de antes confirmou o runtime `921e7c8`.
  Contra ele, o pacote trocava só o `ficha_b47.py`.
- **Desde o backup das 20:48 de 19/11.** O `.env`, a campanha e o
  `closure_lab.db` estavam iguais. O `bot.sqlite3` só cresceu com o uso
  (chamadas, falas, mensagens), o que é o esperado.
- **Envio.** Foi pelo Commit do app existente, com o build automático. O ZIP
  foi anexado pelo mesmo caminho do registro do
  [Acerto da Expansão](PUBLICACAO-EXP-ACERTO-R53-2026-11-19.md): o `click()`
  do input de arquivo foi interceptado e restaurado logo depois.
- **Conferência no backup de depois.**
  - Os 93 arquivos do pacote estão instalados iguais.
  - O `.env` e a campanha têm o mesmo hash do backup de antes.
  - Os dois bancos deram `integrity_check` `ok`, e as 18 tabelas estão iguais.
  - A comparação foi feita por contagens e hashes, sem expor valores.
- **Guarda.** Os backups ficam fora do Git, em `D:\Downloads`, com o nome
  `backup-guias-2026-11-20-HHMM-…`.

## Conferência em produção

- **Logs:** online em **7 servidores** às 00:02:42, com zero erros. Só
  aparecem os avisos de voz já conhecidos.
- **Discord, 00:05, tópico Testes.** Mandei o `GC:ficha` com o mesmo `.xlsx`
  da Máxima usado às 21:55 de 19/11.
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1573172430283866134)
  - Antes eram 7 erros, 9 pendências e 6 páginas. Agora são **5 erros, 9
    pendências e 6 páginas**.
  - Na página Correções e revisão, "familias livres" e "familias fechadas"
    aparecem uma vez cada.
  - O cartão continua igual: "Técnica Máxima — Teste R67 Explosão · Classe 5 ·
    Dano 19d8 · 25 PE · saldo 8 · ficha VÁLIDO".

## Pendências reais

- Os cartões de feitiço e de Liberação preenchidos ainda não passaram pelo
  Discord.
- A divergência de RAM (`RAM=256` no `discloud.config`, 512 MB no painel)
  continua em aberto. Veja [Discloud em 05/11/2026](DISCLOUD-2026-11-05.md).
