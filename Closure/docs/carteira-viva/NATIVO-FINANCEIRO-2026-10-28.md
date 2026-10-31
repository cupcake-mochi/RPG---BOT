# Ensaio financeiro no Google

28/10/2026 · PR 84 · **encerrado com recusas seguras, sem validar a escrita**.
Código `7491d811ee0d3ab7f3455fddc736ee4430d4bb2e`, sem alteração de runtime nesta rodada.
Limpeza concluída às **21:36:57 de Brasília**.

Atualização offline posterior: [candidatas e diagnóstico](CANDIDATAS-2026-10-28.md).
O ensaio documentado aqui continua sendo o código 7491d81; não foi repetido ou
reclassificado como validação da escrita. A causa das versões segue pendente.

## Resultado

O bot não enviou nenhum POST Sheets financeiro. A perda deliberada de uma
resposta HTTP200 não chegou a ser injetada; reconciliação após escrita real
continua sem validação. Não chamar os 1.514 testes offline de prova nativa.

A fonte foi criada por cópia nativa da oficial, em arquivo privado e descartável.
Somente essa fonte recebeu `EXTRATO!A2:C2` fictício e uma nota, pelo conector.
Leitura posterior confirmou os dados/notas e preservação dos formatos anteriores.
Oficiais e fichas de jogadores não foram editadas.

OAuth/Picker próprios das Guias, identidade Discord real e base/chave/segredo novos,
fora do Git. Primeira solicitação de dez minutos expirou antes da seleção; a segunda
concluiu autorização, seleção e cadastro da fonte fictícia. O prazo não foi ampliado.

## Primeira cópia: versão mudou durante a leitura

Um POST Drive ficou sem resposta registrada e retornou `copia_incerta` em
23,830 s. A mesma intenção foi recuperada sem segundo POST em 13,908 s, com
marcadores/propriedade pessoal/privacidade conferidos. Retomada: 45 GETs Discord,
um OAuth e três GETs Drive, todos HTTP200; zero Sheets.

O adaptador financeiro começou a leitura, mas a versão do destino passou de
**9 para 10**. Recusa `alterada` em **157,908 s**, antes de criar diário financeiro
ou enviar limpeza. Houve 387 GETs Discord, um OAuth, 28 GETs Drive e 13 GETs
Sheets (metadados e 12 páginas): **429 respostas HTTP200, nenhum HTTP429**.
A fonte ainda estava na versão 12 no diagnóstico posterior. A causa da mudança
de versão da cópia não foi demonstrada; não atribuir a usuário ou recálculo.

## Segunda candidata: fonte mudou antes da identificação

Nova intenção descartável, um único POST Drive sem resposta registrada. A
primeira busca ainda não encontrou arquivo; a busca posterior encontrou uma
candidata única. Nenhum POST de criação foi repetido.

A preparação privada fez apenas leituras antes do primeiro recibo de identificação:
leu as dependências pequenas e uma grade financeira completa, fechada na versão
**9**. Esse preparo foi do runner de ensaio, não uma fase já integrada ao bot.
Não atualizou o recibo da primeira cópia recusada nem reinterpretou versões.

A preparação/identificação terminou em **418,688 s**, recusada porque a **fonte**
passou de **12 para 13**. A candidata continuou `enviada`, sem recibo identificado,
e o segundo adaptador de escrita financeira nem foi chamado. O bloqueio exato foi
“O modelo mudou durante a cópia. Não inicialize esse arquivo.”

Diagnóstico adicional na candidata: cinco GETs, incluindo projeções simples/ricas,
revalidação HTTP e `alt=json`, devolveram versão 9 e HTTP200, com Date atual e
`Cache-Control: no-cache, no-store, max-age=0, must-revalidate`. A comparação
**não demonstrou problema de cache**. Não adicionar exceções ou adotar outra
versão para fazer passar; a causa da mudança da fonte também continua desconhecida.

## Encerramento

- Fonte e duas cópias na lixeira recuperável: três PATCH HTTP200, cada um seguido
  de GET HTTP200 confirmando `trashed=true` e propriedade pessoal.
- Usado somente o grant do ensaio. O conector não oferece lixeira recuperável;
  o encerramento usou a API Drive, com IDs privados derivados dos próprios diários.
- Revogação HTTP200. Tentativa posterior recebeu `revogada`/OAuth HTTP400, com
  nove GETs Discord e **zero GET/POST Drive ou Sheets** após a revogação.
- Dados fictícios removidos globalmente na base isolada. Zero personagens,
  operações de cópia, diários financeiros, conexões ativas ou segredos de jogador.
  Cadastro e ledger com `integrity_check=ok`; porta 8876 livre, runners encerrados.
- Nenhum Apps Script, Gateway, modelo pago, escopo novo, campanha real, merge ou
  deploy. Nenhum ID privado, token, banco ou conteúdo pessoal neste relatório/Git/ZIP.

## Próximo trabalho

**Bot:** investigar, em ensaio controlado e sem escrita, o que altera as versões
no intervalo entre criação, leitura e identificação. Definir uma fase de candidata
com vínculo explícito ao modelo e ao contrato antes do primeiro recibo imutável.
A preparação manual acima não resolveu o caso da fonte e não deve virar aprovação.
Preservar o bloqueio de versões, os marcadores, a autorização atual e o diário sem
replay. Uma cópia já identificada/recusada não pode receber uma versão nova.

**Produtor/contrato:** cinco propriedades financeiras Apps Script continuam fora
da API de células; demais domínios, preservação global, arte, automações/notas
vivas/treinos e responsável precisam de implementação/prova próprias. Se houver
novo recibo de conteúdo/propriedades, definir cobertura e semântica em proposta
separada; nunca inferir preservação ou ausência de histórico pela versão Drive.
Não mudar a oficial ou ampliar `drive.file` para contornar a limitação.

**Mestre:** nenhuma autorização ou decisão real de campanha foi automatizada ou
concedida. Aprendizado, requisitos livres, narrativa e autorizações seguem humanos.

A escrita/reconciliação nativas continuam pendentes. Criação incondicionalmente
bloqueada e quatro indicadores gerais falsos. Não repetir OAuth/cópias até fechar
o diagnóstico e o protocolo; descartáveis/grant deste ensaio já foram encerrados.
Sem mudança de código, não repetir suíte/ZIP nem publicar por este fechamento.
Sol Alto para continuar; Médio para revisão focal.
