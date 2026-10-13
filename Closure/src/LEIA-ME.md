# src: código do bot

Esqueleto da fase 1 do `docs/PLANEJAMENTO.md`, escrito em 13/10/2026. O bot antigo em
`../../Closure Legado/` serve só de consulta.

**O que já faz:** sobe, responde `/ping` lendo o `MANIFESTO.json`, decide quem responde a cada mensagem
(por horário e pelo nome chamado), registra o gatilho em SQLite e sabe enviar com o nome e o avatar de
cada personagem. **O que ainda não faz:** responder no chat. A resposta (busca nas regras, prompt do card,
chamada ao modelo) já está ligado em `closure_bot/cogs/chat.py`.

## Arquivos

| Arquivo | O que faz |
| ------- | --------- |
| `closure_bot/plantao.py` | Quem responde: turno por horário, nome chamado, as duas citadas. Não conhece o Discord. A regra tem dono: `dados/personagem/servidor.md` e os `vida.md` |
| `closure_bot/config.py` | Lê o `.env` da pasta `Closure/` (o ambiente vence o arquivo) |
| `closure_bot/registro.py` | SQLite: `chamadas_api`, `gatilhos`, `mensagens_bot`, `paineis_clima` (um por servidor), `falas` (as últimas respostas de cada personagem por canal), `paciencia`, `fichas` (o que elas guardam de cada pessoa) e `mensagens_do_dia` (o texto de quem chamou, só até as 4h30) |
| `closure_bot/vida.py` | O estado do momento, pelo desenho dos `vida.md`: carga, movimento do canal, paciência, intimidade; monta o bloco de estado e as linhas a mais do lembrete |
| `closure_bot/reflexao.py` | Reflexão diária: tira das mensagens do dia os fatos de cada pessoa, passa pela peneira e apaga o texto |
| `closure_bot/cogs/pessoa.py` | `/meus_dados`, `/meus_pronomes`, `/meu_fato`, `/esquecer_fato`, `/apagar_meus_dados`, e o laço da reflexão às 4h30 |
| `closure_bot/dados.py` | Lê o manifesto das regras e o nome e a versão de cada card. Não escreve em `dados/` |
| `closure_bot/carteiro.py` | Envia a fala pelo webhook do canal, com nome e avatar por mensagem, e guarda o ID |
| `closure_bot/bot.py` | Junta tudo e carrega os módulos |
| `closure_bot/clima.py` | Clima de Tóquio ou de outro lugar pela Open-Meteo (sem chave), com cache de 15 min; acha o lugar pelo nome, diz se a mensagem puxa o assunto e monta a linha do bloco 4 |
| `closure_bot/cogs/clima.py` | `/clima [lugar]`, `/clima_canal`, `/clima_canal_desligar` e o painel diário de Tóquio, um canal por servidor |
| `closure_bot/modelo.py` | A chamada à IA numa camada só: fila de `provedor:modelo` com reserva (Vertex AI e AI Studio), e cada tentativa registrada com tokens e latência |
| `closure_bot/cogs/admin.py` | `/ping`, `/status`, `/teste_webhook` (este só pro dono) |
| `closure_bot/cogs/chat.py` | Escuta as mensagens, decide quem responde, monta o pedido, chama o modelo e envia a fala |
| `closure_bot/conversa.py` | A conversa em andamento com cada personagem por canal, só em memória (30 min, 12 turnos) |
| `closure_bot/prompt.py` | Monta o pedido ao modelo. Hoje pela ponte do site, no Node; é o único ponto que depende dela |
| `closure_bot/cogs/regras.py`, `ficha.py` | Vazios: fases 2 e 3 |
| `testes/` | 144 testes; 26 deles precisam do discord.py e 4 da cryptography e são pulados sem ele. `testes/dados/` guarda respostas reais da Open-Meteo |

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
- **Contra a monotonia** (pedido do Mizuki, 13/10/2026): o `carteiro` guarda o texto de cada fala enviada
  (só as delas, nunca o que as pessoas escrevem; 30 por personagem e por canal). A ponte aceita essas falas
  em `falas_anteriores` e roda com elas o detector de repetição da própria página, então o aviso "você já
  usou..." vale de uma conversa pra outra, sem chamada a mais. Medição com `ferramentas/medir_monotonia.py`:
  "oi closure" foi de 3 pra 6 respostas diferentes em 6, e "kal, tudo bem?" de 4 pra 6. Tira frase repetida;
  não dá assunto novo, que depende do estado e da ficha.
  A memória tem limite, pra ela não ter que inventar pra sempre: valem só as 6 respostas mais novas e só as
  das últimas 12 horas (`FALAS_VALEM_HORAS`); a frase só é barrada depois de aparecer em duas delas.
