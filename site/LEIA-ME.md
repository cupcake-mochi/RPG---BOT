# Site de teste do bot

Página de chat pros amigos testarem a Kal'tsit e a Closure sem acesso ao claude.ai. É a mesma
página "Plantão de teste" (`Closure/ferramentas/pagina_teste/`), só que conversando com o Gemini
por um servidor pequeno que guarda a chave. A chave nunca vai pro navegador.

## Como funciona

- `servidor.py` serve a página e repassa cada mensagem pro Gemini. Só aceita conversas montadas
  pela própria página (com o prompt de sistema de uma das personagens), pede um código de acesso
  e tem limite por pessoa e por dia, pra ninguém usar a chave pra outra coisa nem estourar a cota.
- Cada botão tem uma fila de modelos. Se um esgota a cota, cai ou demora mais de 60 s, o próximo
  responde, e a conversa salva anota qual modelo deu cada fala.
  - **Rápido:** Gemini 3.1 Flash-Lite, 3.5 Flash-Lite, 2.5 Flash-Lite e, com `MISTRAL_API_KEY`, Mistral Medium.
  - **Padrão:** Gemini 3.8 Flash, 3.5 Flash e 3 Flash Preview (cada um só tem 20 pedidos por dia na
    chave grátis), Mistral Medium e depois a fila do Rápido.
  - Dá pra trocar com `FILA_RAPIDO` / `FILA_PADRAO` (`provedor:modelo,...`; provedores: `gemini`,
    `mistral`, `groq`, `openrouter`, cada um com a sua `*_API_KEY`).
  - A chave do Gemini é a mesma dos testes de personalidade, então os dois gastam a mesma cota.
- Cada conversa é salva sozinha a cada resposta e a cada marcação de "Estranha" (com a nota),
  sem botão de enviar. Com `GITHUB_TOKEN` configurado, o servidor também manda cada conversa, em
  texto, pra pasta `conversas/` da branch `conversas` deste repositório, uns 90 segundos depois
  da última mudança. O repositório é público: avise os amigos que o que eles escrevem fica visível. É lá que dá pra ler e avaliar, porque o disco do Render grátis apaga quando o
  serviço reinicia. Sem token, dá pra baixar o que estiver no servidor em
  `https://SEU-SITE/api/conversas?admin=SENHA_ADMIN`.
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
4. Opcional, mas recomendado: crie um token em GitHub > Settings > Developer settings >
   Fine-grained tokens, só pro repositório `RPG---BOT`, com permissão **Contents: Read and write**,
   e coloque em `GITHUB_TOKEN`.
5. O Render dá um endereço `https://closure-teste-xxxx.onrender.com`. É esse que você manda.

No plano grátis o site dorme depois de 15 minutos sem uso; a primeira abertura depois disso
demora uns 50 segundos.

Outras variáveis (opcionais): `GEMINI_MODELO`, `GEMINI_MODELO_RAPIDO`, `LIMITE_HORA` (padrão 40
por pessoa), `LIMITE_DIA` (padrão 300 no total).
