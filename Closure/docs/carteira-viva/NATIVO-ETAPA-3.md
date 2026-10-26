# Piloto da conexão de fichas

26/10/2026 · etapa 3 · código em `codex/carteira-viva-etapa-3`, PR 80.
Ensaio local com provedores reais, distinto da demonstração fictícia.
Sem merge ou publicação na Discloud.

## Configuração usada

O usuário criou a conta Google dedicada das Guias e escolheu seu endereço
como suporte público. Aceitou os termos Cloud e a política de dados das APIs
diretamente no navegador e autorizou a criação/configuração do projeto próprio
`guias-ciclo-fichas` (número `1015676492327`). Não foi ativado faturamento.

- OAuth Google: Guias do Ciclo — Fichas, Externo/Testando, duas contas de teste
  autorizadas (mantenedor e conta dedicada); único escopo `drive.file`.
- Cliente web: Carteira de personagens — Piloto local. Origem JavaScript
  `http://127.0.0.1:8876`; retorno `/oauth/google/retorno` nessa origem.
- Drive, Sheets e Picker ativados. Chave Google Picker — Piloto local com uma
  API (Picker) e referenciadores `http://127.0.0.1:8876/*` e
  `https://docs.google.com/*`. Restrições preservadas durante o teste.
- Por escolha do usuário, Discord usa as **Guias oficiais**, não outro app.
  O retorno `/oauth/discord/retorno` local foi salvo e o próprio usuário
  redefiniu o segredo OAuth. O token do bot não foi redefinido.
- O token existente das Guias foi usado só em REST para conferir membros e
  cargos no servidor autorizado. Nenhum segundo bot/Gateway foi iniciado.
- Banco próprio no diretório privado do usuário, com cifra e chave separada.
  Serviço em loopback. Entrada controlada autenticada por segredo local,
  ainda sem comando instalado no Discord.

Credenciais não estão no Git. Os arquivos locais privados foram conferidos
com permissão 600 e diretório 700. O disco externo ignora essas permissões;
não manter credenciais em texto nele. O download do JSON pelo painel não
concluiu; a credencial foi preservada da tela de criação sem copiar seu valor
para o chat. Durante a leitura da configuração existente da Discloud, uma
linha de outro serviço apareceu numa saída de ferramenta por erro de filtro;
a leitura foi limitada ao token necessário e o arquivo foi fechado sem salvar.
Nenhuma configuração completa ou valor de segredo foi incorporado à PR.

## Defeitos encontrados e corrigidos

1. **URL sem identificador do app.** O construtor do núcleo Authlib recebe
   `session` antes de `client_id`; o argumento posicional produzia
   `client_id=None`. Regressão falhou antes e passou após informar
   `OAuth2Client(None, client_id=...)`. Conferência para Google e Discord.
2. **Escopo Discord herdado da instalação.** O retorno real trouxe
   `identify applications.commands`, embora o login pedisse só identify.
   Aceita-se somente identify, opcionalmente acompanhado desse escopo de
   comandos já concedido. Extras como email, guilds, bot e connections
   continuam recusados; Google mantém o escopo único exato. Não se solicita
   nem usa applications.commands nesse login.
3. **Chave restrita do Picker recusada.** `no-referrer` ocultava a origem
   necessária à validação. `strict-origin` no cabeçalho e na página envia
   apenas a origem, sem caminho/query. O Picker passou a carregar mantendo
   as mesmas restrições da chave.
4. **Lista de arquivos sem altura.** O SDK injeta uma pequena folha de estilo,
   bloqueada pela CSP. Regras equivalentes de layout ficam no CSS local;
   `style-src 'self'` e o bloqueio de unsafe-inline permanecem. A lista passou
   a ser visível e selecionável.

Também foi acrescentado diagnóstico por códigos/nomes reconhecidos. Mensagens
arbitrárias, código de autorização, descrição do provedor e tokens não entram
nos logs. Regressão confere essa ausência. O SDK Google passa o access token
na URL interna do iframe; não publicar/exportar essa URL em observações do
navegador. O aplicativo não grava tokens em storage ou URLs próprias.

## Resultados nativos

| Ensaio | Resultado |
|---|---|
| Participação atual na API Discord | Confirmada antes de emitir a entrada |
| OAuth Discord com PKCE/estado e mesma conta | Passou após as correções |
| OAuth Google com conta de teste e drive.file | Passou |
| Picker real com chave restrita | Carregou após os ajustes de origem/layout |
| Escolha de arquivo | Somente a cópia privada descartável criada nesta rodada |
| Metadados e leitura `ANALISE!A1:D32` | Arquivo autorizado, formato e nome identificados |
| Confirmação | Um personagem fictício cadastrado; autorização durável cifrada |
| Reinício | Personagem, arquivo e conexão preservados |
| Reutilização da conexão | Refresh real e releitura sem novo consentimento Google |
| Revogação Google real | HTTP 200 no endpoint oficial |
| Tentativa depois da revogação | Invalid grant tratado; segredo removido, estado revogada; personagem mantido; serviço online |
| Reconexão após revogação | Nova autorização, releitura e confirmação do mesmo personagem/arquivo |
| Limpeza | Autorização de teste revogada, cadastro fictício removido e banco íntegro |

O cadastro se chama QA Carteira — descartável. A planilha era uma cópia da
oficial Ciclo Maldito, denominada QA Carteira — OAuth e Picker — DESCARTÁVEL —
26-10-2026, com compartilhamento privado confirmado por metadados. Foi movida
para a **lixeira recuperável** ao fim. Oficial e fichas de jogadores não foram
editadas. Não foi criada nova aplicação Discord, nem reiniciada a Discloud.

Evidências locais fora do Git:
`/tmp/carteira-etapa3-nativo-sucesso.png` e
`/tmp/carteira-etapa3-nativo-recuperado.png`. Não incluem códigos OAuth ou
valores de credenciais. Não usar screenshots das telas de segredo ou URLs
internas do iframe em relatórios públicos.

## Testes e limites

152 testes distintos da Carteira aprovados após as correções. Suíte completa
posterior: 1.128 executados, 1.127 aprovados, um online opcional pulado e zero
falhas, em 722,911 segundos. As mensagens de
modelos/custos dos testes são simuladas; nenhuma chamada paga foi realizada.

O piloto prova conexão e leitura pequena de identificação, **não análise
mecânica completa**, recálculo da ficha ou aprovação. Não altera células.
Entrada ainda é controlada, sem `/personagem` instalado no bot. O ensaio de
troca entre dois arquivos distintos continua coberto offline, mas não foi
executado no Google real nesta rodada, cuja autorização era para uma cópia.
Conta errada, callbacks atrasados, concorrência e rollback foram simulados;
não declarar todos esses casos como nativos. Tela pequena foi conferida na
demo; celular físico, comandos privados e cargos reais ficam para as próximas
etapas. Não existe origem web pública ou carteira para outros computadores.

A próxima etapa é leitura completa sob demanda e análise privada, com campanha
e aprovações do servidor. Modelo recomendado: GPT-6.1 Sol · Alto. Manter
separados código da PR, configuração externa, piloto local e publicação.

## Referências

- [Google Picker web](https://developers.google.com/workspace/drive/picker/guides/web-picker): projeto, chave, origens e integração.
- [OAuth Discord](https://docs.discord.com/developers/topics/oauth2): identificação e troca de código.
- [OAuth web Google](https://developers.google.com/identity/protocols/oauth2/web-server): autorização e renovação.
