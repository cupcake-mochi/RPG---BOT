# Publicação da consulta R63

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **04/11/2026 às
10:03:02,953**, horário de Brasília. O runtime é o merge
`2356c11d70205762dfbe89f9365d36ced47e53b5` da
[PR #98](https://github.com/cupcake-mochi/RPG---BOT/pull/98).
A consulta passou para **R63/v0.373**, com 576 trechos. A análise segue na R53.

## Git e testes

- O push confirmou `088a4afed97444aaad66d8bdae5e5db93717a60f` na branch da
  consulta. A PR estava sem conflitos e o CI passou antes do merge.
  [Execução do CI](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/41833773168)
- A árvore de arquivos do merge é idêntica à do commit testado. A suíte local
  teve 1.002 testes, 1.001 aprovados e um online opcional pulado. A auditoria
  recuperou 498/498 fontes e as 13 referências mecânicas deram iguais.
  [Validação da consulta](CONSULTA-R63-2026-11-04.md)

## Discloud

O backup prévio foi baixado e validado antes do envio. Tinha 270 arquivos e
3.414.732 bytes, incluía `.env`, campanha e os dois bancos íntegros. Os 92
arquivos do runtime anterior coincidiam com o backup após a PR #96.

O ZIP de atualização tem 92 arquivos e 1.854.368 bytes. SHA-256
`012dfd9de8482179cee996ac95ddee5e09368f6aa0b20b7bf41c32a7b560f7db`.
O envio foi feito pelo Commit do app existente com o build automático.

O backup posterior tem 270 arquivos e 3.415.990 bytes. Os **92/92 arquivos
instalados** coincidem com o ZIP. `.env` e campanha são idênticos ao backup
prévio. Os dois bancos passaram em `PRAGMA integrity_check`. O esquema e as
18 tabelas, duas no primeiro banco e 16 no segundo, ficaram iguais. Os backups
estão em armazenamento local privado.

## Conferência em produção

Os logs mostraram o bot online em seis servidores, com zero erros de início
e os avisos já conhecidos de dependências de voz. Às 10h03, `GC:ping`
respondeu **R63/v0.373**, 576 trechos e 50 ms no tópico Testes.
[Resposta no Discord](https://discord.com/channels/1357866906341736488/1561410667108368575/1567524772059938927)

A validação de consulta cobriu as fontes recuperadas. As respostas
conversacionais do modelo ficaram fora do ensaio desta publicação.
