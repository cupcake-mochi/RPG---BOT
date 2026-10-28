# Coleta de células pela API do Sheets

28/10/2026 · etapa 7 parcial, PR84. Não publicada. Criação bloqueada.
Produtor PR31 código 2427024/fechamento f36b410; sem mudança funcional nesta
rodada. Main produtor ef361cc e consumidor de42447 reconferidas.

## O que funciona no código

`carteira_viva/grade_inicializacao.py` implementa um transporte interno de
leitura pela API REST do Sheets, usando Provedores e seu Bearer Google existente.
Só GET, hosts oficiais, sem redirecionamento, escrita ou chamada Apps Script.
O método Sheets aceita o escopo drive.file; a permissão continua por arquivo
escolhido. Isso ainda não é uma execução Google autenticada comprovada.

`LeitorGradeRest(provedores, revalidar_contexto, aguardar_cota)` exige dois
callbacks confiáveis do backend. `abrir(acesso, arquivo, dominio)` aceita só
financeiro/progressao; retorna PlanoGrade privado, transitório, vinculado à
instância e ao contexto. `pagina(acesso, plano, indice)` aceita um índice inteiro
nesse plano, nunca intervalos/URLs enviados pelo navegador. Plano/dados não devem
ser serializados para clientes, banco, logs ou relatório público.

Antes de CADA GET: confere contexto, reserva cota, reconfere contexto após a
espera. Depois da resposta reconfere contexto novamente. O callback deve compor
usuário/servidor/fonte/conexão/modelo e revisões, consultando autorização real;
hash não é autenticação. O de cota deve usar Cotas compartilhada por projeto e
conta pseudonimizada. Ainda falta ligar esses callbacks ao serviço de criação:
não usar uma resposta do navegador ou um callback que só repete seu valor.

Versão Drive autenticada antes/depois do plano e de cada página deve permanecer
igual à inicial; não adota outra versão após edição. Limite total de 30 minutos
inclui cota/rede/parser. Reinício exige plano novo. Não há cursor persistido,
retentativa automática ou selo de conferência completa. Páginas podem ser
relidas; o coordenador futuro deve ordenar e confirmar cobertura separadamente.

## Cobertura delimitada

Seletores fixos conferidos contra financeiro.gs e progressao.gs do produtor
2427024: operações celulares e dependências diretas conhecidas de financeiro,
configuração do nível, curva/base de XP e painel de missões. Não é expansão
recursiva de referências de fórmulas nem auditoria do arquivo inteiro.

EXTRATO, SALÁRIOS e DADOS_SALARIOS até o fim físico, teto de 5.000 linhas por
livro. Acima disso recusa, sem truncar. Intervalos são divididos em até 4.096
células por página; uma faixa por GET Sheets. Grade/ID/título/posição e tamanho
retornados precisam corresponder ao pedido. Limites HTTP: 4 MiB por resposta,
prazo absoluto de 15 s por requisição (ou o saldo menor da rodada), sem aumentar o limite de 512 KiB dos métodos anteriores.

No máximo financeiro: 50 páginas/126.168 posições, 153 GETs contando observações
Drive e abertura. Progressão: sete páginas/1.749 posições, 24 GETs. São contagens
de transporte, não tempo medido ou capacidade garantida no Google. Nenhuma rede
é feita para interpretar fórmulas/links presentes nas células.

Cada célula conserva separadamente entrada literal/fórmula, resultado, nota e
formato numérico. Zero, falso e texto iniciado por igual permanecem distintos.
Datas ficam como serial/formato Google; não converter para Date/UTC ou comparar
com hashes Apps Script sem um adaptador explícito. Resultado omitido não é
inventado como cache: fica ausente. Vazios finais omitidos em um bloco válido
são completados; bloco ausente, deslocado ou excessivo é recusado. Erros de
fórmula/tipos desconhecidos são recusados sem expor o texto retornado.

## O que continua faltando

Esse transporte NÃO implementa o protocolo de recibos/conferência GS. Não lê
DocumentProperties/ScriptProperties; Sheets REST não fornece essas coleções.
Não confere fórmulas contra o contrato, pós-estados de fábrica, mesclas,
validações, imagens ou formato visual. Não limpa nada, não copia e não chama
qualquer executor. Os demais domínios não foram adaptados.

Próximo passo: exportar contrato determinístico do produtor para consumo no
backend, adaptar estado/recibos com persistência cifrada e vínculo de cópia,
compor autorização real e fila/cotas no serviço; validar releituras, reinício,
concorrência e Google nativo em cópia descartável. Não aumentar permissões para
contornar propriedades ausentes. `scripts.run` continua sendo uma rota separada
com requisitos próprios, não habilitada nesta tarefa.

Versão estável não congela cálculos externos. Conferência conjunta, imagens,
consistência temporal e criação continuam falsas, inclusive após ler todas as
páginas. Preservação global, orçamento nativo, automações/treinos/notas e novo
responsável pendentes. Etapas 8–10 continuam separadas. Nenhum endpoint novo.

## Testes e entrega

24 novos testes, HTTP simulado, incluem todas as 50 páginas e o último registro
físico, máscara HTTP, fórmulas/datas/zeros/vazios, fonte/grade/versão mudadas,
acesso alterado durante espera/resposta, cotas por GET, prazo absoluto de
rede/callback, cancelamento,
403/429/redirect, resposta excessiva e ausência de dados privados em repr.
95 direcionados locais passaram (24 novos + 71 existentes). CI completo em
fechamento; esperado 1.362 executados com um opcional pulado.

Pacote ignorado regenerado sem env: 90 arquivos, CRC e bytes comparados aos
fontes, sem Carteira/credenciais/bancos/campanha. SHA256:
2daf78ac11c6d619baff3bd0db64388b1869e97f45ecc7f60219741c33eeec70.
Não publicado. Nenhuma chamada Google/Discord autenticada, uso de modelo pago,
merge, deploy, acesso novo ou alteração de ficha oficial/jogador nesta rodada.
Sol Alto para integração; revisão Médio. Não alterar configurações do modelo.

## Referências

- [Sheets.get](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/get):
  ranges, máscara de campos e autorização drive.file.
- [GridData](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/sheets#GridData):
  posição e linhas do bloco.
- [CellData](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/cells#CellData):
  fórmula/entrada, resultado, nota e representação serial de datas.
