# Revalidação entre o diário e o envio

30/10/2026 · etapa 7 parcial · PR84 · sem publicação.

Retomada em `c92b14e`, árvore limpa e branch igual ao remoto. A main publicada
está em `6b30985` (runtime `229e539`, consulta R60); ela não foi incorporada nesta
cadeia experimental. PR31 do produtor continua em `83996e8`, sem alterações aqui.
Os ensaios financeiros e de propriedades já encerrados não foram repetidos.

## Defeito reproduzido

Nos serviços de cópia e financeiro, a transação que grava o estado `enviada`
é assíncrona. Entre a última conferência do contexto e seu retorno, a conta podia
ser desconectada ou o prazo expirar. O próximo passo era o POST, e a recusa por
acesso/prazo aparecia somente depois do envio.

Quatro regressões reproduziram o problema antes da correção: desconexão e
expiração após armar o diário nos dois serviços. Todas falharam porque havia um
POST simulado. Não há dados reais nas fixtures nem chamada ao Google.

A correção reconfere membro, autorização/contexto e validade do token **depois**
da transação e **antes** do POST. Não espera uma nova cota nem rearma o diário.
Uma recusa deixa `enviada`: a recuperação continua somente por leitura, sem
repetir um envio cujo estado durável já avançou. No financeiro, a regressão de
expiração também tenta retomar e exige zero POSTs.

Isso fecha o intervalo assíncrono observado; **não** fornece CAS no Google,
bloqueio de edições do dono ou atomicidade entre a autorização e a rede. Uma
revogação depois da última observação ainda depende da fiscalização do Google.
Nenhum indicador global foi liberado e nenhuma permissão foi ampliada.

## Validação

A bateria financeira após a correção passou: 42 testes, zero falhas, 36,377 s.
O conjunto completo de cópia e financeiro e o CI desta revisão têm seu fechamento
registrado na retomada. Não certificar ativação, demais domínios ou criação com
base nessa correção de envio. ZIP de produção não precisa ser republicado:
`carteira_viva/` não integra o pacote estável atual.

Fechamento: 85 testes conjuntos passaram em65,236s. CI41160365416, código1268e1b, concluiu em30/10 às23:35:14 Brasília:1.647 executados/1.646 aprovados/um opcional, zero falhas,230,489s. Execução local anterior saída143, sem conclusão, não contada como aprovação.

## Contrato após atualização concorrente do produtor

A main da ficha avançou para5ea10b4 (PR44, correção de origens da ANALISE).
O CI sintético da PR31 recusou o contrato por três hashes antigos, embora os
29 cenários novos de ativação tenham passado. A main foi integrada à branch
experimental do produtor; não houve merge da PR31 em main.

Comparação recursiva da exportação confirmou que só os hashes de Ficha.gs,
Pessoal.gs e Configuracao.gs mudaram. Todos os campos operacionais, fórmulas,
faixas, indicadores e protocolos são idênticos. Artefato regenerado no produtor
0c6c171 e importado aqui com nova guarda estrita:
`0c9dcc89e6b1cb3401a54fb1311d9f72c60774cbec84d741474a7a6066bd8098`.
47 cenários REST/piso no produtor e68 de conferência/financeiro no bot
(78,593s) aprovados. Não altera retrospectivamente recibos históricos nem reusa
grants: operações antigas vinculadas a outro hash devem recusar, como antes.
Nenhuma nova equivalência de fórmula ou versão foi acrescentada.
