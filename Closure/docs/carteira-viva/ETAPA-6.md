# Carteira no navegador

Etapa 6 · 26/10/2026. Branch `codex/carteira-viva-etapa-6`, base `52ca144`
da etapa 5/PR 82. Implementação em validação; **não publicada**. PRs dependentes
77–82 não foram mescladas. O bot em produção permanece separado.

## Uso

O título do cartão da ponte opcional abre `/carteira/servidor/personagem`.
A pessoa entra com Discord e precisa participar daquele servidor. O link
sozinho não dá acesso. “Público” significa outros membros do servidor, sem
indexação global. A galeria mostra até 20 opções por página, o responsável,
a apresentação permitida e o horário da leitura. Abrir um cartão próprio ou
como revisor permite atualização sob demanda; a lista não lê todas as fichas.

Detalhes e análise têm área privada, com as mesmas capacidades do Discord.
A análise reaproveita o motor e o apresentador existentes, inclusive as cores
locais de erro/pendência. O navegador recebe só a página solicitada da análise,
sem o snapshot completo. Navegar revalida cargos, fonte, leitura e campanha;
não é uma troca local entre páginas privadas já guardadas no HTML.

A imagem é baixada de rota autenticada do mesmo serviço, com autorização
atual. O arquivo continua cifrado fora do SQL; não há URL pública de mídia nem
parâmetro para buscar uma prévia privada. URL Google aparece só após consulta
privada autorizada e o próprio Google continua verificando seu acesso.

Textos PT/EN, controle de idioma apenas da página, foco de teclado, estados de
carregamento e tela pequena. Troca de arquivo/apresentação permanece no Discord;
esta entrega é de leitura. Nenhuma célula é escrita e nenhuma análise aprova a
ficha por si só. Valores livres são texto, sem HTML arbitrário ou links vindos
do perfil. Botão Encerrar sessão continua disponível durante uma consulta.

## Sessão

- OAuth Discord identify, Authlib/PKCE e o mesmo retorno já configurado.
  O dispatcher distingue o estado da Carteira dos fluxos de conexão Google.
- Cookie opaco HttpOnly, SameSite=Lax, Secure e prefixo __Host- em HTTPS.
  Nenhum bearer de serviço ou token OAuth vai ao frontend.
- Estado OAuth de uso único, ligado ao cookie, com dez minutos. Cookie e CSRF
  são trocados após login. Um state de outro navegador não encerra a sessão atual.
- Trinta minutos sem uso e máximo de oito horas; uso não renova o máximo.
  Logout/expiração são reconferidos após esperas e antes da resposta. Logout
  durante OAuth não permite que o callback recrie a sessão.
- Participação/cargos são conferidos nas ações. Saída detectada encerra a
  sessão; perda apenas de cargo recusa o privado. Dados já vistos ou copiados
  não podem ser recolhidos. A interface limpa o privado ao perder acesso,
  expirar, sair e voltar de página restaurada pelo navegador.
- Sessões/PKCE/CSRF cifrados no schema 5; cookie e estado têm hashes separados.
  Sessões não entram no backup e são encerradas em reinício, restore e rotação
  de chave. Cadastro e conexões Google confirmadas permanecem.
- Até 512 sessões e dez inícios de login por sessão anônima. Limites locais,
  não uma garantia de proteção global contra abuso; rever na etapa 9.

O serviço usa um único banco/worker, sem cópia sincronizada no frontend.
Respostas privadas/no-store, Vary Cookie, sem CORS, CORP same-origin e CSP
restrita a arquivos próprios na Carteira. A conexão/Picker conserva sua CSP
separada. Formulários exigem Origin exata e CSRF; identidade nunca vem de JSON.

## Rotas

- GET `/carteira/{servidor}` e `/{personagem}`: HTML genérico, sem dados da ficha.
- GET `/api/carteira/{servidor}/sessao`: estado do próprio login e CSRF.
- POST `/api/carteira/{servidor}/entrar`: inicia identify; não pede Google.
- POST `/api/carteira/sair`: invalida a sessão no servidor.
- GET `/api/carteira/{servidor}/galeria`: projeção básica por dono/cursor.
- GET `/api/carteira/{servidor}/personagens/{id}`: cartão básico salvo.
- POST `.../{id}/atualizar`, `/detalhes`, `/analisar`, `/analise`: ações fechadas,
  autorizadas. Atualizar reutiliza até 60 s; analisar relê; analise abre salva.
- GET `.../{id}/imagem`: bytes WebP, somente apresentação pública permitida.

O método de análise aceita só página e idioma. Não recebe usuário, campanha,
regra, aprovação, nome de método do banco ou destino de escrita.

## Testes e situação

Sessões, migração 4→5 e preservação de cadastro, cifra, backup sem sessões,
CSRF, rotação/logout/expiração, estado de outro navegador e respostas atrasadas
estão cobertos por testes HTTP/SQL reais com provedores fictícios. Registrar os
resultados e ensaios visuais ao fechar a rodada; não chamar demonstração de
validação nativa do OAuth ou Google. A demonstração local tem contas fictícias
de responsável e membro comum e segue o mesmo serviço de autorização.

Faltam fechar validação visual/teclado/celular, CI e eventuais ensaios reais.
HTTPS persistente, campanha/idioma autoritativos entre bot e serviço, medição de
host e baterias nativas avançadas continuam requisitos antes da publicação.
Não houve merge, deploy, modelo pago ou alteração de ficha oficial/jogador.

## Depois desta etapa

Restarão quatro etapas: 7 (modelo do servidor), 8 (edições permitidas),
9 (operação/recuperação/escala) e 10 (publicação). O plano recomenda
**GPT-6 Astra · Alto** para validar o contrato da etapa 7 antes de implementar
cópias. Não alterar modelos oficiais e não presumir que cópia ativa gatilhos.