- **Vida** (13/10/2026): `vida.py` calcula o estado sem chamar modelo. Carga: respostas dela na última hora,
  em todos os canais. Movimento: mensagens do canal em 15 min (só a hora fica, em memória). Paciência: por
  pessoa e por personagem, cai com pergunta repetida em 30 min ou tentativa de tirá-la do personagem, volta 1 a
  cada 2 h; da pergunta fica só um resumo embaralhado, nunca o texto. Intimidade: dias diferentes em que a
  pessoa chamou aquela personagem (5, 15, 40, 100). O estado entra pela ponte (`estado=`): o bloco troca o
  da página, que é fixo, e o lembrete ganha no máximo duas linhas contando a de fora do plantão.
  Medição com `ferramentas/medir_monotonia.py --modo vida`: com ficha a resposta muda de assunto
  ("Como tá o Ren, ainda aguentando o tranco na mesa do Tiago?"); sem ficha ela usa o canal e o fato de a
  pessoa ser nova. Faltam os fatos da ficha, que só a reflexão diária preenche.
- **Ficha de pessoa e reflexão diária** (13/10/2026): quando alguém chama uma personagem, o texto fica em
  `mensagens_do_dia`. Às 4h30 `reflexao.py` manda o lote ao modelo, só por provedor pago, e grava no máximo três
  fatos novos por pessoa, até 15 no total (o mais velho sai). O texto é apagado mesmo se o modelo falhar. A
  peneira roda no pedido e no código: nada de saúde, dinheiro, religião, política, relacionamento, idade,
  endereço, contato, nem fato sobre outra pessoa. Na resposta entram só os fatos ligados à mensagem (até dois)
  ou, em uma de cada três, um sorteado (`vida.escolher_fatos`). Teste de verdade com 12 mensagens inventadas:
  8 fatos certos, e ficaram de fora a ansiedade, a idade, a cidade, a fofoca e o mau humor do dia.
- **Regras de fora** (lidas em 13/10/2026): política e termos de desenvolvedor do Discord e termos da API do
  Gemini. Feito por causa delas: a peneira dos fatos, a política de privacidade (`docs/PRIVACIDADE.md`,
  com link no fim do `/meus_dados`) e a cifra do banco. Falta o Mizuki pôr o link da política no portal de desenvolvedor do
  Discord. Fica em aberto, por decisão dele: o gratuito continua primeiro na fila, e nessa cota o Google pode
  usar o que recebe pra treinar, o que a regra 21 do Discord não permite com conteúdo de mensagem.
- **Banco cifrado:** `python3 -m closure_bot --gerar-chave` cria a `CHAVE_DO_BANCO` no `.env` (já criada neste
  computador). Com ela, falas, mensagens do dia, pronomes e fatos vão cifrados pro disco; IDs, horas e
  contagens ficam em claro. A hospedagem precisa da mesma variável. Sem a chave, ou com outra, o bot não
  mostra letra embaralhada: esquece o que não abre. Perder a chave é perder as fichas.
- **Chat ligado** (13/10/2026): quem chama uma personagem recebe resposta. O caminho, em `cogs/chat.py`:
  decide quem responde, atualiza o estado, monta o pedido pela ponte (`prompt.py`) com a conversa em andamento,
  as falas anteriores, o estado e a linha de clima, chama o modelo e envia pelo webhook. Só entra na conversa a
  mensagem de quem a chamou e a resposta dela; o resto do canal não vai pro modelo. Se o modelo falha, ela
  fica calada (frase pronta de erro não é fala dela) e o motivo vai pro log. Só o dono, pelo `DONO_ID`, vai
  no pedido como Mizuki.
- **Espera:** cada tentativa tem 25 segundos. Provedor que falha fica de molho (10 min depois de cota
  estourada, 2 min depois de sobrecarga ou queda de rede) e a fila pula direto pro seguinte.
- **Em aberto:** o bot em produção precisa do Node e da página do site baixada (`src/var/site/nucleo.js`), ou
  a busca ganha versão em Python. Testado de ponta a ponta sem o Discord, com mensagem de mentira e o resto
  de verdade; no Discord mesmo ainda não rodou.

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
