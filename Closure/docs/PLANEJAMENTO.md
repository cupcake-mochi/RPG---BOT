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
*Em 13/10/2026: código escrito e testado fora do ar (92 testes, `src/LEIA-ME.md`). Falta subir com o token
e testar o webhook no servidor.*

### Fase 2: consulta

- `/regra <termo>`: busca nos blocos e devolve o trecho com a âncora. Não gasta API.
- Chat: busca os blocos relevantes e o modelo responde **só** com base neles, citando.
  Busca por palavra-chave e sinônimo no começo; embedding só se a bateria falhar.
- Bateria de 20 a 30 perguntas com a âncora esperada, rodada a cada sincronização.

**Pronto quando:** a bateria passa e o chat não responde regra sem citar.

### Fase 3: correção de ficha

*Começou em 14/10/2026, depois de a ficha ganhar a aba `ANALISE` (B47, fase 1). Feito: leitor
(`src/closure_bot/ficha_leitor.py`, `.xlsx` e link), corretor das contas de vida, PE, Integridade, proteção e
Defesa, dos nomes de Caminho, Trilha e Origem e dos avisos da ficha (`src/closure_bot/ficha_corretor.py`), estrutura
das regras de campanha e do registro de custom aprovado, e o `/ficha analisar` com o painel de resposta, ligado em 14/10.
Avanço posterior: contas parciais de montagem de feitiços e entidades em `ficha_magia.py`; Classe e PE nominal,
limites de peças/Restrições e dano-base quando determinado, nível/Classe e entrada/retorno das entidades.
Falta completar as entradas da ANALISE e conferir as contas restantes, além das 3 a 5 fichas reais com habilidades.
As quatro cópias de teste iniciais tinham as cartas vazias. Depois, Mizuki autorizou criar cópias preenchidas:
quatro casos foram calculados no Google, relidos e confirmados por ele no Discord; são casos montados,
sem substituir personagens reais em uso. Em 15/10, seguiram equipamento, extras da Principal e trunfos da domada,
com parada antes de TR/perícias. Cobertura parcial e validação em
`pesquisa/validacao/2026-10-15-ficha-equipamento-trunfos/relatorio.txt`.*

Mizuki adiou o cadastro e a aprovação de conteúdo próprio para a etapa CONFIGURAÇÃO da ficha (14/10).
Não registrar comandos de campanha nem criar novas tabelas no bot nesta etapa. O desenho deve ser retomado junto da
CONFIGURAÇÃO; uma regra ou aprovação declarada pelo jogador não vale automaticamente como decisão do mestre.
Entradas necessárias e limites atuais: `dados/ficha/ENTRADAS-FALTANTES-ANALISE.txt`.

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

O contrato é a aba `ANALISE` da própria ficha (B47, fase 1, testada no Sheets em 14/10/2026), descrito em
[`dados/ficha/CONTRATO-ABA-BOT.md`](../dados/ficha/CONTRATO-ABA-BOT.md) (versão 3), com a lista de chaves gerada da
ficha em `dados/ficha/analise-chaves.tsv`.

- Quatro colunas: chave · valor · célula · parte (`cabeçalho`, `entrada`, `resultado`, `aviso`); 2.650 chaves.
- Chave minúscula, sem acento, com ponto entre os níveis e o número do item nas listas (`feitico.7.pecas`).
- Valores como texto; o bot converte (vírgula decimal, 1/0, vazio = não preenchido).
- Lida do `.xlsx` baixado do Google ou pelo link aberto (CSV da aba).
- `formato.versao` diferente da conhecida recebe aviso, não correção.
- O bot nunca acredita na ficha: regras da campanha vêm do bot, contas são refeitas, avisos são só o primeiro filtro.

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
