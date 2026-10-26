# Preparar o acesso Google

Inspeção e piloto de 26/10/2026. A seção abaixo registra a inspeção inicial;
a configuração dedicada da etapa 3 foi criada depois, com autorizações
específicas do usuário. Não usar o projeto pessoal Rhodes Bot para o piloto.

## O que foi encontrado

Na conta pessoal aberta no navegador, o projeto **Rhodes Bot** mostra
“A plataforma de autenticação do Google ainda não está configurada”. Os
outros dois projetos visíveis na organização, chamados “My First Project”,
mostram o mesmo estado. Não há cliente OAuth pronto nesses três projetos.
Isso não é uma afirmação sobre contas ou organizações não inspecionadas.

No checkout usado nesta etapa não há `.env` das Guias. Nenhum segredo de
produção foi procurado em backups nem copiado da Arquivista. A documentação
da Arquivista descreve OAuth da conta mantenedora com cliente desktop; esse
fluxo não substitui a autorização individual dos jogadores num serviço web.

No painel Discloud consultado, a conta está no plano **Gold**, com dois apps:
Guias (700 MB) e Arquivista (256 MB), ambos online. Nenhum site apareceu nessa
lista. A documentação de [sites e APIs da Discloud](https://docs.discloud.com/how-to-host/websites-and-apis)
exige Platinum ou superior, `TYPE=site`, porta 8080 e subdomínio. Portanto,
não assumir que o app de bot atual já possa receber callbacks públicos.

## Hospedagem proposta

**Desenvolvimento:** processo local separado, banco fictício e testes sem rede.
Para o piloto OAuth no computador, registrar callbacks locais próprios quando
o cliente permitir. Isso prova o fluxo local, não funcionamento para jogadores
em outros computadores/celulares.

**Publicação:** serviço web separado do processo de conversas, com HTTPS e
volume persistente para SQLite. Carteira, callbacks e API de personagens no
mesmo serviço. O bot chama essa API por conexão autenticada; não usa SQLite
compartilhado pela rede. A escolha inicial preferida é aproveitar Discloud
somente se o usuário aprovar o plano/recursos necessários. Alternativa: outra
hospedagem com HTTPS e disco persistente, com orçamento antes da contratação.

Não contratar nada nesta etapa. O valor incremental ainda não foi cotado;
não há promessa de hospedagem gratuita nem autorização para upgrade. O
desenho não depende de uma marca específica de hospedagem. Não migrar os bots
atuais nem transformar o app publicado em site para testar.

## Configuração concreta que falta

| Item | Proposta | Situação |
|---|---|---|
| Projeto Google | Guias do Ciclo - Fichas (`guias-ciclo-fichas`) | Criado na conta dedicada, sem ativar faturamento; número `1015676492327` |
| Nome do aplicativo | Guias do Ciclo — Fichas | Cadastrado |
| Público | Externo/Testando | Só conta dedicada das Guias e conta pessoal do mantenedor autorizadas |
| APIs | Drive, Sheets e Picker | Três ativações conferidas no painel |
| Cliente Google | Carteira de personagens — Piloto local | Criado; credencial em diretório privado do usuário, fora do Git |
| Escopo | `https://www.googleapis.com/auth/drive.file` | Único escopo configurado; consentimento nativo separado |
| Retorno Google | `http://127.0.0.1:8876/oauth/google/retorno` | Salvo no cliente local; origem JavaScript `http://127.0.0.1:8876` |
| Retorno Discord | `http://127.0.0.1:8876/oauth/discord/retorno` | Salvo nas Guias oficiais por escolha do usuário; segredo OAuth redefinido pelo próprio usuário |
| Picker web | Google Picker — Piloto local | Chave criada com uma API (Picker), referenciadores `http://127.0.0.1:8876/*` e `https://docs.google.com/*`; ainda não comprova seleção nativa |
| Documentos públicos | Página de apresentação, privacidade e termos atualizados | Preparar antes de público geral |
| Segredos | Diretório privado do usuário no disco do sistema | Arquivos 600, pasta 700; disco externo ignora permissões e não deve guardar as credenciais em texto |

Não registrar domínio de exemplo como retorno real. Preparar a origem exata
antes de criar o cliente. Não colocar token/segredo em documentos ou pedir que
o usuário os envie no chat. Configuração sensível no navegador deve seguir
a confirmação exigida naquele momento; esta lista não concede acesso Google.

### Variáveis do serviço, não do bot publicado

Implementação local da etapa 3: [execução e piloto](SERVICO.md). Configuração
externa e prova nativa continuam pendentes.

```text
CARTEIRA_PUBLIC_ORIGIN
CARTEIRA_DISCORD_CLIENT_ID
CARTEIRA_DISCORD_CLIENT_SECRET
CARTEIRA_DISCORD_BOT_TOKEN
CARTEIRA_GOOGLE_CLIENT_ID
CARTEIRA_GOOGLE_CLIENT_SECRET
CARTEIRA_GOOGLE_PROJECT_NUMBER
CARTEIRA_PICKER_API_KEY
CARTEIRA_ENCRYPTION_KEYS
CARTEIRA_DATABASE_PATH
CARTEIRA_SERVICE_TOKEN
CARTEIRA_GUILDS
CARTEIRA_DEV
```

Todos os valores ficam fora do Git. A chave do Picker vai ao navegador, mas
deve ter restrições de API/origem; não substitui OAuth. A chave de cifra não
pode ser derivada do token Discord nem renovada sem migração dos envelopes.

## Prova nativa ainda necessária

1. Preparar ambiente separado, cliente e callbacks; confirmar identidade
   Discord e membro atual sem ler conversas.
2. Abrir conexão pelo Discord e entrar no Google no navegador oficial.
3. Selecionar apenas uma ficha descartável; confirmar conta, `isAppAuthorized`,
   formato e leitura fixa pequena em `ANALISE`.
4. Confirmar o vínculo, reiniciar o serviço de teste e reler com renovação.
5. Cancelar outro cadastro e selecionar uma conta/arquivo indevido: nenhuma
   troca silenciosa deve ocorrer.
6. Revogar o acesso Google e comprovar bloqueio/reconexão; substituir arquivo
   mantendo o personagem e sem alterar o original.
7. Repetir em celular. Confirmar a necessidade de navegador externo; não
   contornar restrições Google a navegadores embutidos.

O piloto real começou pela entrada controlada; participação foi conferida
na API Discord, mas autorizações/seleção ainda precisam de confirmação e
resultado nativo. Não iniciar bot duplicado com token de produção para criar
o comando de teste. Preparar aplicação/ambiente de
teste ou outra entrada controlada e documentar suas diferenças do fluxo final.

## Referências

- [OAuth web Google](https://developers.google.com/identity/protocols/oauth2/web-server): fluxo e renovação no servidor; usar biblioteca mantida.
- [Escopo por arquivo](https://developers.google.com/workspace/drive/api/guides/api-specific-auth): `drive.file` permite leitura/escrita dos arquivos autorizados.
- [Picker web e mobile](https://developers.google.com/workspace/drive/picker/guides/overview): fluxos diferentes; a página web usará Picker web.
- [OAuth Discord](https://docs.discord.com/developers/topics/oauth2): identificação do usuário por authorization code.
- [Sites Discloud](https://docs.discloud.com/how-to-host/websites-and-apis): requisitos de hospedagem externa.

Consentimento em modo de teste pode ter renovação com validade limitada.
Validar os requisitos de publicação/verificação antes de oferecer acesso
durável a qualquer jogador. Não prometer autorização “permanente”.

## Credenciais locais do piloto

Ficam em `~/.local/share/guias-ciclo/carteira-piloto`, fora do repositório.
Não copiar os conteúdos para ferramentas de registro, commits ou ZIPs.
`google-client.json`, `discord-client.json`, `discord-bot.json`, `picker.json`
e `ambiente.json` têm permissão 600; diretório 700. O token das Guias é usado
somente em REST para conferir membros/cargos no servidor permitido. Não há
segundo processo de bot/Gateway. O usuário cancelou a proposta de um app
Discord separado e escolheu o oficial; nenhum app de teste foi criado.

O download do JSON pelo painel falhou; a credencial Google foi preservada
da tela de criação, sem expor seu valor, e conferida localmente. Apenas
metadados não secretos entram no Git. O serviço continua sem domínio público.
