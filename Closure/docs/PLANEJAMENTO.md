# Planejamento do bot Closure

> Escrito em 12/10/2026. Substitui o `plano-de-continuidade.md`, que juntava as
> conversas do dia; o conteúdo dele está todo aqui. Quando algo mudar, atualize
> este arquivo e registre o porquê em `DECISOES.md`.

## O que o bot vai fazer

1. **Consulta:** responder dúvida sobre o sistema **Ciclo Maldito** no chat, citando de
   onde tirou a regra.
2. **Correção de ficha:** analisar a ficha do jogador e apontar o que está fora da regra.
3. **Personalidade:** fazer tudo isso na voz de uma personagem (a definir, Arknights),
   como participante interativa do servidor.

## O princípio: um dado, um dono

É a mesma regra do repositório do sistema. Quem é dono de quê:

| Informação | Dono | O Closure faz o quê |
| ---------- | ---- | ------------------- |
| Texto das regras | `JJK---Project`: `sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md` (R44, 520 blocos com âncora) | Gera cópia em `dados/sistema/` por script. Nunca edita à mão. |
| Catálogos da ficha (perícias, ofícios, Caminhos, Trilhas, Origens, TRs, atributos, Famílias) | `JJK---Project`: `sistema/05-material/gerador-ficha/dados.js`, conferido pelo `conferir-ficha.py` | Gera JSON em `dados/sistema/` por script. |
| Fórmulas de personagem (Defesa, vida, PE, conhecidos…) | Peças de `sistema/03-mecanica/` e `conferir-criacao.py` | Reimplementa no corretor, com teste contra a ficha de exemplo (Kaori). |
| Bestiário | `JJK---Project`: `bestiario/` | Entra na fase 5, com acesso restrito. |
| Layout da ficha | Google Sheets "Ficha - Era da Revolução" | Lê só a aba oculta, pelo contrato em `dados/ficha/`. |
| Voz da personagem | Este projeto (`dados/personagem/`) | É dono. Alimentado pela pesquisa de fidelidade. |
| Código do bot | Este projeto (`src/`) | É dono. O legado só serve de consulta. |

Atualizar o bot quando o sistema mudar = rodar o script de sincronização de novo.

## Fases

### Fase 0: organizar a pasta Closure (concluída em 12/10/2026)

Objetivo: deixar a pasta pronta pra ser atualizada sem bagunça antes de escrever bot.

- Preencher o `README.md` (resumo, objetivos, estado atual).
- Criar `docs/DECISOES.md`: uma linha por decisão, com data e porquê.
- Montar a estrutura:

  ```
  Closure/
  ├── README.md              entrada e estado atual
  ├── docs/                  PLANEJAMENTO.md, DECISOES.md, especificações
  ├── pesquisa/              (já existe)
  ├── referencias/           material de terceiros
  ├── dados/
  │   ├── sistema/           GERADO pelo sincronizador; não editar
  │   ├── ficha/             contrato da aba oculta + fichas de teste
  │   ├── corpus_closure/    falas coletadas pela pesquisa de fidelidade (já existe)
│   └── personagem/        card, exemplos, lorebook (fase 4)
  ├── ferramentas/           sincronizar.py e afins
  └── src/                   código do bot (a partir da fase 1)
  ```

- Escrever `ferramentas/sincronizar.py`, que lê o clone do `JJK---Project` e gera:
  - `dados/sistema/livro.jsonl`: um bloco por linha (`ancora`, `capitulo`, `titulo`,
    `texto`, `acesso`);
  - `dados/sistema/catalogos.json`: o conteúdo do `dados.js`;
  - `dados/sistema/MANIFESTO.json`: versão do sistema, edição do livro, commit e data.
  Ele falha alto se o livro mudar de forma, como o `livro.py` do repo já faz.
- Escrever `dados/ficha/CONTRATO-ABA-BOT.md` (resumo abaixo; a lista de campos fica lá).

**Pronto quando:** rodar o sincronizador gera os três arquivos e o manifesto diz
v0.359 / R44. *Feito: 499 blocos em 21 capítulos, commit 53a08595. O contrato da
aba oculta está em `dados/ficha/CONTRATO-ABA-BOT.md` como rascunho.*

### Fase 1: esqueleto do bot

