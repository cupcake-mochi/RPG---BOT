# Publicar o site da Carteira viva

Preparado em 21/11/2026, antes do upgrade da Discloud. Tudo daqui pra baixo
espera o plano **Platinum** (R$ 10,99/mês, conferido em discloud.com/plans em
21/11/2026), que é o primeiro plano com site. Contratar é com o Mizuki.

O site é um **app novo** na Discloud, `TYPE=site`, separado do app das Guias.
O bot continua no app dele e só passa a chamar o site.

## Situação em 21/11/2026, noite

O site está no ar em **https://guias-carteira.discloud.dev**: app `guias-carteira`,
512 MB, ao lado do bot (512 MB), do Arquivista (256 MB) e da Servidora (128 MB).
Os 4 somam 1,4 GB dos 2 GB do Platinum. Medido em casa, o site parado com o
motor carregado usa uns 60 MB; o bot ficou em uns 150 MB no dia todo.

| Passo | Situação |
|---|---|
| 1. Subdomínio | Feito. A Discloud deu `.discloud.dev`, não `.app` |
| 2. `.env` do site | Feito, com chave, segredo de serviço, token do bot, Client ID e servidores |
| 3. Discord | Retorno `.dev` cadastrado. **Falta o Client Secret**: o Discord pede o código de dois fatores do Mizuki pra redefinir |
| 4. Google | **Parado**: a conta dona do projeto precisa ativar a verificação em duas etapas antes de abrir o Google Cloud |
| 5 e 6. Pacote e app do site | Feito. Os 4 campos que faltam estão com `PENDENTE-MIZUKI` |
| 7. Ligar o bot | Espera os passos 3 e 4. Sem isso os comandos apareceriam e o cadastro falharia |
| 8. Teste | Espera o passo 7 |

Servidores liberados em `CARTEIRA_GUILDS`: o servidor principal (`GUILD_ID` do
bot) e o servidor que tem campanha cadastrada no `ficha-campanhas.json`.

## O que já está pronto no código

| Peça | Onde |
|---|---|
| Arquivo de início do site, porta 8080 em 0.0.0.0 | `iniciar_carteira.py` |
| Pacote do site, com `discloud.config` de site | `ferramentas/empacotar_carteira.py` |
| `.env` do site com chave e segredo sorteados | `empacotar_carteira.py --gerar-env` |
| Páginas públicas: início, privacidade e termos | `/`, `/privacidade`, `/termos` |
| Excluir personagem e apagar todos os dados | `/personagem excluir`, `/personagem apagar_meus_dados` (e `/character delete`, `/character delete_my_data`) |
| Ponte no bot, ligada só com o site configurado | `CARTEIRA_API_URL` e `CARTEIRA_SERVICE_TOKEN` no `.env` do bot |

## Passo a passo

### 1. Subdomínio (Mizuki, no painel da Discloud)

Registrar um subdomínio, por exemplo `guias-carteira`. A Discloud escolhe, na hora de publicar, se
fica em `.discloud.app` ou `.discloud.dev`. A origem do site é o endereço
completo com `https://`, sem barra no fim. Nos exemplos abaixo:
`https://guias-carteira.discloud.dev`.

### 2. `.env` do site (eu rodo, sem mostrar segredo)

```sh
python3 ferramentas/empacotar_carteira.py --gerar-env ~/.local/share/guias-ciclo/carteira-site.env
```

- O arquivo já sai com `CARTEIRA_ENCRYPTION_KEYS` e `CARTEIRA_SERVICE_TOKEN`
  sorteados. Os outros campos ficam em branco, cada um com uma linha dizendo
  de onde vem.
- O arquivo fica no disco do sistema, fora do git e fora do HD externo.
- Guardar uma cópia da chave de cifra **longe dos backups do app**. Sem ela, o
  banco do site não abre.
- O pacote recusa `.env` com campo obrigatório vazio, linha que não seja
  `CARTEIRA_*` ou `CARTEIRA_DEV`.

### 3. Discord (Mizuki faz o login, eu guio)

No Developer Portal, app **Guias do Ciclo** → OAuth2:

- acrescentar o retorno `https://guias-carteira.discloud.dev/oauth/discord/retorno`;
- copiar o Client ID e o Client Secret pro `.env` do site;
- `CARTEIRA_DISCORD_BOT_TOKEN` é o mesmo token do bot (o `DISCORD_TOKEN` do
  `.env` dele). O site usa só pra conferir membro e cargo, sem Gateway.

### 4. Google (Mizuki faz o login, eu guio)

