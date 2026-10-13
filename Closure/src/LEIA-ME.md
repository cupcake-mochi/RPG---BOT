# src: código do bot

Esqueleto da fase 1 do `docs/PLANEJAMENTO.md`, escrito em 13/10/2026. O bot antigo em
`../../Closure Legado/` serve só de consulta.

**O que já faz:** sobe, responde `/ping` lendo o `MANIFESTO.json`, decide quem responde a cada mensagem
(por horário e pelo nome chamado), registra o gatilho em SQLite e sabe enviar com o nome e o avatar de
cada personagem. **O que ainda não faz:** responder no chat. A resposta (busca nas regras, prompt do card,
chamada ao modelo) entra nas fases 2 e 4, no ponto marcado em `closure_bot/cogs/chat.py`.

## Arquivos

| Arquivo | O que faz |
| ------- | --------- |
| `closure_bot/plantao.py` | Quem responde: turno por horário, nome chamado, as duas citadas. Não conhece o Discord. A regra tem dono: `dados/personagem/servidor.md` e os `vida.md` |
| `closure_bot/config.py` | Lê o `.env` da pasta `Closure/` (o ambiente vence o arquivo) |
| `closure_bot/registro.py` | SQLite: `chamadas_api`, `gatilhos`, `mensagens_bot` e `paineis_clima` (um por servidor) |
| `closure_bot/dados.py` | Lê o manifesto das regras e o nome e a versão de cada card. Não escreve em `dados/` |
| `closure_bot/carteiro.py` | Envia a fala pelo webhook do canal, com nome e avatar por mensagem, e guarda o ID |
| `closure_bot/bot.py` | Junta tudo e carrega os módulos |
| `closure_bot/clima.py` | Clima de Tóquio ou de outro lugar pela Open-Meteo (sem chave), com cache de 15 min; acha o lugar pelo nome, diz se a mensagem puxa o assunto e monta a linha do bloco 4 |
| `closure_bot/cogs/clima.py` | `/clima [lugar]`, `/clima_canal`, `/clima_canal_desligar` e o painel diário de Tóquio, um canal por servidor |
| `closure_bot/modelo.py` | A chamada à IA numa camada só: fila de `provedor:modelo` com reserva (Vertex AI e AI Studio), e cada tentativa registrada com tokens e latência |
| `closure_bot/cogs/admin.py` | `/ping`, `/status`, `/teste_webhook` (este só pro dono) |
| `closure_bot/cogs/chat.py` | Escuta as mensagens, decide e registra o gatilho |
| `closure_bot/cogs/regras.py`, `ficha.py` | Vazios: fases 2 e 3 |
| `testes/` | 85 testes; 19 deles precisam do discord.py e são pulados sem ele. `testes/dados/` guarda respostas reais da Open-Meteo |

## Rodar

De dentro de `src/`:

```bash
python3 -m unittest discover -s testes
```

```bash
python3 -m closure_bot --conferir
```

O `--conferir` não conecta ao Discord: mostra as regras lidas, a versão dos cards, quem está de plantão e o
que falta no `.env`. Pra subir de verdade:

```bash
pip install -r requirements.txt
```

```bash
python3 -m closure_bot
```

## O que falta pra subir (depende do Mizuki)

1. **Token do app no Discord**, no `.env` da pasta `Closure/` (modelo em `.env.exemplo`, na raiz do repositório). Nunca no chat.
2. No Developer Portal, ligar o **Message Content Intent** do bot: sem ele o bot não lê o nome na mensagem.
3. No servidor, a permissão **Gerenciar webhooks** pro bot. Sem ela a fala sai pela conta do bot, com o
   nome na frente ("**Closure:** ...").
4. `DONO_ID` e as duas URLs de avatar no `.env`. `GUILD_ID` é opcional: é só um servidor de teste em que os
   comandos aparecem na hora. O bot foi feito pra rodar em vários servidores.
5. Em cada servidor, usar `/clima_canal` no canal que vai receber o painel diário (ou passar o canal).

## Modelo e prompt (13/10/2026)

- **Chamada à IA:** `closure_bot/modelo.py`. A fila padrão tenta o **gratuito primeiro** (Gemini 3.8 Flash
  pela chave do AI Studio) e só vai pro pago (o mesmo modelo pela Vertex) quando a cota do dia acaba; depois
  vem o 3.1 Flash-Lite, gratuito e pago. Provedor sem chave no `.env` sai da fila.
- **Teto de gasto:** a Vertex é pós-paga e não para quando o crédito acaba, passa a cobrar no cartão. Então
  o teto é do bot: antes de usar o pago ele soma o gasto do mês pelo registro (tokens vezes o preço de tabela
  de 13/10/2026) e, chegando a `TETO_MENSAL_USD` (padrão US$ 9), tira o pago da fila até o mês virar.
  `/status` e `--conferir` mostram o gasto estimado.
- **O que o gratuito custa:** a cota do 3.8 Flash é de 20 pedidos por dia, dividida com o site de teste; o
  Google pode usar as conversas do nível gratuito pra melhorar os produtos dele (no pago, não); e ele falha
  mais: num teste de 13/10, 3 de 7 pedidos voltaram "modelo com alta demanda".
