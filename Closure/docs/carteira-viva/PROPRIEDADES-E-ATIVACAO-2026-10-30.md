# Propriedades e ativação da cópia

30/10/2026 · investigação do contrato · **nenhuma ativação implementada ou executada**.
A escrita de células e a recuperação já foram [validadas](NATIVO-ESCRITA-EQUIVALENTE-2026-10-30.md).
Este documento delimita o que falta fora das células; não substitui essa prova.

## O que cada propriedade controla

Leitura do produtor `Ficha---RPG-JJK`, branch `codex/inicializacao-financeira-carteira`,
HEAD `e1a5691`; main observada `ef361cc`. Nenhum fonte do produtor alterado.
O contrato REST atual lista exatamente estas cinco propriedades:

| Escopo e chave | Uso no produtor | Estado inicial proposto para uma cópia ainda isolada |
| --- | --- | --- |
| Documento · `salario_extrato` | Quantidade de lançamentos para encontrar a próxima linha de EXTRATO. Ausente, a rotina rederiva pelo livro. | Ausente após conferir o livro limpo; não copiar o contador do modelo. |
| Documento · `salario_trocas` | Posição do histórico de mudanças em DADOS_SALARIOS H:J. Ausente, usa o total calculado em Q5. | Ausente após limpar o histórico e conferir as fórmulas preservadas. |
| Documento · `salario_correcao_nome` | Nome temporário usado entre digitar a missão e corrigir sua data. | Ausente, junto das caixas BI11/BO11 vazias. Não carregar um nome do personagem anterior. |
| Documento · `salario_proximo` | Cache de próxima apuração nos remendos de abertura/edição. Pode ser recriado ao abrir. | Ausente no fechamento da inicialização; depois, só o estado derivado pela ativação própria validada. Não exigir ausência para sempre. |
| Script · `salario_edicao` | Marca o projeto que tem edição instalável ativada; evita tratar o mesmo evento pelo caminho simples. | Ausente antes da ativação. Se a edição instalável for ativada, precisa corresponder ao projeto da cópia e aos acionadores do responsável. |

Fontes: `apps-script/Salarios.gs` (registro de trocas, extrato, correção e
`ativarSalarioDiario`), `r53/diagnostico-android/salario_lote.gs`,
`salario_na_edicao.gs` e `r53/inicializacao/financeiro.gs`.

`salario_edicao` não é só cache: apagar a chave sem coordenar a ativação pode
reabrir o caminho simples enquanto já existe a edição instalável. Escrever o ID
sem comprovar o acionador pode suprimir a rotina simples e deixar a ação sem
tratamento. Nenhuma dessas alternativas equivale a ativar corretamente a cópia.

Não usar `deleteAllProperties()`. Editor, recuperações, montagem, paleta e diários
têm outras propriedades. Não apagar diários existentes para tentar recomeçar.

## Limite do acesso atual

`drive.file` autoriza os arquivos escolhidos no Drive/Sheets. O contrato de células
não expõe PropertiesService. Não há adaptador autorizado neste bot para consultar,
apagar ou atestar aquelas cinco propriedades por esse caminho.

A [API de execução do Apps Script](https://developers.google.com/apps-script/api/how-tos/execute)
exige um executável publicado, projeto Cloud padrão compartilhado e token com os
escopos de todo o script. Essa configuração não existe para cada cópia e não foi
autorizada nesta rodada. Não criar um endpoint público ou ampliar OAuth para
contornar esse limite.

A [documentação de acionadores](https://developers.google.com/apps-script/guides/triggers/installable)
explica que os instaláveis rodam como quem os criou e que uma conta não enxerga
os de outra. Logo, uma lista vazia de `getProjectTriggers()` de uma conta não prova
sozinha a inexistência global de acionadores. Uma conta central das Guias também
não passa a representar automaticamente o jogador.

[Escritas por API não disparam os eventos de edição](https://developers.google.com/apps-script/guides/triggers#restrictions).
Não simular `onEdit`, escrever uma caixa de comando e esperar que isso execute a
ativação, nem inferir a ativação do fato de um POST Sheets ter retornado200.

## Rota recomendada dentro dos limites atuais

Separar **inicialização pelo bot** de **ativação pelo responsável no Google**.
Isso é uma proposta para o contrato do produtor, não um procedimento já entregue:

1. Manter a cópia privada e fora do cadastro novo até concluir os domínios de
   inicialização. Vincular operação, contrato, origem, destino, responsável e
   estado esperado; manter a recuperação do envio único já implementada.
2. O produtor precisa fornecer uma ação própria, limitada à cópia ativa, que
   confira o vínculo e o estado sem pressupor um booleano vindo do navegador.
   A ação deve tratar só as cinco chaves, preservar as demais propriedades e
   coordenar bloqueio/diário/acionadores. Não reutilizar o inicializador inteiro
   para repetir resets de células que já foram concluídos pelo REST.
3. O responsável faz o aceite necessário na conta Google. Nenhum gatilho é
   criado pelo administrador do modelo ou pela conta central em seu lugar.
   A ausência de autorização mantém a cópia incompleta, com explicação clara.
4. A prova da ativação precisa cobrir o projeto e a identidade corretos, os
   acionadores necessários, o primeiro evento real e a ausência de duplicação.
   Definir separadamente como o backend verificará essa prova. Um checkbox,
   JSON colado pelo jogador ou recibo sem autenticação não pode liberar criação.
5. Só depois dessa validação e da conferência conjunta avaliar liberação da
   criação. Enquanto o mecanismo verificável não existir, manter
   `financeiro_concluido=False`, propriedades pendentes e os quatro indicadores falsos.

Se o produto exigir nenhuma ação adicional no Google, é necessário um contrato
novo no produtor: tornar o estado necessário acessível e verificável pelo acesso
permitido, além de redesenhar a ativação. Não basta migrar cinco chaves para uma
aba oculta: todos os leitores/escritores, cópias antigas, eventos e identidades
precisam continuar coerentes. Essa alternativa exige proposta/PR separado, sem
alterar a oficial ou ampliar acesso nesta integração.

## Aceite exigido para a próxima implementação

- Cinco chaves antigas com resíduos e uma propriedade alheia sentinela: tratar
  apenas as cinco; preservar editor/recuperações/paleta/diários e a sentinela.
- Origem, oficial, arquivo cadastrado, projeto ou responsável diferentes: recusar
  antes de qualquer escrita ou criação de acionador.
- Repetição, interrupção depois de apagar uma chave e reinício: recuperar pelo
  mesmo diário, sem limpar de novo dados já usados ou repetir lançamentos.
- Abrir após limpar: aceitar somente cache rederivado no momento previsto;
  distinguir inicialização da ativação, sem fabricar emissão/salário/histórico.
- Ativação na conta correta e teste de missão, gasto e correção: um tratamento
  por evento, sem dados herdados ou execução em nome de outro responsável.
- Identidade/autorização revogadas e relatório de cliente adulterado: nenhuma
  liberação. Validar Era, Ciclo e modelo sintético em cópias descartáveis.

Não houve novo Google/Discord, piloto, Apps Script instalado, produtor editado,
modelo pago, merge ou publicação para esta investigação.
