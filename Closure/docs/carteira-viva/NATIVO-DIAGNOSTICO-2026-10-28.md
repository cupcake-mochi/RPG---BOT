# Diagnóstico da origem no Google

28/10/2026 · PR 84 · **leitura de progressão validada no caminho observado; ensaio encerrado**.
Código do serviço `10df9c2fc94e333bdcce8225a62629e2500ff675`.
Limpeza concluída às **23:47:20 de Brasília**, sem recursos ativos do piloto.

## Preparação e autorização

Nova cópia nativa da oficial Ciclo, feita pelo conector e colocada na pasta privada
ChatGPT, com nome **QA Carteira — diagnóstico de versões — DESCARTÁVEL — 28-10-2026**.
Metadados confirmaram ID diferente da oficial, tipo Google Sheets, pasta esperada,
`shared=false` e uma única permissão de usuário proprietário. Nenhuma célula foi
editada ou preenchida, nenhuma oficial/jogador alterada e nenhuma função GS executada.

Piloto loopback em `127.0.0.1:8876`, banco/chave/segredo de serviço novos fora do
Git, usando o app já existente. Login Discord principal, consentimento Google
confirmado pessoalmente pelo usuário e somente essa descartável escolhida pelo
Picker. Prévia conferida e cadastro fictício na base isolada. Não reutilizou grant
revogado dos ensaios anteriores nem alterou a campanha/configuração de produção.

O transporte privado bloqueava escrita Drive/Sheets: só GETs e POSTs necessários
aos endpoints OAuth. O serviço diagnosticou a origem da intenção **preparada**, sem
fixar sua versão original, armar envio, criar destino ou iniciar financeiro.
A única criação remota foi a fonte descartável pelo conector.

## Primeira tentativa: financeiro interrompido

A configuração do modelo e a intenção preparada chegaram a ser registradas. A
sessão de comando terminou com código **143**, sem resultado salvo. O motivo e o
momento exatos do encerramento não foram determinados. A porta estava fechada,
mas o arquivo de estado continuava em `comparando_leituras`, e o contador só tinha
um checkpoint anterior. O acompanhamento inicialmente confundiu esse estado
antigo com execução ativa; isso foi corrigido e explicado ao usuário.

A espera observada de cerca de 1.341 s desde a gravação daquele estado **não é
medição do tempo do serviço**. Não há contagem completa de chamadas, comparação
financeira, causa de versão, HTTP429 ou timeout do serviço demonstrados nessa
primeira tentativa. Não converter a interrupção em sucesso ou em diagnóstico de
lentidão do bot, Google ou computador. A intenção seguia preparada, sem diário
financeiro; o transporte continuava sem permissão de POST Drive/Sheets.

## Retomada: duas leituras de progressão

O runner foi desacoplado da sessão de comando e passou a salvar contagens/status
antes/depois de cada chamada. A retomada usou a mesma fonte, base, conexão e grant
válido, sem novo login ou consentimento. Fez **duas amostras novas de progressão**;
não reutilizou hashes ou páginas da tentativa financeira interrompida.

Fluxo da retomada concluído em **164,128 s**, incluindo a preparação do chamador:

- Duas amostras completas: **8/8 páginas cada**, cobertura compatível.
- Oito páginas comparadas; zero páginas com mudança em literais, fórmulas,
  resultados, notas e formatos numéricos.
- Versões iniciais iguais; nenhuma divergência durante a coleta ou nos sinais
  de antes/depois das amostras.
- Diário preparado idêntico antes/depois; versão original não fixada, destino
  não criado, nenhum diário financeiro ou POST Drive/Sheets.
- Quatro indicadores de liberação permaneceram falsos.

Fase do diagnóstico: **188 GETs de membro, dois de servidor, dois de cargos,
um POST OAuth Google, 42 GETs Drive e 18 GETs Sheets: 253 HTTP200**. A preparação
do chamador somou outros 13 HTTP200. Nenhum HTTP429 nessa retomada.

Essa medição mostra o custo da rede para dois retratos completos do domínio.
Otimização posterior pode avaliar agrupar faixas pequenas em GETs, preservando
cobertura, versão, acesso atual por chamada, cota e cancelamento. Não aumentar
cotas ou trocar autorização por TTL para reduzir o número aparente.

## Encerramento

- Runner encerrado normalmente; porta 8876 livre e nenhum runner ativo.
- Única descartável desta rodada na lixeira **recuperável**, PATCH HTTP200 seguido
  de GET HTTP200 confirmando ID/propriedade/`trashed=true`. Nada excluído em definitivo.
- Revogação Google HTTP200. Nova chamada do próprio diagnóstico recusada com
  `revogada`/OAuth HTTP400; cinco GETs Discord HTTP200 e **zero Drive/Sheets** após revogar.
- Dados fictícios removidos: zero personagens, fontes, cópias, financeiro,
  configuração de modelo, fluxos web, sessões, conexões ativas e segredos retidos.
- Integridade `ok` no banco e ledger. Arquivos privados de execução/credenciais
  permanecem fora do Git; nenhum ID privado, ticket, token ou dado pessoal no relatório.
- Abas criadas para o piloto fechadas; aba anterior do usuário preservada.

## O que esta prova não conclui

É uma prova real do **dono, numa fonte privada descartável e somente em progressão**.
Não confere se as fórmulas/contas de progressão estão corretas. Também não é
comparação financeira, prova de estabilidade global, causa das mudanças de
versão anteriores, preservação de imagens ou inicialização limpa. A interrupção
financeira continua sem resultado comparável. Não houve escrita financeira,
resposta de escrita perdida ou reconciliação nativa dessa escrita.

Financeiro, diagnóstico da candidata, propriedades Apps Script, demais domínios,
concorrência, preservação, automações/responsável e prova integral seguem pendentes.
Criação bloqueada/quatro indicadores falsos. Sem modelo pago, escopo novo, Gateway,
merge, Discloud ou alteração do produtor/oficiais/jogadores.

## Continuar

1. Conferir topo da fila e código/CI; esta rodada não deixa grant, runner ou fonte
   ativa a retomar. Não restaurar a descartável ou usar o token revogado.
2. Antes de outro ensaio financeiro longo, melhorar o acompanhamento do ciclo de
   vida e avaliar coleta agrupada com regressões, sem truncar ou adotar versões.
3. Retomar diagnóstico financeiro e preparação de conteúdo somente com escopo e
   recursos descartáveis explícitos. Propriedades/demais domínios e escrita continuam
   exigindo provas próprias; este resultado não substitui nenhuma delas.

Sol Alto para continuar; revisão Médio.
