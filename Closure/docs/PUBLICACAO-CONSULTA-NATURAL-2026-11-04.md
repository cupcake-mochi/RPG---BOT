# Publicação das correções de consulta

Publicado no app Guias do Ciclo (`1773761486581`) em **04/11/2026**.
Os logs registraram o bot online às **11:00:04,923 (Brasília)**, em seis
servidores. Runtime: `609bcbb2609d29d8a57c9ab946566d0a37a6f263`, merge da
[PR #100](https://github.com/cupcake-mochi/RPG---BOT/pull/100).

A consulta permanece R63/v0.373, com 576 trechos. A análise mecânica continua
R53. Carteira Viva, cadastros, fichas oficiais e fichas de jogadores intactos.

## Verificações

- [CI aprovado](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/41841591448)
  no código `0daf7f3ff39bc054476b75f8b582f6339105b184`, antes do merge.
  A árvore do merge é igual à testada. Validação anterior: 1.012 testes,
  1.011 aprovados e um online opcional pulado; auditoria 498/498 fontes.
- Backup anterior criado, baixado e validado antes do Commit: 270 arquivos,
  3.415.990 bytes. Inclui ambiente, campanha e dois bancos íntegros.
- Pacote regenerado na main aprovada: 92 arquivos, 1.855.867 bytes,
  SHA-256 `d13728fde2ed819c35f87c6a669d9224d8fc768c516af771c4ec28cdce0f825d`.
  Sem ambiente, bancos ou cadastro real no ZIP de atualização.
- Envio pelo Commit do app existente. Build automático concluído;
  nenhum Rebuild separado. Logs sem erro de início, apenas avisos de
  dependências de voz ausentes.
- Backup posterior: 270 arquivos, 3.417.480 bytes,
  SHA-256 `0dee76832f43d314e2250b236e9104aec1d477377286049fa35cbbedd21c48ff`.
  **92/92 arquivos instalados idênticos ao pacote**, comparados byte a byte.
- `.env` e cadastro de campanha idênticos antes/depois. Os dois bancos
  passaram em `PRAGMA integrity_check`; esquemas e conteúdo das 18 tabelas
  (duas e 16) ficaram iguais, sem exceções.
- Teste adicional no núcleo extraído do backup posterior: quatro casos
  relatados × duas personagens × dois modos de lore, 16 combinações,
  passou em 5,745 s. Confere as fontes completas selecionadas, sem modelo pago.

Backups e comprovante visual estão em armazenamento local privado, fora do Git.
O Discord pediu novo login: `GC:ping` após este envio não foi executado.
Respostas conversacionais geradas por modelo também não foram testadas nesta
publicação. A confirmação anterior de ping às 10h03 pertence ao deploy R63
anterior; não deve ser atribuída a este envio.

## Continuidade

Correções já publicadas. Não repetir deploy por este registro documental.
Se houver sessão autenticada, resta a conferência opcional de `GC:ping` no
Discord. Ensaios de respostas com modelo dependem de autorização de quantidade
e custo. Carteira Viva permanece na sua fila separada, sem avanço nesta rodada.
