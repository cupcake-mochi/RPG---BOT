# Testes da Carteira viva

Matriz de testes futuros. A [etapa 1](ETAPA-1.md) executou 39 cenários locais
do contrato/protótipo; a [etapa 2](ETAPA-2.md) acrescentou 62 testes do banco,
retenção e recuperação. O piloto nativo da etapa 3 está descrito em NATIVO-ETAPA-3.md; os demais
ensaios desta funcionalidade continuam pendentes. As colunas abaixo indicam exigências de validação, não resultados.
A suíte histórica do bot não comprova funções ainda não implementadas.

A [etapa 3](ETAPA-3.md) acrescenta testes HTTP em loopback, OAuth com
Authlib e transporte simulado, retornos atrasados, renovação, troca/reconexão,
ponte privada e backup sem tentativas abertas. Demonstração fictícia e piloto local com provedores reais foram executados
separadamente. Cadastro, reinício, refresh, revogação e reconexão passaram no
piloto; [resultados e limites](NATIVO-ETAPA-3.md). As demais linhas da matriz
não se tornam nativas por esse ensaio. Execução: [SERVICO.md](SERVICO.md).

## Preparação

- Seguir [o plano](PLANO.md) e usar apenas personagens/planilhas fictícios.
- Ambiente isolado, banco e credenciais de teste; não substituir o bot em
  produção para ensaiar uma etapa incompleta. Definir ambiente na etapa 1.
- Duas contas Discord: responsável pelo personagem e membro sem privilégios.
  Depois testar um cargo de revisão, um cargo de edição e remoção desses cargos.
- Dois servidores sintéticos para isolamento nos testes automatizados. Para
  ensaio nativo, usar servidores autorizados; não criar outro só para cumprir
  a matriz sem autorização. Se faltar o segundo, marcar esse caso nativo pendente.
- Google: uma cópia de cada modelo oficial, uma avançada com entidades/cartões,
  uma com custom sintético aprovado, uma sem aprovação e uma incompatível.
  Incluir uma cópia sem acesso de escrita e outra sem acesso de leitura.
- Registrar valor esperado antes do teste e evidência depois. Falha pode ser
  do código, dado incompleto ou expectativa envelhecida; apurar antes de mudar teste.
