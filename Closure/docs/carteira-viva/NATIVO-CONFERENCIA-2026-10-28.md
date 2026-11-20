# Conferência real pelo OAuth das Guias

28/10/2026 · etapa 7 parcial, PR84 em rascunho. **Sem publicação.**
Código ensaiado: `45c03c877a85b31303ebc3d9bcd44a71457c2d2f`.
Este fechamento acrescenta documentação; não altera código, contrato ou pacote.

## Ensaio

Uma cópia privada e descartável do modelo público Ciclo Maldito foi criada
pelo Drive conectado. Somente a cópia foi selecionada no Google Picker do
**OAuth próprio das Guias**, após login Discord e consentimento Google reais.
O usuário concluiu a autenticação de dois fatores e autorizou `drive.file`
para esse ensaio. Nenhum outro arquivo foi selecionado ou compartilhado.

O serviço local, acessível apenas no loopback, cadastrou um personagem fictício
vinculado à cópia. Um executor privado chamou o método interno
`Consultas.conferir_inicializacao` com os provedores HTTP, worker SQLite,
fila, cotas e renovação reais. Não foi criado endpoint ou comando público.
A cópia veio do conector; as leituras da conferência abaixo usaram a concessão
Google das Guias. Não confundir essa preparação com implementação de cópia
ou inicialização automática no produto.

Nenhuma célula foi alterada, nenhum Apps Script foi executado e nenhum
acionador foi instalado. Oficiais e fichas de jogadores ficaram intactas.
Não houve Gateway Discord adicional, chamada a modelo, merge ou deploy.
Não foram ampliados escopos, intents ou serviços do projeto Google.

## Leitura completa

Tempo observado: **247,349 segundos**. Dois domínios concluídos e persistidos:

| Domínio | Páginas | Erros de pós-inicialização | Pendências |
|---|---:|---:|---:|
| Financeiro | 25 | 11 | 0 |
| Progressão | 8 | 0 | 0 |

As 13 guardas de fórmulas financeiras não apontaram divergência. Os 11 achados
financeiros foram dois sinais em `DADOS_SALARIOS!L2` (`entrada_divergente` e
`resultado_divergente`) e nove posições com `conteudo_residual` em
`EXTRATO!A2:C4`. Não são onze registros financeiros distintos.

Isso confirma a barreira esperada: uma cópia bruta do modelo herda estado e
histórico, portanto não pode ser entregue como personagem recém-inicializado.
A conferência é de pós-inicialização; esses achados não significam que uma
ficha de jogador com histórico legítimo esteja irregular na análise comum.
Nenhum valor do histórico ou dado pessoal é necessário neste relatório.

Os quatro indicadores permaneceram falsos: `criacao_disponivel`,
`conferencia_conjunta_concluida`, `consistencia_temporal_verificada` e
`imagens_atuais_conferidas`. Dois domínios lidos não liberam criação.

Requisições instrumentadas **somente durante a conferência**:

| Destino | Método | Quantidade |
|---|---|---:|
| Discord: membro atual | GET | 337 |
| Discord: servidor | GET | 8 |
| Discord: definições de cargos | GET | 8 |
| Google: renovação OAuth | POST | 1 |
| Google: Drive/metadados/versão | GET | 73 |
| Google: Sheets | GET | 35 |

São 353 GETs Discord, 108 GETs Google e um POST OAuth: **462 respostas HTTP 200**.
Não houve 429 observado. A fase anterior de conexão teve 44 respostas HTTP 200,
contadas separadamente; o tráfego do navegador/Picker não entra nesses totais.
A instrumentação reteve apenas categoria, método, fase e status, sem URLs com
parâmetros, cabeçalhos, tokens ou corpos HTTP.

Essa cópia tem menos linhas físicas financeiras que o cenário simulado máximo
(25 páginas contra 50). Não comparar seus 108 GETs Google aos 183 da simulação
como se fosse redução de custo no mesmo arquivo. Tampouco é teste de capacidade
para vários jogadores: só houve um iniciador e uma operação por vez.

## Reinício e retomada

Com a porta local liberada e os dois bancos SQLite íntegros, o piloto foi
reiniciado usando o mesmo banco/chave. Não houve novo consentimento ou seleção
no Google. A retomada reabriu os dois resultados em **8,551 segundos**:

