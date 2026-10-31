# Ensaio de ativação local · 30–31/10/2026

**Em andamento. Não é liberação da criação nem atestado para o backend.**
Uma única cópia nova, privada, na conta pessoal do mantenedor. Permissões
conferidas pelo Drive: somente proprietário, shared=false. Origem oficial
somente copiada, sem edição. Nenhum jogador, produção ou OAuth das Guias alterado.

## Código e ensaio

Bot PR84:1268e1b corrige revalidação após armar envios;86c438f importa o contrato
com três hashes de origem atualizados, mantendo todas as operações. CI final
41161538937:1.647 executados/1.646 aprovados/um opcional, zero falhas,272,967s.

Produtor PR31:49e9963 implementa instalação local;0c6c171 integra a fonte da
correção de ANALISE da main5ea10b4 e regenera o contrato (só hashes mudaram).
0fb6764 recusa conferência de propriedades incompleta,30 cenários e CI41161952426
aprovados.82b8b58 fecha a janela entre a marca/diário completo e a última
conferência de preservação;31 cenários locais aprovados, CI41163063026 em andamento.
Nenhuma dessas PRs foi mesclada/publicada nesta rodada. A integração da main
ocorreu somente na branch experimental do produtor.

QA no projeto vinculado da própria cópia. Módulo separado com financeiro,
propriedades, ativação e auxiliares limitados ao ID/operação dessa descartável.
Código salvo e relido pela UI, idêntico:primeiro37.740 caracteres, atualização39.074,
fechamento39.227. Não substituiu módulos existentes nem executou construir/continuar.
Login e autorização do Apps Script concluídos diretamente pelo mantenedor.

## Preparação observada

- Primeira chamada financeira,30/10 às23:42:46:cancelada em185,940s. Houve
  clique do assistente em Parar durante a espera de autorização e navegação
  posterior. Não certificar causa específica ou conclusão.
- Consulta às23:49:27:financeiro/propriedades incompletos,zero rotinas/registro.
- Segunda chamada financeira às23:49:47:cancelada em356,663s,coincidindo com
  sair do editor para Execuções. Não houve erro de timeout registrado.
- Consulta às23:58:27:diário financeiro presente com26 passos,não concluído,
  zero acionadores. Não recriar operação ou apagar o diário.
- Retomada às23:58:48, mantendo o editor:retornou em31/10 às00:01:09,
  fase financeiro,concluido=true,retomar=false; execução concluída às00:01:10.
- Propriedades às00:02:07:retornou às00:07:02,concluido=true,retomar=false.
  Não repetiu a limpeza financeira. As cinco propriedades passam pelo perfil
  próprio, com suas preservações e sem instalar rotinas nessa fase.

As duas interrupções coincidem com interações/navegação do assistente; isso
não demonstra timeout, problema de Google, cache ou PC. A retomada quieta
completou pelo diário. Manter o editor na execução até ela devolver resultado;
não Parar/reload/navegar durante a chamada. O ensaio financeiro REST anterior
já encerrado não foi repetido: a preparação atual é Apps Script nesta QA.

## Ativação e próximos passos

A primeira chamada qaAtivacaoInstalar foi iniciada após financeiro/propriedades
concluídos, com82b8b58 instalado/relido. Aguardar o resultado antes de repetir.
Ainda não foi comprovada a instalação das três rotinas ou um evento real.

Depois:retomar pelo mesmo diário quando indicado; conferir três UIDs,marca,
repetição terminal antes de usar a ficha e eventos reais de abertura/edição,
missão/gasto/correção. Resposta incerta de criação nunca autoriza novo create().
Não aceitar relatório local como autorização do backend. Indicadores globais falsos.

Limpeza:auxiliar QA só aceita a cópia/operação e os UIDs/handlers do próprio
diário; recusa criação incerta ou rotinas alheias. Remover apenas os recursos QA,
invalidar autorização do projeto, conferir recusa posterior sem renovar e enviar
esta cópia à lixeira recuperável. Fechar somente as abas criadas para o ensaio.
Não afirmar limpeza enquanto essa conferência não ocorrer.

Evidências e códigos privados fora do Git:
`~/.local/share/guias-ciclo/carteira-piloto/etapa7-ativacao-20261030/`.
Inclui estado-ensaio.json, código original/atual, logs de financeiro/propriedades
concluídos e diagnósticos. Não reutilizar grants de pilotos anteriores. Não há
serviço na porta8876 iniciado nesta rodada. Retomada integrada:Sol/High;
revisão do fechamento:Medium. Não alterar automaticamente configurações de modelo.