- Tópico disponível informado pelo usuário:
  [Testes](https://discord.com/channels/1357866906341736488/1561410667108368575).
  Verificar sessão/conta no início. Login manual pelo usuário, sem senha/código no chat.

## Matriz obrigatória

“Local” inclui testes automatizados com respostas Google/Discord simuladas.
“Nativo” significa comportamento observado no serviço real. Um não substitui
o outro nos casos marcados nas duas colunas.

| Caso | Resultado esperado | Local | Nativo |
|---|---|---|---|
| Membro cadastra dois personagens | Dois IDs estáveis e dono correto, sem exigir admin | Sim | Sim |
| `/personagens @jogador` | Só personagens daquele dono no servidor atual | Sim | Sim |
| Pessoa tenta assumir cadastro existente | Recusa, sem transferir por conhecer link/ID | Sim | Sim |
| Google cancelado ou conta trocada | Cadastro não é concluído em nome errado | Sim | Sim |
| Retorno OAuth usado duas vezes/expirado | Recusa sem repetir vínculo | Sim | Sim |
| Arquivo acessível não selecionado para o app | Sem contornar autorização por arquivo | Sim | Sim |
| Reinício após conexão | Autorização válida reutilizada sem pedir consentimento a cada leitura | Sim | Sim |
| Revogação Google | Reconexão clara, sem token em mensagem/log | Sim | Sim |
| Cadastro igual em outro servidor | Campanha, cache privado e autorização independentes | Sim | Sim |
| Jogador consulta personagem alheio | Só apresentação permitida, sem link privado/análise | Sim | Sim |
| Cargo atual de idioma/lore | Não ganha leitura privada por herança | Sim | Sim |
| Dono/admin/cargo de revisão | Acesso privado conforme capacidade explícita | Sim | Sim |
| Revisor tenta editar | Recusa sem capacidade de edição | Sim | Sim |
| Cargo removido, usuário sai do servidor | Botão antigo e sessão web deixam de acessar dados privados | Sim | Sim |
| ID de personagem ou servidor adulterado | Nenhum dado de outro contexto é retornado | Sim | Sim |
| Cache/página web pública | Não contém dados privados escondidos no HTML/JSON | Sim | Sim |
| Primeira leitura simples | Mesmo resultado mecânico do leitor existente | Sim | Sim |
| Avançada, Ritual, custom e entidades | Paridade com motor atual; sem falsa aprovação | Sim | Sim |
| Campo ausente, zero e vazio | Distinção preservada, sem completar dado por suposição | Sim | Sim |
| Leitura durante salvamento de cartão | Espera limitada ou aviso, sem certificar estado parcial | Sim | Sim |
| Cliques repetidos e páginas da galeria | Uma leitura em andamento por vínculo; lista usa resumos | Sim | Sim |
| `429`, erro Google e timeout | Fila limitada e mensagem útil; bot continua atendendo | Sim | Só falha controlada, sem forçar quota real |
| Troca válida de arquivo | Mesmo personagem/cartão, nova fonte, análise reavaliada | Sim | Sim |
| Troca inválida/cancelada | Fonte anterior preservada | Sim | Sim |
| Troca durante leitura/edição antiga | Resultado antigo não sobrescreve vínculo novo | Sim | Sim |
| Aprovação de fonte anterior | Não aparece como aprovação da nova ficha | Sim | Sim |
| Desvincular um de vários personagens | Não apaga arquivo nem revoga os outros sem explicação | Sim | Sim |
| Apagar cadastro/desconectar conta | Exclusão/retenção conforme política; sem remover arquivo Google | Sim | Sim |
| Personalizar título/frase/cor/imagem | Prévia clara, limites, sem menções inesperadas | Sim | Sim |
| URL maliciosa, arquivo grande ou falso | Recusa sem baixar rede interna nem exceder limites | Sim | Cópias benignas |
| Imagem removida/expirada | Apresentação continua legível; substituição possível | Sim | Sim |
| Modelo do servidor | Só gestão autorizada; cópia nova sem histórico/emissão herdados | Sim | Sim |
| Modelo trocado ou incompatível | Fichas antigas intactas; erro explicativo na nova cópia | Sim | Sim |
| Cópia com scripts/rotinas | Inicialização e comportamento nativo comprovados | Parcial | Obrigatório |
| Edição autorizada | Só campos/efeitos do contrato, confirmação e releitura | Sim | Obrigatório |
| Edição repetida/timeout/reinício | Não duplica ganho ou lançamento; resultado incerto apurado | Sim | Obrigatório |
| Edição simultânea pelo jogador | Conflito não sobrescreve mudança silenciosamente | Sim | Obrigatório |
| Migração e restauração | Cadastros, vínculos e demais bancos preservados | Sim | Ambiente de teste |
| PT/EN, celular, teclado e contraste | Nomes curtos, ações claras, sem depender só da cor | Parcial | Sim |

Não provocar erros destrutivos ou exaurir cotas do serviço real. Cenários de
falha usam simulação local/proxy controlado em ambiente de teste sempre que
possível. Botão de edição só aparece quando a operação estiver implementada
e autorizada; se estiver fora do escopo, registrar como indisponível.

## Carga sem prejudicar o bot

1. Gerar 100, 500 e 1.000 cadastros sintéticos, variando fichas simples,
   avançadas e valores de tamanho máximo permitido. Separar cadastro de
   leitura simultânea. Não criar mil planilhas Google para esse ensaio.
2. Medir banco/cache/imagens separadamente, memória máxima, CPU, tempo de
   resposta p50/p95, espera em fila, erros e leituras evitadas pelo cache.
3. Simular rajadas de 1, 5, 20 e 100 consultas, inclusive todas ao mesmo
   personagem e consultas distribuídas entre servidores. São simulações,
   não 100 chamadas Google disparadas contra produção.
4. Misturar navegação da galeria e comandos usuais do bot. Confirmar que
   tarefas de leitura não bloqueiam o processamento de eventos do Discord.
5. Conferir cotas efetivas do projeto. Os padrões Sheets consultados são
   300 leituras/minuto/projeto e 60/usuário/projeto, com cotas próprias de
   escrita. OAuth de jogadores distribui a cota por usuário, não remove a
   cota global. Drive e outras APIs têm limites próprios.
6. Definir antes do ensaio o orçamento real de RAM/disco e limites da fila.
   Meta inicial de resposta do backend para galeria em cache: p95 até 2 s;
   medir rede/renderização Discord separadamente. Leitura Google tem prazo
   limitado e resposta inicial de processamento, não promessa de 2 s.
7. Critério: sem vazamento, perda de dados, duplicação de escrita, crescimento
   sem limite ou bloqueio do bot. Reservar margem de memória para conversas
   e funcionalidades existentes; se não couber, reduzir concorrência/cache
   ou propor infraestrutura antes de publicar. Registrar limite comprovado.

Não anunciar “suporta 1.000 personagens” apenas por carregar 1.000 linhas no
SQLite. Não medir custo do banco como se todas as fichas fossem vazias nem
extrapolar um teste no computador para a Discloud sem validar recursos.

## Ordem dos ensaios reais

Fazer sessões curtas, com resultado salvo ao fim de cada bloco:

1. **Acesso:** conectar, cancelar, reconectar e perder permissão.
2. **Cadastro e privacidade:** dois personagens, duas contas, galeria,
   permissões e troca de arquivo; o original permanece intacto.
3. **Análise:** cópias simples, avançada e custom, com resultados esperados.
4. **Carteira e cartão:** celular/desktop, imagens, PT/EN, área privada.
5. **Modelos e escrita:** apenas depois dos contratos; verificar efeitos
   nativos e comparar valores antes/depois em cópias descartáveis.
6. **Publicação autorizada:** backup, migração, arquivos instalados, dados
   preservados e um ensaio curto dos principais fluxos.

Os blocos usam comandos determinísticos, sem chamar a conversa das guias.
Se for necessário testar respostas do modelo, pedir nova autorização de
quantidade e custo; aprovações de outras rodadas não são reutilizadas.

## Registro e encerramento

Para cada caso, registrar: etapa, SHA, versão da ficha, local/nativo,
identificador fictício, resultado esperado/obtido, evidência e pendência.
Não salvar tokens, emails reais, conteúdo de jogadores ou URLs privadas em
relatórios públicos. Capturas devem estar livres desses dados.

Executar regressões focadas em cada alteração. Rodar a suíte completa com
núcleo presente antes da entrega integrada:

```bash
cd Closure/src
../.venv/bin/python -m unittest discover -s testes
```

Antes da Carteira, o registro histórico era de 976 testes, 975 aprovados e um opcional
pulado. Os relatórios das etapas registram os totais posteriores; não usar o número antigo como
resultado novo ou meta artificial. Não repetir suíte extensa por edição de docs.

Ao fim, mandar cópias descartáveis à lixeira, remover concessões de teste
e apagar dados sintéticos conforme o roteiro. Preservar as oficiais, fichas
de jogadores e credenciais de produção. Exclusão permanente de servidor
não é necessária para validar a funcionalidade.

## Acréscimos da etapa 4

Os testes `test_carteira_leitura`, `test_carteira_consultas`,
`test_carteira_consultas_web` e `test_carteira_fila` cobrem leitura autenticada
simulada, paridade de normalização CSV/XLSX, paridade com o motor, fontes e
autorizações substituídas durante o pedido, campanha/motor alterados, fila,
cache, limites, cancelamento, renovação e rotas internas privadas. Banco e
motor são reais; respostas Google/Discord são fictícias.

Executar com as dependências do bot e da Carteira e núcleo preparado:

```sh
# Em Closure/src
../.venv/bin/python -m unittest testes.test_carteira_leitura testes.test_carteira_consultas testes.test_carteira_consultas_web testes.test_carteira_fila
```

Para HTTP/threading, usar ambiente que permita loopback e o mecanismo interno
de despertar o event loop. A execução restrita no computador não entregou o
retorno da thread no setup; essa tentativa foi encerrada e a suíte executada
com essas permissões locais, sem rede externa. Isso não é defeito do Google.

O piloto nativo básico da etapa 4 passou: leitura completa e paridade integral
com XLSX, cache, análise e abertura salva, seguidos de limpeza/revogação.
Ritual e entidade também passaram na paridade offline; a matriz nativa avançada
e a interação privada no Discord continuam pendentes.
O arquivo da etapa 3 está na lixeira e seu grant foi revogado; não reutilizar
esse registro antigo como se a autorização ainda estivesse ativa.

O piloto mostrou que fórmulas completas excediam a resposta de 16 MiB. A API
agora fornece só valores/erros efetivos, sem ampliar esse teto. Vazio calculado
omitido no Google é preservado como vazio; a recusa de XLSX sem cache ganhou
regressão explícita. O teste de saúde proíbe adquirir o semáforo, em vez de
depender de um segundo de agendamento da máquina. Resultados detalhados e
ressalvas locais: NATIVO-ETAPA-4.md.

## Resultado da etapa 5

[ETAPA-5.md](ETAPA-5.md) registra 62 testes novos e a distinção entre suíte e
piloto. Suíte local de 1.237 passou com um opcional pulado; 25 testes finais
da interface/ponte passaram, incluindo as cinco regressões novas que aumentam a coleta para
1.242. Conferir o CI final para a execução única do total. Não repetir a suíte
extensa apenas por documentação.

Discord real, duas contas e fichas fictícias: galeria própria/alheia/vazia,
paginação, PT/EN, edição com prévia, salvamento e consulta privada passaram.
A análise direta da conta sem cargo foi recusada. Google foi simulado nesta
rodada; a leitura nativa da etapa 4 continua sendo uma prova separada.
Ainda faltam troca/reconexão pelos novos botões, cargo revisor concedido/removido
no Discord real, publicação HTTPS e bateria nativa avançada de ficha. Não
considerar essas linhas da matriz concluídas pelos testes automatizados.

Fechamento: busca de nomes corrigida retestada no Discord e anexo WebP exibido.
Upload/confirmação da imagem foram pela API interna; o formulário de anexo do
comando ainda é pendência nativa. Piloto encerrado e dados fictícios removidos;
produção retomada. Os detalhes operacionais estão em ETAPA-5.md.

CI final do código `ced4d52`: 1.242 executados, 1.241 aprovados, um opcional,
zero falhas (run 40395109029). Reteste local de cota/HTTP: 33/34; um upload
válido retornou 400. Caso isolado repetido passou, sem mudar expectativa ou
limite; worker levou 19,153 s de 20 s disponíveis. Causa provável de I/O, não
comprovada pelo erro anterior. Essa ocorrência está detalhada em ETAPA-5.md.

## Resultado da etapa 6

Carteira web na PR 83, dependente da 82. [ETAPA-6.md](ETAPA-6.md) registra
40 regressões novas e os ensaios visuais. Conjunto direcionado final: 60/60.
CI final do código 0c9a15f: 1.282 executados, 1.281 aprovados, um opcional, zero
falhas, 261,589 s (run 40423286577). A demonstração no navegador usa identidades
fictícias e não valida Google real. O login Discord real, cartão, análise e página 2 passaram com uma conta real
e ficha fictícia; logout entre abas também. Três personagens/conexão removidos
e serviço encerrado, sem mexer na produção. A última guarda (`0c9a15f`) encerra
sessões na exclusão global de dados: regressão reproduzida e 18/18 de sessões
passaram. Esse caso está incluído no CI completo final de 1.282.

Passaram na demonstração: responsável/comum, cartão alheio básico sem privado,
logout limpando DOM/link, PT/EN, idioma através do callback, detalhes e análise
paginada, foco de teclado e 390×844 sem rolagem horizontal. Dados/provedores
fictícios não comprovam cópias oficiais, performance de produção, celular físico
ou revogação nativa de cargo durante uma consulta.

Continuam na matriz externa: Google + Carteira web + nova ponte combinados,
reconexão/troca pelos botões, cargo revisor concedido/removido no Discord real,
saída/retorno durante espera, imagem pelo formulário do comando, HTTPS público,
capacidade/429 e recuperação no host final. Essas pendências permanecem abertas
mesmo com a suíte verde. Não repetir pilotos básicos por rotina nem transformar
um teste de provedor fictício em validação nativa.