- 19 GETs Discord (nove de membro, cinco de servidor e cinco de cargos);
- um POST OAuth para renovar a autorização já cifrada;
- um GET Drive para conferir a versão do arquivo;
- **zero GETs Sheets**: os domínios completos não foram relidos.

As 21 respostas da retomada foram HTTP 200. A inicialização desse segundo
processo teve outras seis respostas Discord, contadas à parte. O prazo original
do registro e o contexto continuaram valendo. O ensaio comprova reabertura de
um resultado completo após reinício, não interrupção no meio de uma página.

## Revogação e limpeza

Ao encerrar, a concessão Google usada no piloto foi revogada: HTTP 200 no
endpoint oficial. Revogar uma concessão atinge o acesso dessa conta ao projeto,
não apenas o arquivo escolhido. As três bases antigas do piloto haviam sido
conferidas em modo somente leitura: nenhuma mantinha concessão ativa desse
cliente. Nenhum segredo/token do bot Discord foi alterado.

A tentativa seguinte de retomar recebeu HTTP 400 na renovação Google e o
provedor retornou `revogada`. Houve nove GETs Discord nessa tentativa e **nenhum
GET Drive/Sheets**. O serviço marcou a conexão revogada, apagou seu segredo
cifrado e descartou o trabalho persistido, sem reapresentar resultado antigo.
O personagem fictício foi excluído pelo método autorizado do cadastro.

Conferência final da base exclusiva do ensaio: zero personagens, zero conexões
ativas, zero segredos de conexão e zero conferências persistidas;
`integrity_check = ok`. Isso não afirma que todo registro mínimo de auditoria
ou de remoção foi apagado. O serviço foi encerrado e a porta 8876 ficou livre.
A cópia descartável foi movida à lixeira recuperável pelo Drive; a interface
confirmou a ação. A aba criada para limpeza foi fechada.

Configuração privada do piloto e evidências locais ficam fora do Git. Nenhum
banco, credencial, cadastro real, identificador de usuário ou URL transitória
OAuth/Picker foi adicionado ao repositório ou ao pacote.

## O que permanece pendente

- O caminho nativo medido é o **dono da ficha**. Revisor por cargo explícito,
  Administrator/dono de servidor por prerrogativa, perda de cargo durante rede,
  429 e cancelamento no meio do domínio têm regressões offline, mas não foram
  exercitados com contas reais nesta rodada.
- Cópia e diário de escrita REST com reconciliação ainda não existem no produto.
  Não adicionar chamada de escrita ao auditor ou usar seu recibo para liberá-la.
- Propriedades Apps Script, demais domínios, preservação global/arte,
  automações/treinos/notas/novo responsável e consistência temporal dos cálculos
  ainda impedem fechar a inicialização. Um contrato de leitura não atesta esses
  pontos nem demonstra que toda atualização do produtor está na cópia.
- A latência nativa completa ainda é de minutos. Preservar os prazos comuns das
  consultas e a revalidação de acesso; medir mudanças em cenários equivalentes.

Próximo trabalho de código: projetar e implementar cópia/diário de escrita no
backend REST, com ações limitadas ao contrato e reconciliação após interrupção,
sem liberar `criar_por_modelo`. Depois validar preservação e domínios restantes
em novas cópias descartáveis. Manter a etapa 7 parcial e as etapas 8–10 na fila.

## Git e validação

Main remota reconferida: bot `de424478a7a120ecb43bd0c79eb93774d446fae6`;
produtor `ef361ccdf7a0210781176e3c42d318cde147553d`. PR31 do produtor intacta.
A PR84 continua dependente da etapa 6/PR83, em rascunho, sem merge/deploy.

O [CI 40762548326](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40762548326)
do código ensaiado passou em 28/10 às 17:27:25 Brasília: **1.457 executados,
1.456 aprovados e um opcional pulado**, zero falhas, 334,900 s. Não somar esta
prova nativa como testes unittest novos. Nenhum código mudou nesta rodada:
não repetir a suíte completa ou regenerar/publicar ZIP por documentação.

Continuar em `codex/carteira-viva-etapa-7`, lendo o topo de `FILA-ATUAL.txt`,
`RETOMADA.md`, este relatório e `INICIALIZACAO-PRODUTOR.md`. Modelo/esforço
recomendados: **Sol Alto** para implementação; **Médio** para revisão documental.
