# Site de teste do bot

Página de chat pros amigos testarem a Kal'tsit e a Closure sem acesso ao claude.ai. É a mesma
página "Plantão de teste" (`Closure/ferramentas/pagina_teste/`), só que conversando com o Gemini
por um servidor pequeno que guarda a chave. A chave nunca vai pro navegador.

## Como funciona

- `servidor.py` serve a página e repassa cada mensagem pro Gemini. Só aceita conversas montadas
  pela própria página (com o prompt de sistema de uma das personagens), pede um código de acesso
  e tem limite por pessoa e por dia, pra ninguém usar a chave pra outra coisa nem estourar a cota.
- Botão **Rápido** usa `gemini-3.1-flash-lite`; **Padrão** usa `gemini-3.8-flash`. Na chave
  gratuita o 3.8 Flash só aguenta umas 20 mensagens por dia, por isso o Rápido é o padrão.
- Cada conversa fica salva no servidor (com as marcações de "Estranha"). Pra baixar todas:
  `https://SEU-SITE/api/conversas?admin=SENHA_ADMIN`. No plano grátis do Render o disco é
  apagado quando o serviço reinicia, então baixe de vez em quando. O botão "Copiar conversa"
  continua funcionando pra quem quiser mandar no Discord.
- O texto dos prompts, do lorebook e do livro fica visível no código da página (é ela que monta
  o contexto, igual no claude.ai).

## Atualizar quando um card mudar

```
python3 site/montar.py
```

Isso regera `publico/index.html` e `publico/prompts.json` a partir do `montar_pagina.py`
(as versões dos cards ficam no `VERSOES` dele). Suba os dois arquivos e o Render publica sozinho.

## Rodar no seu PC

```
cd site
GEMINI_API_KEY=... SENHA=qualquercoisa python3 servidor.py
```

e abra `http://localhost:8000`.

## Colocar no ar (Render, grátis)

1. Entre em https://render.com com a conta do GitHub.
2. **New > Blueprint**, escolha o repositório `RPG---BOT` e a branch deste site. Ele lê o `render.yaml`.
3. Preencha `GEMINI_API_KEY` (a mesma do `.env`), `SENHA` (o código que você passa pros amigos)
   e `SENHA_ADMIN` (só sua, pra baixar as conversas).
4. O Render dá um endereço `https://closure-teste-xxxx.onrender.com`. É esse que você manda.

No plano grátis o site dorme depois de 15 minutos sem uso; a primeira abertura depois disso
demora uns 50 segundos.

Outras variáveis (opcionais): `GEMINI_MODELO`, `GEMINI_MODELO_RAPIDO`, `LIMITE_HORA` (padrão 40
por pessoa), `LIMITE_DIA` (padrão 300 no total).
