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