- `src/` com discord.py em módulos separados: `regras`, `ficha`, `chat`, `admin`.
- Configuração por `.env` (token, chave de API, IDs de canal e cargo do mestre).
- SQLite com log de toda chamada de API (modelo, tokens, latência, gatilho).
- Deploy na Discloud, reaproveitando o `discloud.config` do legado.
- **Um bot, duas personagens** (12/10/2026): o código escolhe quem responde pelo horário (Kal'tsit 9h–21h,
  Closure 21h–9h) e pelo nome chamado na mensagem. Nome e avatar têm que mudar por mensagem. Caminho a
  conferir: enviar a fala por webhook do canal, que aceita `username` e `avatar_url` por mensagem
  ([documentação](https://docs.discord.com/developers/resources/webhook)); trocar o nome da conta do bot não
  serve, porque é limitado a poucas trocas por hora. Ponto de atenção: mensagem de webhook não é a conta do
  bot, então "responderam a uma mensagem dela" tem que ser reconhecido pelo ID da mensagem que o bot guardou.

**Pronto quando:** o bot sobe, responde `/ping` e lê o `MANIFESTO.json`.
*Em 13/10/2026: código escrito e testado fora do ar (83 testes, `src/LEIA-ME.md`). Falta subir com o token
e testar o webhook no servidor.*

### Fase 2: consulta

- `/regra <termo>`: busca nos blocos e devolve o trecho com a âncora. Não gasta API.
- Chat: busca os blocos relevantes e o modelo responde **só** com base neles, citando.
  Busca por palavra-chave e sinônimo no começo; embedding só se a bateria falhar.
- Bateria de 20 a 30 perguntas com a âncora esperada, rodada a cada sincronização.

**Pronto quando:** a bateria passa e o chat não responde regra sem citar.

### Fase 3: correção de ficha

Depende da ficha fechar (faltam as Origens) e da aba oculta existir.

- Leitor da aba oculta (`.xlsx` exportado; o openpyxl lê aba oculta).
- Corretor em funções puras: recebe os campos e devolve uma lista de problemas
  (`regra`, `campo`, `esperado`, `encontrado`, `ancora`). Sem IA nessa parte.
- O modelo só explica o resultado, na voz da personagem.
- Testes com a ficha de exemplo da Kaori e com 3 a 5 fichas reais.

**Pronto quando:** as fichas de teste dão exatamente os erros conhecidos.

### Fase 4: personalidade

A pesquisa de fontes multilíngues e fidelidade já terminou: relatório em
`pesquisa/reports/Fontes multilíngues e método de fidelidade.md` e corpus em
`dados/corpus_closure/`. Esta fase não espera mais nada além da escolha da personagem.

- Escolher a personagem (o nome do bot sugere a Closure).
- Card curto, exemplos de fala em pt-BR e lorebook, como o primeiro relatório definiu.
- Funil antes do modelo (menção, reply e DM sempre; resto com chance baixa e cooldown).
- Bateria cega com quem conhece a personagem antes de soltar no servidor.

### Fase 5: bestiário e livro do mestre

- Mesmo sincronizador, com `acesso: mestre`.
- Só responde pra quem tem o cargo de mestre ou em canal restrito.

## Contrato da aba oculta da ficha

A aba visível (CARTEIRA) é toda de célula mesclada; o bot não lê ela. A aba oculta tem:

| campo | valor | observação |
| ----- | ----- | ---------- |
| versao_ficha | 1 | sobe quando o layout mudar |
| nome | =CARTEIRA!O9 | |
| caminho | =CARTEIRA!… | |
| forca | =… | |
| pericia.atletismo | =… | |
| tecnica.1.nome | =… | listas viram linhas numeradas |

- Nome de campo em minúsculo, sem acento, com ponto pra agrupar.
- A coluna `valor` é só fórmula apontando pra aba visível.
- Ficha com `versao_ficha` diferente da esperada recebe aviso, não correção.

## O que depende do Mizuki

- Fechar as Origens na ficha e criar a aba oculta (fase 3).
- 3 a 5 fichas reais, com erros já conhecidos (fase 3).
- Escolher a personagem (fase 4).
- Token do app no Discord, chave de API paga e plano da Discloud (fase 1).

## Decisões já tomadas

- API paga com funil, sem fine-tuning (relatório "Bot de personagem modelo ou API").
- Fonte das regras é o repositório `JJK---Project`, não o PDF.
- A correção é determinística; a IA só explica.
- O legado (`Closure Legado/`) não é alterado.