No projeto `guias-ciclo-fichas` (número `1015676492327`):

- **Cliente OAuth novo, tipo web, de produção.** O atual é o "Piloto local",
  com retorno em `127.0.0.1`.
  - Origem JavaScript: `https://guias-carteira.discloud.dev`.
  - Retorno: `https://guias-carteira.discloud.dev/oauth/google/retorno`.
- **Chave do Picker:** acrescentar o referenciador
  `https://guias-carteira.discloud.dev/*`, mantendo só a API do Picker.
- **Tela de consentimento:**
  - página inicial `https://guias-carteira.discloud.dev/`;
  - privacidade `…/privacidade`;
  - termos `…/termos`;
  - o escopo continua só `drive.file`.
- **Status de publicação: passar de "Em teste" para "Em produção".** Em teste,
  a autorização de quem não é usuário de teste não funciona, e a renovação
  vence em 7 dias.
- **Domínio autorizado:** o Google pode pedir que o domínio do site seja
  verificado no Search Console. Com subdomínio da Discloud, conferir na hora o
  que a tela pede. `drive.file` é escopo não sensível, então o app não precisa
  da verificação formal de escopo. Isso foi conferido antes; a parte do
  domínio ainda não.

### 5. Pacote do site (eu rodo)

Pegar o cadastro das campanhas do backup mais recente do app das Guias
(`src/var/ficha-campanhas.json` dentro do zip) e montar:

```sh
python3 ferramentas/empacotar_carteira.py --subdominio guias-carteira \
    --campanhas CAMINHO/ficha-campanhas.json --env ~/.local/share/guias-ciclo/carteira-site.env
```

- Sai em `src/var/carteira-site.zip`.
- Com o `.env` dentro, o zip não pode ser compartilhado.
- Sem `--campanhas`, o site sobe com a análise desligada; cartão, galeria e
  cadastro funcionam.
- `RAM=512` é o mínimo que a Discloud pede pra site. A RAM é decisão do
  Mizuki; `--ram` muda o valor.
- O banco nunca vai no zip. Ele nasce em `var/carteira.sqlite3` no disco do
  app e continua lá entre um envio e outro.

### 6. Subir o site (eu faço, com o ok do Mizuki)

- Criar o app novo com o zip. **Não** usar o Commit do app das Guias.
- Conferir os logs e abrir `https://guias-carteira.discloud.dev/saude`, que
  responde `{"servico": "carteira-viva", "estado": "online"}`.
- Conferir `/`, `/privacidade` e `/termos`.

### 7. Ligar o bot (eu faço, com backup antes e depois)

- No `.env` do bot, acrescentar:

  ```text
  CARTEIRA_API_URL=https://guias-carteira.discloud.dev
  CARTEIRA_SERVICE_TOKEN=<o mesmo do .env do site>
  ```

- Montar o pacote do bot (`ferramentas/empacotar.py --com-env`) e mandar pelo
  Commit do app das Guias, como nos registros anteriores. O pacote já leva os
  4 arquivos da ponte.
- No arranque, o bot registra `/personagem`, `/personagens`, `/character` e
  `/characters` em todos os servidores. Sem as duas variáveis, nada disso
  aparece.

### 8. Teste em produção

1. `/personagem cadastrar` com uma cópia descartável da ficha, no computador.
2. Repetir no celular, com navegador externo.
3. `/personagens`, editar o cartão, marcar Vida/PE/Defesa e abrir a galeria
   web pelo título do cartão.
4. `/personagem analisar` (só com o cadastro das campanhas no pacote).
5. `/personagem excluir` e `/personagem apagar_meus_dados` com a conta de teste.
6. Revogar o acesso em myaccount.google.com/permissions e conferir que o
   cartão pede reconexão.

## Depois de publicado

- **Cadastro das campanhas:** o site usa uma cópia. Quando o mestre aprova
  algo no bot, o `ficha-campanhas.json` dele muda, e a cópia do site só
  acompanha quando o site recebe o arquivo de novo.
  - Hoje: montar o pacote com o arquivo novo e mandar pelo Commit do app do
    site.
  - Sincronizar sozinho fica como trabalho futuro.
- **Backup:** o backup da Discloud do app do site leva o banco cifrado. A chave
  fica só no `.env` e na cópia separada. Restaurar segue
  [BANCO.md](BANCO.md); cópia com mais de 30 dias é recusada.
- **Atualizar o site:** o mesmo pacote, pelo Commit do app do site. O disco do
  app, com o banco e as imagens, continua.