- **Vertex com credencial desde 13/10/2026:** chave de API em `VERTEX_API_KEY`. A organização do Google
  Cloud bloqueia esse tipo de chave por padrão; o Mizuki soltou a restrição só no projeto do bot. O primeiro
  teste real (17 respostas, US$ 0,096) está em `pesquisa/validacao/` e resumido no fim de
  `pesquisa/reports/Qual IA usar no bot.md`.
- **Raciocínio reduzido por padrão** (Mizuki, 13/10/2026, "por enquanto"): o bot pede `thinkingLevel: low`.
  No teste custou 42% menos e respondeu em 2 a 4,5 s em vez de 4 a 13 s, sem perda visível em 17 respostas.
  `RACIOCINIO=modelo` no `.env` devolve o padrão do próprio modelo.
- **Prompt:** por enquanto vem do site de teste, por `../ferramentas/prompt_do_site/`. Essa ponte baixa a
  página do ramo `site-teste` e roda no Node a lógica dela (lorebook, busca no livro, estado, lembrete), então
  o bot usa exatamente o que os amigos testam, sem cópia de texto de card. Precisa do Node instalado.
- **Ler respostas:** `python3 ferramentas/testar_modelo.py` (de dentro de `Closure/`) manda 16 casos pelas
  duas personagens e grava em `pesquisa/validacao/`. Com a fila na Vertex cada caso é uma chamada paga.
- **Ainda não ligado:** o `cogs/chat.py` continua só registrando o gatilho. Falta chamar a ponte e o modelo
  ali, e decidir se o bot em produção roda o Node ou se a busca ganha versão em Python.

## Regras de plantão implementadas

- Kal'tsit das 9h às 21h, Closure das 21h às 9h, horário de Brasília.
- O bot só reage a nome na mensagem (`closure`, `kal`, `kal'tsit`, `kaltsit`), menção ao bot ou resposta a
  uma mensagem dele. Mensagem de bot ou de webhook nunca é gatilho.
- Sem nome: responde quem está de plantão. Com nome: responde a chamada, mesmo fora do turno (a decisão
  sai marcada como fora do plantão, pra o lembrete ganhar a linha certa).
- As duas citadas na mesma mensagem: vale o nome que abre a mensagem; sem isso, quem está de plantão.
  **Essa regra é minha**, pra cobrir "closure, a kal'tsit falou que..."; o Mizuki pode trocar.
- Conversa privada com o bot é ignorada por enquanto: não existe webhook em DM, então lá não dá pra trocar
  nome e avatar. Fica em aberto.

## Clima (pedido do Mizuki em 13/10/2026)

Vem do bot antigo, que tinha painel de clima de Tóquio. Decisões do Mizuki: o painel automático volta; quando
perguntam, a personagem responde; vale pra outros lugares além de Tóquio; e **as duas monitoram de longe, sem
estar no lugar**.

- **Fonte:** Open-Meteo no lugar da OpenWeatherMap. Não pede chave nem conta, então não há segredo pra
  guardar. A chave antiga está escrita no código do legado; se aquele arquivo já foi compartilhado, vale
  revogar a chave no site da OpenWeatherMap.
- **`/clima [lugar]`** mostra o painel na hora (temperatura, sensação, umidade, vento, mínima e máxima, sol).
  Sem lugar, Tóquio.
- **Painel diário, um por servidor:** quem tem a permissão Gerenciar servidor usa `/clima_canal` no canal
  desejado, ou escolhe o canal no campo do comando (colar o ID do canal funciona). O painel de hoje sai na
  hora; nos outros dias, na primeira leitura depois das 6h de Brasília, e a mesma mensagem é editada quando a
  condição ou a temperatura mudam (confere de 15 em 15 min). `/clima_canal_desligar` desliga. É mensagem do
  bot, sem nome de personagem. Canal, dia e ID da mensagem ficam no SQLite, pra um reinício não postar de
  novo. Diferença pro legado: se o bot estiver fora do ar às 6h, o painel sai quando ele voltar.
- **Na conversa:** quando a mensagem puxa o assunto, `contexto_clima()` devolve a linha de dado pro bloco 4.
  Sem lugar na pergunta vale Tóquio ("tá chovendo aí?"); com lugar, o de lá ("como tá o clima em São Paulo?"):
  `[São Paulo, Brasil agora (14:15 de lá, dia): 28 °C, sensação de 30 °C, trovoada, ...]`. Lugar que a busca
  não acha vira `[Clima: o monitor não achou o lugar "X".]`. Sem a mensagem puxar, nada entra: é a mesma
  regra do sono da Closure, pra o clima não virar bordão. A ligação com o prompt entra junto com a resposta
  no chat (fases 2 e 4).
- **Como a busca escolhe o lugar:** entre os resultados com aquele nome, fica o mais populoso ("Paris" é a
  da França). A linha traz estado e país, pra quem perguntou ver se era esse. "Nova York" tem apelido no
  código, porque a busca em português só achava uma cidade do Maranhão.
- **Falta no card (texto de personagem, vai pelos geradores, com teste):** dizer que as duas acompanham o
  clima pelo computador e contam como está, sem dizer que estão lá. Elas respondem de outra estação, então
  não falam "aqui tá chovendo".

## Pendências desta fase

- Subir de verdade com o token e testar `/teste_webhook` no servidor.
- Deploy na Discloud: o `discloud.config` do legado aponta pra um arquivo só; aqui o pacote precisa levar
  `src/` e a parte de `dados/` que o bot lê.
- Se o Project do app tiver criado algo em `src/` depois de 12/10, juntar com isto.
