# Atestado de ativação por pulso · 02/11

Contrato e classificador offline. **Não lê o Google, não altera o produtor e
não libera criação**; `criacaoDisponivel` e os demais indicadores seguem falsos.

## Problema e escopo da prova

As rotinas instaláveis rodam como quem as criou e uma conta não enxerga as de
outra. O bot só tem `drive.file`. Checkbox, JSON colado ou relatório local não
provam a ativação. O dono controla células, propriedades e o código das
rotinas, então nenhum sinal da planilha prova algo contra um dono que queira
enganar o bot; como o bot já confia nos valores da ficha, um atestado mais
forte que esses dados não protege nada.

**Decisão do mantenedor (02/11):** o atestado protege contra instalação falha
(rotina incompleta, duplicada, autorização revogada, cópia trocada, gatilho que
nunca disparou), não contra trapaça do dono.

## Pulso

Cada rotina grava, ao concluir uma execução real, um registro com:
`rotina` (`instalacao`, `diario`, `edicao`, `abertura`), `operacao`, `arquivo`,
`sequencia` (por rotina, só cresce) e `quando`. O local de gravação é decisão
do produtor (PR31 da ficha): preferência por metadados de desenvolvedor, a
confirmar se a leitura aceita `drive.file`; senão, faixa em aba oculta lida
pelo leitor REST já provado. O bot nunca escreve nessa área.

## Estados (`carteira_viva/atestado_ativacao.py`)

| Estado | Condição |
|---|---|
| `nao_ativada` | Nenhum pulso |
| `aguardando` | Faltam `diario`, `abertura` ou `edicao`; o motivo diz o que o jogador precisa fazer |
| `ativa` | As três rotinas vistas, `diario` com menos de 26 h |
| `parada` | Último `diario` com mais de 26 h, ou nenhum `diario` 26 h depois do primeiro pulso |
| `inconsistente` | Outra operação/planilha, sequência repetida, contador voltando desde a última leitura, ordem de sequência contra os horários, ou horário no futuro |

**Decisões do mantenedor (02/11):** a ficha só fica `ativa` depois do primeiro
disparo real do `diario` (3h), sem execução imediata na ativação; o jogador é
orientado a abrir e editar a ficha uma vez depois de ativar, porque escrita por
API não dispara eventos de edição.

## Alternativa descartada

`processes.listScriptProcesses` da API do Apps Script lista execuções por tipo
(`TIME_DRIVEN`, `TRIGGER`…), mas exige escopo novo, o ID do projeto de cada
cópia, e não prova mais que o pulso contra o dono. Não seguir sem desenho
separado.

## Testes

`testes/test_carteira_atestado.py`: sete casos (sem pulso; só instalação;
três rotinas, inclusive com leitura anterior; outra operação/planilha;
sequência repetida/fora de ordem/voltando; diário antigo e diário que nunca
rodou; pulso malformado ou no futuro). A garantia de que o bot não escreve na
área do pulso depende do local escolhido pelo produtor e entra junto com o
leitor. Bateria local da Carteira: 680 testes aprovados.

## Falta

Produtor: gravar o pulso só depois de concluir o trabalho de cada rotina (PR31).
Bot: leitor do local escolhido, guardar `Atestado.maximos` por ficha, mostrar o
estado e o motivo na interface. Depois, prova nativa com a sessão Google do
mantenedor numa descartável nova.
