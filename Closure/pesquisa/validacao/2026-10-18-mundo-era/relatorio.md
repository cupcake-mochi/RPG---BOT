# Consulta da Era da Revolução — 18/10/2026

Implementação: `4200281`, branch `codex/mundo-era-revolucao`, PR 66 em rascunho,
com base na branch da PR 65. Sem merge ou implantação desta funcionalidade.

## Fontes e exclusão

O ZIP fornecido pelo usuário tem SHA256
`b0a2c4ab1995ca8c176000898a85cbc28029dae252987e6fc3c29b0aa04eaa07`.
Importação reproduzida e comparada por igualdade com o JSON salvo: 31 documentos,
228 seções; 21 registros de regiões/índice, dois públicos e oito de mestragem.
`importacao.json` registra os caminhos e hashes individuais.

Somente entradas `01/02/03-.../*/Texto-para-Discord.txt` são abertas.
04 Reservado Mizuki, 05 Registros Complementares, 06 Recursos Visuais e índices
globais não entram. Não há modo de acesso privado do dono. Um teste com conteúdo
canário inclusive inválido em UTF-8 demonstra que as entradas excluídas nem
passam pelo leitor do ZIP; outro verifica ausência dos caminhos no núcleo.
Nenhum conteúdo das três pastas foi necessário para esta validação.

## Ensaios específicos e pacote

- **Suíte completa: 834 executados, 833 aprovados e um online opcional pulado**,
  296,489 s, sem falhas/erros. Comando: `python -m unittest discover -v -s testes`
  a partir de `Closure/src/`, usando o runtime descrito abaixo.
  Saída completa: `suite-completa.log`. Inclui os 12 testes novos.
- **12 testes novos aprovados**: importação seletiva, tamanho/duplicatas,
  limpeza de links/menções, corpus/proveniência, continuação/mudança de assunto,
  recuperação de todas as regiões, cidade pelo nome, fatos publicados fora do
  detector de bordão, orçamento de contexto, duas guias e motores iguais.
  Saída: `era-testes-mundo.log`.
- **14/14 casos da ponte iguais** entre QuickJS e Node após regeneração do núcleo.
  Versões: Closure v0.37, Kal'tsit v0.30, lorebook v2.0 e mundo era-2026-10-18-v1.
- **12/12 pedidos pelo pacote extraído aprovados**, seis perguntas nas duas
  guias: acesso a Victoria/Ægir, capital de Columbia, chegada à Lua, promoção de
  Grau e ausência de cura conhecida para Oripatia. A cópia extraída só tem os
  arquivos de execução, comprovando que a hospedagem não precisa do ZIP original
  nem dos arquivos de autoria. Saída: `era-smoke-pacote.json`.
- **67/67 arquivos do ZIP iguais aos fontes de empacotamento**. Corpus embutido
  comparado por igualdade ao JSON autorizado. Sem `.env`, bancos ou cadastro de
  campanha. Em relação ao pacote B47 instalado, apenas
  `src/var/site/nucleo.js` mudou. Saída: `era-pacote-validacao.json`.

Pacote de entrega: `closure-lab-era-revolucao-2026-10-18.zip`, 1.206.024 bytes,
SHA256 `acc3e58d71f8410c144b0c70a5fed383f1adeb14e167a695c7d68adf8c5b180d`.
Fica em `entregas/`, fora do Git. Aproximadamente 53 KiB a mais no ZIP em relação
à versão instalada. Não há biblioteca nova ou chamada adicional de modelo
para recuperar fontes.

## Método e limites

Ensaios offline, Python 3.12 e dependências da `.venv` existente copiadas para
disco local em `/tmp/era-runtime`; mesmos fontes em `/tmp/era-validacao/Closure`
para evitar interferência da latência do disco externo. O caminho `.venv` do
ambiente de teste aponta para esse runtime, necessário ao ensaio da CLI de
campanha. Nenhuma dependência ou expectativa foi alterada para obter aprovação.
O núcleo regenerado no checkout foi comparado por bytes com o da cópia testada.

Os provedores da suíte são simulados; não houve chamada paga, mensagem ao
Discord ou teste de resposta real do modelo nesta entrega. Recuperação correta
não certifica a redação final, fidelidade ou obediência perfeita de um modelo.
A busca é lexical e limitada; perguntas amplas podem precisar ser divididas.

O conteúdo da mestragem preserva a redação da campanha, inclusive eventuais
ambiguidades. Não altera a avaliação B47 nem converte prosa, lembrete do jogador
ou um trecho recuperado em aprovação. Autorizações, limites de uso de NPCs e
conhecimento de PJs continuam a cargo dos responsáveis humanos.

Retomada/publicação/roteiro: `docs/RETOMADA-MUNDO.md` e `dados/mundo/LEIA-ME.md`.
