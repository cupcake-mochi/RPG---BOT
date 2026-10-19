# Correção da consulta por nomes — Era da Revolução v2

O usuário confirmou que o registro de Shiki estava na fonte e pediu corrigir
a recuperação, prevenir falhas semelhantes e atualizar a Discloud ao final.

## Falha e correção

O importador descartava qualquer negrito que contivesse dois-pontos. Isso
excluía tanto rótulos genéricos quanto títulos válidos, entre eles
`Shiki Zen'in — Capo dei capi de Volsinii:`. O texto estava publicado, mas o
nome não abria sua fonte. A ordenação ainda favorecia a introdução regional
mesmo quando a consulta era especificamente sobre uma pessoa/localidade.

Agora o índice distingue os rótulos dos nomes em títulos; extrai o nome antes
do cargo, normaliza apóstrofos e aceita grafia sem apóstrofo. Infere formas
curtas apenas com indicação pessoal de cargo/parentesco e sem homônimo completo
no corpus; não abrevia Northern Court, Max D.C. ou localidades com descrição.
Alias mais longo prevalece sobre outro contido nele. Trechos sem menção ao
nome ficam fora da consulta específica, preservada a busca ampla por região.

O JSON foi reindexado a partir dos textos autorizados salvos. Os **31 caminhos,
hashes e textos/228 seções são idênticos à v1**; não foi necessário acessar o
ZIP original nem pastas excluídas. Livro R52/B47, cards, memória, mídia,
aprovações e configuração não foram alterados.

## Verificações

- **Suíte completa: 841 executados, 840 aprovados e um online opcional pulado**,
  313,873 s, sem falhas/erros. Inclui 19 testes de mundo, sete novos nesta
  correção. `suite-completa.log`. Runtime local Python 3.12 com as dependências
  existentes e cópia sincronizada dos fontes, como na validação anterior.
- Reprodução nos núcleos reais: na v1, Shiki e suas variantes não retornavam
  fonte; na v2 retornam Situação Atual — Siracusano II, com o título limitado
  a Volsinii e sem substituir Signora Sicilia. `antes-depois.json`.
- **341/341 consultas do índice regional recuperam sua fonte**, verificadas
  no núcleo realmente empacotado, sem modelo. `auditoria-indice.json`.
- Regressões de Shiki/nome completo/apóstrofos/acentos nas duas guias,
  Cellinia e localidades, fronteira de palavra, rótulos genéricos, homônimos,
  preservação da fonte, exclusões e igualdade JSON/núcleo. Os dados não são
  considerados cobertos só por estarem no arquivo: a consulta é exercitada.
- Pacote: **67 arquivos**, apenas `src/var/site/nucleo.js` diferente da v1;
  versão `era-2026-10-18-v2`, 1.206.340 bytes, SHA256
  `d43dbd27bc63770c57ff18af498d8873edc8cbbbd3d1327740c5623141906d9c`.
  `pacote.json`. ZIP fora do Git: `entregas/closure-lab-era-revolucao-nomes-2026-10-18.zip`.

Os ensaios de recuperação/montagem de prompt não chamam modelo. Resposta final
de um modelo, estilo e interpretação não são certificados por estes ensaios.
A busca continua lexical e limitada, sem prometer toda abreviação ou erro de
grafia possível. As pastas 04/05/06 seguem excluídas até para o dono.
