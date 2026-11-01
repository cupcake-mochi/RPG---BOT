# Próximo ensaio: preparo e eventos reais

## Avanço local em 01/11

Os READMEs da main foram atualizados na PR88 para a publicação R60/v0.369,
runtime229e539, mantendo a análise R53. Não houve novo deploy.

Na PR31 do produtor, código `a085a9f`, a primeira chamada de ativação pode
terminar após a preparação quando ela já consumiu180.000ms. Salva o diário,
retorna zero rotinas/retomar=true e não inicia create(). A próxima chamada
reconfere preservação, contexto e rotinas antes de criar. Não repete a
preparação das propriedades nem remove verificações de segurança. Se o preparo
ficar abaixo do orçamento, mantém o caminho anterior.

O ensaio anterior tinha338s na primeira instalação; isso motivou separar o
preparo longo da criação. Não foi demonstrada uma causa de latência nem ganho
real. O ponto de pausa não interrompe uma leitura em andamento, não garante
tempo máximo e não reduz o trabalho total. O protocolo/contrato REST e os
indicadores de liberação continuam iguais.

Passaram localmente35 cenários de ativação,101 financeiros,46 de propriedades
e47 REST. Quatro cenários novos cobrem orçamento/fronteira, retomada com
funções recarregadas, edição concorrente e rotina desconhecida. A prova nativa
e o CI completo deste commit têm evidência separada.

Fonte e implementação: [PR31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31)
e [contrato de ativação](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/codex/inicializacao-financeira-carteira/r53/inicializacao/ATIVACAO-2026-10-30.md).

## Roteiro curto, em nova descartável

1. Conferir o CI do código a ser instalado. Criar nova cópia privada, pertencente
   à conta executante, e registrar origem, operação e versão. Não restaurar a QA
   encerrada em31/10. Manter código/IDs/contexto e logs completos fora do Git.
2. Usar o mesmo kit restrito à cópia/operação, com o módulo atualizado e código
   salvo/relido. Confirmar ausência de rotinas e preparar financeiro/propriedades
   pelo diário. Se retornar retomar=true, continuar a mesma operação.
3. Executar a ativação uma chamada por vez, mantendo o editor até o retorno.
   Registrar início/fim e resultado de cada chamada, inclusive a eventual pausa
   com zero rotinas. Uma resposta incerta de criação nunca autoriza repetir
   create(). Conferir três UIDs, marca e repetição terminal sem duplicação.
4. Abrir/reabrir a própria ficha e observar uma execução real do wrapper de
   abertura. Fazer uma edição real pela interface e observar UID/fonte e execução
   do wrapper de edição. Chamar handlers manualmente ou escrever pela API não
   comprova esses eventos. Não certificar o relógio diário sem observar disparo.
5. Registrar o saldo inicial W86 e linhas de EXTRATO. Digitar uma única vez
   -500 na caixa ±GASTO/GANHO; aguardar o processamento e confirmar caixa limpa,
   uma única linha no extrato e saldo anterior menos500. Reabrir/atualizar e
   confirmar que o lançamento não duplicou. Se o efeito ficar incerto, investigar
   antes de digitar novamente.
6. Registrar uma missão sintética pela interface, com data válida segundo o fuso
   da ficha. Confirmar que entrou uma vez. Corrigir pelo nome em BI11 e pela data
   real em BO11; conferir o aviso, a data armazenada e ausência de nova missão ou
   duplicação de crédito. Usar nome exclusivo e datas aceitas pelo contrato atual,
   sem alterar relógio, regra, saldo ou emissão para forçar um resultado.
7. Conferir preservações e registrar cada caso como aprovado/falhou/não executado.
   Remover somente rotinas/recursos registrados no diário QA, confirmar zero
   restantes, invalidar a autorização e conferir recusa sem renovar. Mover a
   descartável à lixeira recuperável e fechar apenas abas do ensaio.

O kit do ensaio anterior não está presente neste ambiente de nuvem. Antes de
executar, reconstruir seu invólucro restrito a partir dos contratos versionados;
não reutilizar IDs, grants ou código privado de outra máquina por suposição.
Conferir os campos de missão atuais antes de preencher. A lista acima é um
roteiro, não um registro de execução ou aprovação.

## Dependências e bloqueios restantes

Este ambiente não tem navegador conectado ou identidade Apps Script pronta.
O login/consentimento e o ensaio dos eventos precisam de uma sessão Google
autorizada com acesso ao editor. Nenhuma nova QA ou acionador foi criado.

Instalação local ainda não atesta identidade/ativação ao backend. Concorrência
entre observação e escrita, demais domínios, preservação integral e prova dos
modelos Era/Ciclo/servidor continuam pendentes. Criação bloqueada, etapa7
parcial,8–10 pendentes; PR31/84 experimentais sem merge ou deploy.

Modelo recomendado: Sol/High para execução integrada; Astra/High para desenho
do vínculo verificável/concorrência; Medium para revisar o fechamento.
