# Como a comunidade de roleplay "alimenta" bots de personagem: cards, diálogos de exemplo, lorebooks, estrutura de prompt e samplers (estado em outubro de 2026, aplicado à Closure de Arknights em PT-BR)

Observações de método, válidas para o arquivo inteiro:

- Data da coleta: 12/10/2026. Citações de documentação foram parafraseadas em português; os termos técnicos ficaram no original.
- Fontes que NÃO consegui abrir e que, portanto, só aparecem por referência indireta: o guia PList + Ali:Chat do Trappu (a página carrega por JavaScript e voltou vazia), o documento do template JED (Google Docs devolveu erro), o artigo do RP|Fiend sobre presets de Claude (falha de download) e o Reddit (nenhum tópico de r/SillyTavernAI, r/JanitorAI_Official, r/CharacterAI ou r/PygmalionAI foi recuperado diretamente). Onde uso esses nomes, o dado veio de outra página que os cita.
- `aituts.com` e `tavernsprite.com` são blogs comerciais de 2026 que promovem produto próprio. Uso os dois como retrato da prática corrente, não como autoridade.
- Marcação de idade: **[ANTIGO]** = conselho escrito para modelos locais de contexto pequeno (2023, 2k–8k tokens), que pode não valer para Claude/Gemini/GPT atuais.

## 1. Anatomia do character card (SillyTavern, Character Card V2 e V3): o que cada campo faz e onde cai no prompt

### Takeaway
O card é um conjunto de campos de texto que o frontend concatena numa ordem fixa: instrução de sistema, descrição/personalidade/cenário (sempre presentes), exemplos de diálogo (descartáveis), histórico do chat e, por último, as post-history instructions. Para um bot próprio de Discord, o que importa é reproduzir essa ordem e a distinção "permanente vs. temporário", não o formato de arquivo.

### Cited Findings
- No SillyTavern só o nome é obrigatório. Description entra em todo prompt e deve conter os fatos importantes; pode ter qualquer tamanho e formato (texto livre ou pseudo-diálogo). — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- Tokens permanentes (enviados em toda geração): nome, Description, Personality, Scenario. Temporários: First Message (enviada uma vez, no início) e Examples of dialogue (ficam só enquanto houver espaço; são empurrados para fora bloco a bloco conforme o histórico cresce, a menos que se force a permanência). — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- A documentação afirma que o modelo tende a pegar estilo e tamanho de resposta da First Message mais do que de qualquer outra coisa. — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- Formato dos exemplos: cada bloco começa com `<START>` (marcador que não vai ao modelo; em Chat Completion é trocado pelo texto do utility prompt "New Example Chat"), e as falas usam `{{char}}:` e `{{user}}:`. — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- Campos avançados: Main Prompt (override do system prompt, se "Prefer Char. Prompt" estiver ligado), Post-History Instructions (override, se "Prefer Char. Instructions"), `{{original}}` para reaproveitar o prompt padrão dentro do override, Creator's Notes (não entra no prompt), Character's Note (injeção dentro do chat em profundidade fixa, com papel User/System/Assistant; profundidade 0 = depois da última mensagem), Talkativeness (probabilidade de falar em grupo, padrão 50%). — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- Ordem padrão dos blocos no Prompt Manager (Chat Completion): Main Prompt → World Info (before) → Persona Description → Char Description → Char Personality → Scenario → Enhance Definitions → Auxiliary Prompt → World Info (after) → Chat Examples → Chat History → Post-History Instructions. As Post-History Instructions ficam no fim e são a última coisa enviada ao modelo. — [SillyTavern Docs, Prompt Manager](https://docs.sillytavern.app/usage/prompts/prompt-manager/)
- Prompts podem ser "Relative" (seguem a ordem da lista) ou "In-Chat" (inseridos dentro do histórico numa profundidade e com um papel; profundidade 0 = após a última mensagem). — [SillyTavern Docs, Prompt Manager](https://docs.sillytavern.app/usage/prompts/prompt-manager/)
- Character Card V2 (`spec: 'chara_card_v2'`): mantém os seis campos da V1 (`name`, `description`, `personality`, `scenario`, `first_mes`, `mes_example`) dentro de `data` e acrescenta `creator_notes`, `system_prompt`, `post_history_instructions`, `alternate_greetings`, `character_book`, `tags`, `creator`, `character_version`, `extensions`. — [Character Card V2 spec](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)
- Regras da V2: `creator_notes`, `creator` e `character_version` não podem ser usados no prompt; `system_prompt` substitui por padrão o system prompt global do usuário; `post_history_instructions` substitui por padrão o slot "ujb/jailbreak" (nome histórico da comunidade para a instrução que vem depois do histórico); ambos precisam aceitar `{{original}}`; `alternate_greetings` vira "swipes" extras da primeira mensagem; `character_book` deve ser usado por padrão e ter precedência sobre o world book do usuário. — [Character Card V2 spec](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)
- Entradas do `character_book` na V2: `keys`, `content`, `enabled`, `insertion_order`, `priority` (as de menor prioridade caem primeiro quando o orçamento estoura), `selective` + `secondary_keys`, `constant`, `position` (`before_char`/`after_char`), `case_sensitive`; no nível do livro: `scan_depth`, `token_budget`, `recursive_scanning`. — [Character Card V2 spec](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)
- Character Card V3 (`spec: 'chara_card_v3'`, `spec_version: '3.0'`): acrescenta `assets`, `nickname` (substitui `{{char}}` no lugar de `name`), `creator_notes_multilingual` (por código ISO 639-1), `source`, `group_only_greetings`, `creation_date`, `modification_date`; no lorebook, `use_regex` e "decorators" escritos dentro do `content` (`@@depth`, `@@role`, `@@position`, `@@activate_only_after`...). Embutido em PNG no chunk tEXt `ccv3`, ou em arquivo `.charx` (zip com `card.json`). — [Character Card V3 spec](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md) (lido pelo espelho [jsDelivr](https://cdn.jsdelivr.net/gh/kwaroran/character-card-spec-v3@main/SPEC_V3.md))
- Em 2026 o SillyTavern lê V2 e V3. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)

### Inferences
- O prompt único "Você é a Closure... regras: ..." da tentativa anterior ocupava só o slot do Main Prompt. Faltavam os três slots que a comunidade considera decisivos para a voz: First Message, Chat Examples e Post-History Instructions.
- Num bot de Discord escrito à mão, vale guardar a personagem num JSON com os nomes de campo da V2. Isso permite testar o mesmo card no SillyTavern antes de programar e reaproveitar cards e lorebooks da comunidade.
- `nickname` (V3) e `{{user}}` precisam de tratamento próprio no Discord, porque há vários usuários no mesmo canal (ver seção 9, variável `{{random_user_N}}` do Character.AI).

### Gaps
- Não confirmei se os decorators (`@@depth` etc.) são novidade da V3 ou herança do RisuAI; a spec não deixa explícito.
- A documentação do Prompt Manager não descreve como o orçamento de tokens decide o que cortar primeiro; o corte "exemplos antes do histórico" vem da página Character Design.

## 2. Formatos de escrita de card e seus trade-offs (prosa, W++, PList, Ali:Chat, híbrido, JSON/XML/Markdown, JED/JED+)

### Takeaway
A recomendação de 2026 para modelos grandes é prosa simples e concreta mais diálogos de exemplo; W++ é tratado como obsoleto por gastar tokens sem ganho, e PList + Ali:Chat sobrevive como opção de economia de tokens para modelos locais. Estrutura leve (cabeçalhos Markdown ou tags XML) serve para separar seções, não para descrever personalidade.

### Cited Findings
- Guia de 2026: escrever em prosa, não em pseudo-código, e declarar traços de forma positiva em vez de proibições. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Artigo de setembro de 2026: prosa simples é o recomendado para modelos modernos; formatos estruturados antigos como W++ ainda circulam, mas não são mais necessários e costumam desperdiçar tokens. — [TavernSprite, Card Fields Explained (11/09/2026)](https://tavernsprite.com/blog/sillytavern-character-card-fields/)
- Ali:Chat: a ideia central é usar o próprio diálogo como formato para expressar e reforçar traços. É um guia de estilo, não um template fixo, e pode ser combinado com PList, Boostyle ou W++. O formato de entrevista é opcional. O autor admite que dá mais controle, mas depende mais da qualidade da escrita de quem faz o card. — [AliCat, Ali:Chat v1.5](https://rentry.co/alichat)
- No Ali:Chat a divisão é: Description = diálogos de exemplo dos traços centrais (permanente); First Message = monta a cena (temporária); Examples of dialogue = trocas complementares (temporárias). Traços podem ficar implícitos no jeito de falar e agir. — [AliCat, Ali:Chat Style (Google Doc)](https://docs.google.com/document/d/1qvcvZWhp24p14dsMlmj7vN4cM5RTDSj0gLaZSl1PPO8/mobilebasic)
- **[ANTIGO]** MinimALIstic / Ali:Chat Lite (kingbri, publicado em 11/06/2023, editado em 09/10/2023): a Description contém só exemplos Ali:Chat (limite "suave" de 300–600 tokens; 2 exemplos longos ou 3 curtos, o autor prefere 3 curtos), e o PList (`[Character: traços; ...]`) vai para o Author's Note do personagem, com os traços mais importantes no fim da lista. Um card de exemplo caiu de ~1300 para 599 tokens. O próprio guia avisa que esses guias desatualizam rápido. — [kingbri, MinimALIstic](https://rentry.co/kingbri-chara-guide)
- O alvo de 500–600 tokens permanentes ainda é citado em 2026 como meta para uso local; abaixo de 1.000 tokens permanentes é dado como confortável em qualquer modelo. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Outra referência de 2026: Description focada em 300–600 tokens e campos permanentes abaixo de ~1.000–1.500 tokens; Personality com 4–6 traços, opcional, sem repetir a Description. — [TavernSprite, Card Fields Explained](https://tavernsprite.com/blog/sillytavern-character-card-fields/)
- **[ANTIGO]** A conta que originou a obsessão por tokens: com limite de 2.048 tokens, uma definição de 1.000 tokens corta a "memória" do chat pela metade. — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- JED: uma página de recursos de botmaking descreve o Character Creation Guide (JED) como template utilizável em quase todo LLM, em seções com bullet points que se pode acrescentar ou remover, pensado principalmente em torno do JLLM do Janitor. — [The Information Desk (carrd)](https://the-library.carrd.co/)
- Um gerador de cards de 2026 lista como formatos em uso: Prose, Attributes, AliChat, JED/JED+, Plaintext e W++. — [claude-plugins.dev, character-card-v3-generator](https://claude-plugins.dev/skills/@davidgibbons/sillytavern-skills/character-card-v3-generator)
- Sobre estrutura: a Google recomenda delimitar seções com tags XML (ex.: `<role>`) ou cabeçalhos Markdown e usar um único formato de forma consistente. A Anthropic recomenda tags XML para separar instruções, contexto e exemplos. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies); [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- A Anthropic observa que o estilo de formatação do prompt influencia o estilo da resposta (ex.: tirar Markdown do prompt reduz Markdown na saída). — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Inferences
- Para Gemini/Claude/GPT com contexto de centenas de milhares de tokens, a razão de ser de W++ e de PList (economizar tokens) desapareceu. O que restou de útil do PList + Ali:Chat é a segunda metade: os diálogos.
- Um card em lista de adjetivos ou em bullets tende a puxar respostas com cara de lista e de ficha, pelo efeito "estilo do prompt contamina a saída" descrito pela Anthropic. Isso combina com o sintoma relatado (respostas genéricas).
- Formato sugerido pela convergência das fontes para a Closure: (a) um parágrafo ou dois de prosa com fatos concretos; (b) uma seção curta sobre o jeito de falar; (c) 3–6 trocas de exemplo em PT-BR; (d) tags XML ou cabeçalhos só para separar essas partes.

### Gaps
- Não li o guia do Trappu nem o documento JED/JED+ diretamente; a descrição de JED+ e suas diferenças para o JED ficaram sem fonte.
- Não encontrei teste controlado comparando formatos (prosa vs. W++ vs. PList) em modelos de 2025–2026. O consenso é de prática de comunidade e de blogs, não de medição.
- Não obtive tópicos do Reddit de 2025–2026 para confirmar o consenso com as palavras da comunidade.

## 3. "Show, don't tell": por que exemplos moldam a voz mais do que listas de traços; quantos, de que tamanho, como evitar cópia

### Takeaway
As três documentações oficiais (Anthropic, Google, SillyTavern) e os guias de comunidade concordam que exemplos concretos orientam tom e formato melhor que instrução abstrata; a faixa recorrente é de 3 a 5 exemplos curtos e variados. O risco conhecido é o sobreajuste (o modelo repetir os exemplos), combatido com variedade e pouca quantidade.

### Cited Findings
- Anthropic: exemplos estão entre as formas mais confiáveis de dirigir formato, tom e estrutura; devem ser relevantes, diversos (para o modelo não captar padrões indesejados) e delimitados por tags `<example>`; a dica é incluir de 3 a 5. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Anthropic: dar exemplos da saída desejada é mais eficaz do que instruções abstratas. — [Anthropic, Increase output consistency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency)
- Google: recomenda sempre incluir exemplos few-shot; prompts sem eles tendem a ser menos eficazes; exemplos claros podem até substituir instruções; exemplos em excesso fazem o modelo sobreajustar; a formatação deve ser idêntica entre os exemplos; exemplos de respostas curtas puxam o modelo para respostas curtas. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- SillyTavern: a First Message é o sinal mais forte de estilo e tamanho. — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- Um guia de 2026 chama a saudação de campo mais importante e avisa que terminá-la com pergunta treina um ciclo de pergunta e resposta. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Quantidade segundo guias: 3 a 5 exemplos afiados, cada um mostrando uma faceta distinta da voz, valem mais que uma transcrição longa; "parede de diálogo de exemplo" é listada como erro comum. — [TavernSprite, Card Fields Explained](https://tavernsprite.com/blog/sillytavern-character-card-fields/)
- Ali:Chat: poucos exemplos, deixando o modelo completar o personagem; o que entra é o que sai (exemplos interessantes geram respostas interessantes); para respostas mais longas, exemplos mais longos; variar verbos e vocabulário entre exemplos; deixar os exemplos em aberto. — [AliCat, Ali:Chat v1.5](https://rentry.co/alichat)
- Contra repetição dos exemplos, o mesmo guia sugere reduzir a sobreposição entre diálogos e apagar o texto que entrou em loop, porque o modelo gosta de criar padrões. — [AliCat, Ali:Chat v1.5](https://rentry.co/alichat)
- Character.AI: o uso mais comum da Definition é incluir diálogos de exemplo; usar nomes `{{random_user_1}}`, `{{random_user_2}}` nos exemplos ajuda o personagem a entender que aquelas conversas são distintas da conversa real. — [Character.AI, Definition](https://book.character.ai/character-guide/character-attributes/definition.md)
- Descrição: guia de 2026 pede detalhes concretos e específicos em vez de adjetivos vagos. — [TavernSprite, Card Fields Explained](https://tavernsprite.com/blog/sillytavern-character-card-fields/)
- Pesquisa de 2026: anonimizar o nome do personagem reduz bastante o desempenho de roleplay de personagens fictícios, o que indica que os modelos se apoiam em conhecimento memorizado sobre o personagem; acrescentar informação de personalidade melhora a fidelidade de forma consistente. — [Rethinking Role-Playing Evaluation (alphaXiv 2603.03915)](https://www.alphaxiv.org/abs/2603.03915)

### Inferences
- Por que a lista de adjetivos falha: "cínica, pragmática, obcecada por LMD" descreve milhares de personagens. O modelo preenche a lacuna com a voz média que conhece para esses adjetivos, e o resultado é o tom genérico relatado. Falas reais carregam ritmo, tamanho de frase, interjeições e tipo de piada, coisas que um adjetivo não transmite.
- A Closure é personagem de nicho, com muito menos texto memorizado pelo modelo do que um protagonista famoso. Pelo achado da anonimização, o card precisa trazer a voz por conta própria; apoiar-se só no nome não basta.
- Para evitar cópia literal: exemplos cobrindo situações diferentes (venda, reclamação de trabalho, explicação técnica, provocação, momento sério), aberturas de frase diferentes, nenhum bordão repetido em mais de um exemplo, e rotação de um subconjunto dos exemplos a cada chamada da API (num bot próprio isso é trivial).
- Num bot de Discord sem "First Message", o papel de âncora de estilo passa para os exemplos e para as primeiras respostas do histórico. Vale semear o histórico com uma ou duas trocas curtas escritas à mão.

### Gaps
- Não encontrei medição publicada do efeito "exemplos vs. lista de traços" especificamente em roleplay; a evidência é a recomendação geral de few-shot dos provedores mais a prática da comunidade.
- Os benchmarks encontrados não isolam o número ideal de exemplos de diálogo como variável.
- Não li a seção de anti-padrões do guia do Trappu sobre cópia de exemplos.

## 4. Card para personagem CANÔNICO: mineração de material-fonte, padrões de fala, o que a personagem não diria; onde está o material da Closure; PT-BR

### Takeaway
O material da Closure está na wiki.gg em inglês (subpáginas File, Dialogue, Story, Trivia) e nos leitores de roteiro que extraem o texto do jogo em EN/JP/KR/CN; não encontrei localização oficial nem tradução de fã em PT-BR, então a voz terá de ser adaptada. Atenção: as páginas File e Dialogue da wiki voltaram com falas em chinês na minha leitura, sinal de que parte do conteúdo de operadora pode ainda não ter texto oficial em inglês.

### Cited Findings
- Subpáginas da personagem na Arknights Terra Wiki: File, Story, Overview, Dialogue, Gallery, Trivia. — [arknights.wiki.gg, Closure/File](https://arknights.wiki.gg/wiki/Closure/File)
- Perfil (File): engenheira-chefe da Rhodes Island e chefe do departamento de compras/Procurement, acumulando outros departamentos; exterior brincalhão e de fala solta com senso de responsabilidade de veterana; curiosa, defende compartilhamento aberto de conhecimento (ideal open-source) e rejeita hierarquia rígida e status herdado; descrita também como pouco diligente por natureza e fácil de irritar; uma das integrantes mais antigas, vinda da Babel (seguiu Theresa e o Doutor); idade exata não informada. — [arknights.wiki.gg, Closure/File](https://arknights.wiki.gg/wiki/Closure/File)
- Fatos úteis para a voz: enquanto Kal'tsit esteve fora, Closure tomou decisões finais de vários departamentos; Doutor e Amiya barraram um esquema de propaganda enganosa dela e passaram a conferir as transações do Procurement; a loja funciona por ordem de chegada; ela desconfia dos ideais de "pureza" da própria raça e cita Warfarin entre os poucos da raça de quem não desgosta; nos primórdios de Kazdel projetou estações-base caseiras num sótão. — [arknights.wiki.gg, Closure/File](https://arknights.wiki.gg/wiki/Closure/File)
- Vozes: japonesa Manami Numakura, chinesa Hou Xiaofei. — [arknights.wiki.gg, Closure](https://arknights.wiki.gg/wiki/Closure)
- Página Dialogue: categorias de fala de operadora (Appointed as Assistant, Talk 1–3, Talk after Promotion 1–2, Talk after Trust Increase 1–3, Idle, Onboard, Greeting, Tap, Trust Tap, Assigned to Facility, falas de batalha, resultados, aniversário, Ano Novo), com áudio JP e CN. O texto capturado estava em chinês. — [arknights.wiki.gg, Closure/Dialogue](https://arknights.wiki.gg/wiki/Closure/Dialogue)
- Padrões de fala observados nessa página: assuntos recorrentes são dinheiro e o Procurement (empurra lanches e descontos), reclamação de excesso de trabalho de engenharia, piadas com a herança vampírica (viver de café em vez de sangue), menções a Kal'tsit e Amiya; humor autodepreciativo, provocador e exagerado; suspiros, reticências arrastadas, risadinhas; refere-se a si mesma como a "irmã mais velha fofa". Exemplo curto de fala, oferecendo um biscoito sabor churrasco: "烧烤味饼干，来一片？" — [arknights.wiki.gg, Closure/Dialogue](https://arknights.wiki.gg/wiki/Closure/Dialogue)
- Página Story (resumos, sem roteiro completo; Episódios 10–15 sem conteúdo e Episódio 09 marcado como stub): aparições em Darknights Memoir (dias de Babel), Operational Intelligence, Heart of Surging Flame, Vigilo (mantém o PRTS), Preluding Lights, Episódio 09 (o velho amigo Dijkstra e uma invasão de segurança), Episódio 16, Ancient Forge, e nos operator records de Shirayuki, Mayer, THRM-EX, Castle-3, Vulcan, Weedy, Hibiscus, Executor the Ex Foedere, Robin e Kal'tsit; lista também "Closure's Secret Files". — [arknights.wiki.gg, Closure/Story](https://arknights.wiki.gg/wiki/Closure/Story)
- Roteiros completos: o Arknights Story Text Reader (site em https://astr.pages.dev) permite ler o texto de história por evento nos servidores CN, JP, KR, EN e TW, com dados brutos de `Kengxxiao/ArknightsGameData`. — [050644zf/ArknightsStoryTextReader](https://github.com/050644zf/ArknightsStoryTextReader)
- Idiomas oficiais: a Yostar publica os servidores japonês, coreano e inglês, chamados em conjunto de servidor Global. — [endfield.wiki.gg, Arknights](https://endfield.wiki.gg/wiki/Arknights)
- Para montar uma base de conhecimento a partir de wiki, o SillyTavern tem raspador de Fandom (via plugin de servidor) e de páginas web no Data Bank. — [SillyTavern Docs, Data Bank](https://docs.sillytavern.app/usage/core-concepts/data-bank/)
- Existe uma tradução em português da documentação do SillyTavern (apareceu nos resultados de busca; não verifiquei quem mantém nem se está atualizada). — [pt.sillytavern.wiki, Design de Personagem](https://pt.sillytavern.wiki/usage/core-concepts/characterdesign/)

### Inferences
- Roteiro de mineração sugerido pelas fontes: (1) File e Trivia para fatos e relações; (2) Dialogue para a voz "do dia a dia", que é o registro mais próximo de um chat; (3) roteiros de evento e operator records no ASTR para ver a Closure conversando com outros personagens em trocas reais, que são a melhor matéria-prima para diálogos de exemplo.
- Ficha de voz a extrair, com base no que a página Dialogue mostra: como chama o Doutor; como se refere a si mesma; tamanho típico de frase; interjeições e reticências; os dois ou três temas a que sempre volta (dinheiro, loja, cansaço de engenharia, café/sangue); tipo de humor; e quando ela fica séria (Babel, Theresa, responsabilidade de veterana).
- "O que ela NÃO diria", derivado do perfil: não fala como atendente prestativa nem em tom corporativo; não é cínica amarga (o exterior é brincalhão, o que contradiz o "cínica, pragmática" do prompt antigo); não reverencia hierarquia nem pureza de linhagem; não dá aulas longas e organizadas sem reclamar ou fazer piada no meio. Escrever isso em forma positiva (o que ela faz no lugar) segue a recomendação dos guias de 2026.
- Adaptação para PT-BR: sem texto oficial em português, o caminho é transcriar. Escrever os diálogos de exemplo já em português brasileiro coloquial, fixando decisões de tradução (ex.: "Doutor"/"Doutora"; manter LMD, Rhodes Island, Originium, PRTS no original) num glossário dentro do card. Como o estilo do prompt contamina a saída e os exemplos few-shot devem ter o formato da resposta desejada, exemplos em inglês com a instrução "responda em português" tendem a produzir português traduzido, e não fala natural.
- Vale conferir as falas no áudio/texto japonês e no chinês, além do inglês: a tradução inglesa de Arknights tem escolhas próprias de tom, e a adaptação para o português pode partir do original.
- O termo da raça variou nas fontes (a leitura da wiki trouxe "Blood Demon (血魔)"; o briefing usa "vampira Sarkaz"). Convém fixar no card o termo que a comunidade brasileira reconhece.

### Gaps
- Não encontrei tradução de fã em PT-BR do roteiro de Arknights nem glossário da comunidade brasileira; a busca só devolveu projetos de outros jogos. Ausência de resultado não prova que não exista (Discords e grupos fechados não são indexados).
- Não confirmei por que as páginas File e Dialogue vieram em chinês. Hipótese não verificada: a Closure como operadora jogável ainda não tem texto oficial em inglês no servidor Global. É preciso abrir as páginas e conferir.
- Não consultei a PRTS wiki (chinesa) nem a página Trivia; não verifiquei se o ASTR permite navegar por operator record.
- Não achei guia de comunidade específico sobre adaptar a voz de personagem entre idiomas; o que está em Inferences é dedução a partir das recomendações gerais de few-shot.
- Limite de direitos autorais: o roteiro do jogo é protegido. As notas apontam onde o material está; o card privado pode usar falas curtas como referência, mas não convém publicar transcrições longas.

## 5. Lorebooks / World Info / character book e comparação com RAG clássico

### Takeaway
Lorebook é um dicionário acionado por palavra-chave: o que está no card vai em todo prompt, o que está no lorebook entra só quando o assunto aparece. Para a Closure, a voz e a identidade ficam sempre ligadas, e o lore de Terra (facções, eventos, outros operadores) vai para entradas curtas por palavra-chave; RAG vetorial sobre a wiki é alternativa menos previsível.

### Cited Findings
- World Info funciona como dicionário dinâmico: só insere entradas cujas chaves aparecem no texto escaneado. Chaves separadas por vírgula, sem diferenciar maiúsculas por padrão, com suporte a regex (`/padrão/flags`). — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Chaves secundárias (Optional Filter) com lógicas AND ANY, AND ALL, NOT ANY, NOT ALL. Estratégias: Constant (sempre entra), Keyword (só com a chave) e Vectorized (por similaridade de embedding). — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Scan Depth define quantas mensagens recentes são examinadas. Recursão: o conteúdo de uma entrada pode ativar outras; há opções por entrada para não ser ativada por recursão, impedir recursão adicional e limitar os passos. — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Posições de inserção: Before Char Defs (impacto moderado), After Char Defs (impacto maior), antes/depois dos Example Messages (a entrada é tratada como bloco de exemplo), topo/fundo do Author's Note, `@ D` (profundidade no chat com papel system/user/assistant; profundidade 0 = fim do prompt) e Outlet (macro `{{outlet::Nome}}`). Insertion Order maior fica mais perto do fim do contexto e influencia mais. — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Orçamento: limite de tokens do World Info; esgotado, nenhuma outra entrada é ativada. Constantes entram primeiro. Há também Probability, Inclusion Groups (só uma entrada do grupo entra) e efeitos temporais Sticky/Cooldown/Delay contados em mensagens. — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Ativação vetorial: substitui apenas a checagem de palavra-chave; usa o ajuste "Query messages" em vez do Scan Depth; os resultados não são totalmente previsíveis porque dependem do modelo de embedding. — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Ressalva da documentação: o World Info orienta o modelo, mas não garante que o conteúdo apareça na resposta. — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Um lorebook primário pode ser vinculado ao personagem e é exportado junto com o card; há também lorebooks de persona e de chat. — [SillyTavern Docs, World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/)
- Prática de 2026: lugares e facções pertencem ao lorebook, não ao card; scan depth típico de 2 a 4; no máximo duas ou três entradas constantes. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- **[ANTIGO]** World Info Encyclopedia (kingbri, com Alicat e Trappu; outubro de 2023): incluir como chaves todos os termos ligados ao assunto (nome, apelido, tipo); usar chaves secundárias para estreitar o gatilho; entradas de lore combinam descrição curta com um exemplo de como o personagem pensa sobre o assunto; mover o PList do personagem para uma entrada Constant em profundidade 4; quanto menor a profundidade, mais peso; marcar coisas demais como importantes causa vazamento; valores do autor: scan depth 4, orçamento de 45% do contexto. — [World Info Encyclopedia](https://rentry.co/world-info-encyclopedia)
- RAG no SillyTavern (Data Bank + Vector Storage): documentos são divididos em chunks (tamanho em caracteres, com sobreposição), vetorizados por um provedor de embedding e recuperados por similaridade com as últimas mensagens; limiar de score sugerido entre 0,2 (mais solto) e 0,5 (mais focado); posição de injeção segue as mesmas regras de Author's Note e World Info; escopos global, por personagem e por chat; anexos de personagem não são exportados com o card. — [SillyTavern Docs, Data Bank](https://docs.sillytavern.app/usage/core-concepts/data-bank/)
- Anthropic recomenda recuperação (retrieval) para manter consistência de contexto em chatbots, ancorando as respostas num conjunto fixo de informação. — [Anthropic, Increase output consistency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency)

### Inferences
- Lorebook vs. RAG: o lorebook é curado e determinístico (você escreve a entrada e escolhe o gatilho); o RAG sobre wiki bruta é automático, mas traz chunks em tom enciclopédico e nem sempre os certos. Para um bot de um único personagem com lore finito, 30–80 entradas escritas à mão em PT-BR tendem a dar mais fidelidade que vetorizar a wiki inteira.
- A dica da Encyclopedia de escrever a entrada como "fato + como a personagem fala disso" é a mais valiosa para personagem canônico: a entrada "Kal'tsit" deveria trazer o que a Closure acha dela e como se refere a ela, e não a biografia da Kal'tsit.
- Em português, as chaves precisam cobrir variações (com e sem acento, apelidos, nome em inglês e em português). A correspondência por palavra inteira ajuda a evitar gatilhos falsos.
- Com contexto grande e personagem único, é viável deixar uma parte maior do lore sempre ligada. O limite prático deixa de ser tokens e passa a ser diluição: quanto mais enciclopédia no prompt, mais o tom enciclopédico contamina a fala.
- Para um bot próprio, implementar o lorebook por palavra-chave são poucas linhas (procurar chaves nas últimas N mensagens e inserir o conteúdo num ponto fixo), sem banco vetorial.

### Gaps
- A documentação oficial não compara World Info com Data Bank; a comparação acima é inferência.
- Não encontrei avaliação de 2025–2026 medindo lorebook por palavra-chave contra RAG vetorial em fidelidade de personagem.
- Os números da World Info Encyclopedia (scan depth, 45%) são de 2023 e de modelos locais; não achei equivalentes para Gemini/Claude.

## 6. Montagem do prompt e efeitos de posição: system prompt, Author's Note, post-history, depth injection, prefill; persona drift

### Takeaway
Texto perto do fim do contexto pesa mais na próxima resposta, e por isso a comunidade põe a voz e o formato em post-history instructions ou notas em profundidade baixa, e não só no system prompt. O desvio de persona em conversas longas é documentado em pesquisa, e a reinjeção periódica de instruções reduz o problema sem eliminá-lo; prefill deixou de existir nos Claude 4.6 em diante.

### Cited Findings
- Author's Note insere um trecho em qualquer posição e frequência; quanto mais perto do fim do prompt, maior o impacto na próxima resposta. Profundidade 0 = fim do histórico; profundidade 4 = quarta entrada a partir do fim; frequência 1 = em toda mensagem. Exemplos de uso da própria documentação: pedir um estilo de escrita e relembrar as instruções do início. — [SillyTavern Docs, Author's Note](https://docs.sillytavern.app/usage/core-concepts/authors-note/)
- Post-History Instructions ficam no fim da lista e são a última coisa enviada ao modelo. — [SillyTavern Docs, Prompt Manager](https://docs.sillytavern.app/usage/prompts/prompt-manager/)
- Character's Note fica em profundidade estática no histórico, independentemente do tamanho do chat. — [SillyTavern Docs, Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- "Jailbreak"/"ujb" é só o nome histórico que a comunidade dá ao slot pós-histórico; a spec V2 o formaliza como `post_history_instructions`. — [Character Card V2 spec](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)
- Google (Gemini 3): persona, restrições e formato de saída vão na System Instruction; o contexto longo vem primeiro e as instruções específicas vão no final do prompt, com uma frase de transição. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- Anthropic: dados longos no topo e a pergunta/instrução no fim; nos testes da empresa, colocar a consulta no fim melhorou a qualidade em até 30%, sobretudo com vários documentos. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Prefill: a partir dos modelos Claude 4.6, prefill no último turno do assistente não é mais suportado e a requisição devolve erro 400; modelos anteriores ainda aceitam, e mensagens de assistente em outros pontos da conversa não são afetadas. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Substituto oficial do prefill para consistência de papel: em conversas muito longas, injetar no turno do usuário os lembretes que antes iam como prefill. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Gemini aceita terminar o prompt com um prefixo de resposta para o modelo continuar o padrão. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- No SillyTavern, "Continue Prefill" envia o texto como mensagem de assistente e pode não funcionar em todas as fontes de Chat Completion. — [SillyTavern Docs, Prompt Manager](https://docs.sillytavern.app/usage/prompts/prompt-manager/)
- Persona drift: Li et al. (2024) mediram queda significativa de aderência às instruções em cerca de oito rodadas de conversa (LLaMA2-chat-70B), atribuída ao decaimento de atenção sobre o prompt inicial. — [Measuring and Controlling Persona Drift in Language Model Dialogs (arXiv 2402.10962)](https://arxiv.org/abs/2402.10962)
- Estudo de 2026 (1.200 conversas de 28 turnos, quatro LLMs): reinjetar a persona reduziu o drift em 35–38%; lembretes reflexivos, em 22–27%; instruções específicas sobre o comportamento que desviou, geradas por um monitor, em 87%. Nenhuma intervenção zerou o drift, e escolher o momento de forma adaptativa não superou o agendamento fixo. — [Prompting Against Persona Drift (arXiv 2609.24532)](https://arxiv.org/abs/2609.24532)
- Anthropic, para manter o personagem: definir papel e personalidade no system prompt com detalhes de personalidade, histórico e manias, e preparar o modelo com uma lista de cenários comuns e as respostas esperadas. — [Anthropic, Increase output consistency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency)

### Inferences
- Montagem sugerida para o bot da Closure, na ordem: (1) system: quem ela é, em prosa, mais ficha de voz e glossário PT-BR; (2) entradas de lorebook ativadas; (3) exemplos de diálogo; (4) histórico do canal; (5) um lembrete curto de voz e formato colado ao fim (junto da última mensagem do usuário, já que prefill não existe mais em Claude e a recomendação oficial é usar o turno do usuário).
- O estudo de 2026 sugere que um lembrete específico rende mais que repetir o card inteiro. Exemplo de forma: "frases curtas, reclame do trabalho, puxe a conversa para a loja", em vez de "lembre-se de quem você é".
- O drift também é realimentado pelo próprio histórico: uma resposta longa e com cara de assistente vira exemplo para as seguintes. Truncar ou resumir o histórico antigo e manter os exemplos canônicos sempre presentes (sem deixá-los cair, como acontece por padrão no SillyTavern) atua nessa causa.
- Em APIs com cache de prompt, o bloco fixo (card + exemplos) deve vir primeiro e o variável (lorebook, histórico, lembrete) depois. A ordem recomendada para qualidade coincide com a ordem boa para custo.

### Gaps
- O estudo de 2024 usou um modelo já antigo; não encontrei medição de drift nos modelos de fronteira de 2026 em roleplay de personagem fictício (o estudo de 2026 simula estudantes com TDAH, não personagens de ficção).
- Não achei documentação oficial sobre prefill na API do Gemini em 2026 além da técnica de prefixo de resposta.
- Não verifiquei na documentação do Gemini o comportamento de cache implícito/explícito.

## 7. Matar "AI-ismos" e tom de assistente: causas, correções e samplers

### Takeaway
As causas apontadas são prompt em estilo de assistente, proibições em negativo, respostas longas que se autoalimentam e samplers mal ajustados; as correções mais citadas são exemplos curtos no registro de chat, instrução positiva de estilo, teto de tamanho e pós-processamento. Em APIs fechadas quase não há sampler para mexer em 2026 (Claude Opus recente rejeita `temperature`/`top_p`/`top_k`; a Google pede para não baixar a temperatura do Gemini 3), então o trabalho passou para o prompt.

### Cited Findings
- Proibição em negativo é listada como erro comum: os modelos se agarram às palavras da proibição e fazem a coisa mesmo assim. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Anthropic: dizer o que fazer em vez do que não fazer (ex.: pedir parágrafos de prosa corrida em vez de "não use markdown"). — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Anthropic: os modelos recentes respondem mais ao system prompt; linguagem agressiva ("CRITICAL: You MUST...") passou a causar exagero no comportamento pedido, e a orientação é usar linguagem normal. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- OpenAI (guia do GPT-5.5): modelos novos precisam de menos andaimes de processo; prompts superespecificados acrescentam ruído e produzem respostas mecânicas. — [OpenAI, GPT-5.5 prompting guide](https://developers.openai.com/api/docs/guides/prompt-guidance.md) (lido só pelo resumo da busca)
- Tamanho: o modelo copia o estilo da primeira mensagem (curta e seca gera respostas curtas e secas); recomendação de máximo de 300–500 tokens de resposta para roleplay narrativo. — [TavernSprite, Card Fields Explained](https://tavernsprite.com/blog/sillytavern-character-card-fields/); [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Google: o limite de tokens de saída corta o tamanho (100 tokens ≈ 60–80 palavras); restrições explícitas funcionam; o Gemini 3 já responde de forma direta por padrão. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- Anthropic: o Claude Opus 5 foge à regra e tende a respostas mais longas; mudar o nível de effort não altera o tamanho de forma confiável, e a orientação é pedir concisão no prompt. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Raciocínio ligado é apontado como erro comum em uso criativo (respostas vazias porque o orçamento vai para o pensamento). — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Samplers para modelos locais (text completion) em 2026: temperatura por volta de 1; min-p de 0,05 a 0,1 como filtro principal; top-p 1 e top-k 0 (desligados); penalidade de repetição leve (1,05–1,1) ou DRY; XTC se o modelo for "seguro" demais; mudar um ajuste por vez e gerar várias respostas antes de julgar. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Autor de presets para modelos locais: basta min-p com os outros samplers neutralizados, min-p antes da temperatura; variantes com temperatura 0,7, 1,0 e 1,3; não gosta de XTC. — [Sphiratrioth, SillyTavern Presets](https://huggingface.co/sphiratrioth666/SillyTavern-Presets-Sphiratrioth)
- Amostragem restritiva demais (temperatura baixa com top-p/top-k baixos, ou min-p alto) joga o modelo em trilhos de alta probabilidade e causa loop; penalidade de repetição alta demais quebra a gramática. — [TechTactician, Fix LLM Repetition in SillyTavern](https://techtactician.com/sillytavern-repetition-fixes-best-settings/)
- Slop: o artigo Antislop propõe um sampler com backtracking que suprime mais de 8.000 padrões mantendo a qualidade, enquanto banir tokens fica inutilizável em torno de 2.000. É técnica para modelos locais ou com acesso à amostragem. — [Antislop (arXiv 2510.15061)](https://arxiv.org/pdf/2510.15061v1)
- O preset universal da Marinara (v10) é descrito com scripts de regex anti-travessão, limpeza de tokens e arquivos de logit bias, além de chaves de tamanho de resposta. — [RP|Fiend, Claude Opus 4.6 Presets](https://rpfiend.com/claude-opus-4-6-presets-sillytavern/) (lido só pelo resumo da busca)
- O que cada API expõe:
  - Claude: nos Opus 4.7 em diante (incluindo Opus 5.5), definir `temperature`, `top_p` ou `top_k` com valor diferente do padrão devolve erro 400; a orientação é omitir os parâmetros e guiar o comportamento pelo prompt. — [Anthropic, Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)
  - Gemini: a configuração de geração inclui `topK`, `presencePenalty` e `frequencyPenalty` (suporte e padrão variam por modelo). — [Firebase, GenerationConfig](https://firebase.google.com/docs/reference/unity/struct/firebase/a-i/generation-config)
  - Gemini 3.x: a Google recomenda fortemente manter os valores padrão e avisa que temperatura abaixo de 1,0 pode causar loop ou queda de desempenho. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  - OpenAI: desenvolvedores relatam erro de parâmetro não suportado para `temperature`/`top_p` em modelos de raciocínio; em parte da família GPT-5.x esses parâmetros só são aceitos com reasoning effort "none". Os relatos divergem sobre quais modelos aceitam o quê. — [OpenAI Community, Temperature in GPT-5 models](https://community.openai.com/t/temperature-in-gpt-5-models/1337133); [vercel/ai issue #10932](https://github.com/vercel/ai/issues/10932)
  - Min-p, DRY, XTC e banimento de strings aparecem nas fontes só no contexto de modelos locais em text completion. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)

### Inferences
- Diagnóstico provável da tentativa anterior com Gemini: (a) prompt no formato "You are X + rules", que é o formato de assistente; (b) lista de regras, provavelmente com negativas; (c) nenhum exemplo; (d) nenhum limite de tamanho. Cada item tem correção direta nas fontes.
- Para Discord o alvo de tamanho é bem menor que os 300–500 tokens do roleplay narrativo: uma a três frases na maior parte das vezes. O jeito mais confiável de obter isso é os exemplos terem esse tamanho, mais um teto baixo de tokens de saída como rede de segurança.
- Registro de chat em PT-BR: os exemplos devem carregar as marcas ("né", "tá", "pra", reticências, frase incompleta, uma risada escrita) em vez de o prompt descrever "fale informalmente". Decidir também se a Closure usa ações entre asteriscos; em chat de Discord, o mais natural costuma ser só fala.
- Como DRY e listas de strings banidas não existem nas APIs fechadas, o equivalente num bot próprio é pós-processamento: regex para trocar travessões e remover preâmbulos, e nova geração quando a resposta contiver expressões de uma lista negra (por exemplo "Como uma IA", "Claro!", "Posso ajudar com mais alguma coisa?").
- A lista negra funciona melhor fora do prompt. Colocada no prompt como "não diga X", cai no problema da proibição em negativo.
- Com Gemini 3, baixar a temperatura para "ficar mais fiel" vai contra a recomendação oficial; a fidelidade tem de vir do prompt.

### Gaps
- Não obtive a documentação primária de DRY, min-p e XTC nem valores oficiais; os valores citados são de guias de terceiros.
- Não confirmei se a restrição de sampling vale para Sonnet e Haiku atuais; a frase lida fala em Opus 4.7 e posteriores.
- Não li a referência oficial da OpenAI sobre quais modelos aceitam `temperature`; os dados são de fórum e de uma issue.
- Não encontrei lista de "slop" em português brasileiro mantida pela comunidade; as listas conhecidas são em inglês.

## 8. Conselhos por modelo em 2026 (Claude, Gemini, GPT): presets da comunidade e documentação dos provedores

### Takeaway
Os três provedores dizem a mesma coisa em linhas gerais: papel e personalidade no system prompt, exemplos para tom, instruções positivas e em linguagem normal, e nada de superespecificar. As diferenças práticas são de API (Claude sem prefill e sem sampler nos Opus recentes; Gemini com temperatura padrão; GPT com parâmetro `verbosity`), e os presets da comunidade envelhecem a cada geração de modelo.

### Cited Findings
- Claude: uma frase de papel no system prompt já muda comportamento e tom; 3–5 exemplos em tags; XML para separar partes; casar o estilo do prompt com o da saída desejada. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Claude: detalhar personalidade, histórico e manias ajuda o modelo a emular e generalizar os traços; preparar cenários comuns com respostas esperadas. — [Anthropic, Increase output consistency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency)
- Claude: sem prefill desde os modelos 4.6; sem sampling não padrão desde o Opus 4.7. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices); [Anthropic, Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)
- Gemini: persona e restrições na System Instruction; sempre exemplos few-shot, poucos e variados; instrução específica no fim; valores padrão de amostragem no Gemini 3. — [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- GPT: a personalidade é definida nas instruções (system/developer prompt) e deve tratar de tom, estrutura de resposta, nível de detalhe, relação com o usuário e exclusões; deve ficar separada da lógica de tarefa; começar com uma personalidade mínima e validar com avaliações. — [OpenAI Cookbook, Shaping your agent's personality](https://developers.openai.com/cookbook/examples/gpt-5/prompt_personalities)
- GPT-5.1: o tamanho é controlado por um parâmetro `verbosity` da API, e tom, estilo e cadência pelo prompt; o guia recomenda persona clara e evitar frases de enchimento. — [OpenAI, Using GPT-5.1](https://developers.openai.com/api/docs/guides/gpt-5.1) (lido só pelo resumo da busca)
- Presets da comunidade em 2026: o preset universal da Marinara (v10) é citado como padrão para Claude, Gemini, GPT, DeepSeek e GLM, com chaves de narração, tempo verbal, ponto de vista e tamanho; os prompts da Pixi são ajustados por modelo. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Aviso recorrente: preset escrito para uma geração de Claude costuma estar errado para a seguinte; é preciso checar a data. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Impressões do mesmo guia sobre modelos: Claude é o favorito antigo para prosa e consistência; Gemini Pro oscila entre excelente e fraco, e o Flash tem camada gratuita; GPT tem política de conteúdo mais rígida. — [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- Exemplo de preset envelhecido: um preset da Marinara para o Gemini 2.5 Pro experimental (com cerca de 400 dias) usava temperatura 2 e top_p 0,95. — [MarinaraSpaghetti/SillyTavern-Settings (JSON do preset)](https://huggingface.co/MarinaraSpaghetti/SillyTavern-Settings/blob/main/Chat%20Completion/Friendship%20Ended%20With%20Sonnet,%20Gemini%20is%20Marinara's%20New%20Best%20Friend%20(Again).json)
- A página do repositório no Hugging Face lista um preset de Gemini na versão 4.5 e templates para modelos locais, com coleção datada de julho de 2024. — [MarinaraSpaghetti/SillyTavern-Settings](https://huggingface.co/MarinaraSpaghetti/SillyTavern-Settings)
- Outros presets citados: Freaky Frankenstein MAX+/BOLT+ (nota para desligar o módulo de CoT em Opus 4.8 em diante) e Pura's Director Preset (ajuste para o Opus 4.6 não se alongar; depende de prefill). — [RP|Fiend, Claude Opus 4.6 Presets](https://rpfiend.com/claude-opus-4-6-presets-sillytavern/) (lido só pelo resumo da busca)

### Inferences
- Há conflito entre fontes sobre temperatura no Gemini: o preset antigo usava 2 no Gemini 2.5, e a Google hoje manda manter o padrão no Gemini 3. Vale a recomendação oficial para o modelo em uso; presets antigos não devem ser copiados às cegas.
- Presets de SillyTavern são desenhados para roleplay narrativo longo em terceira pessoa. Para um bot de chat curto em Discord, o que se aproveita deles é a estrutura (ordem dos blocos e o lembrete pós-histórico), não o texto.
- A recomendação da OpenAI de separar personalidade de lógica de tarefa se traduz, no bot, em manter o card da Closure separado das regras operacionais do Discord (quando responder, menções, limites).
- Como os três provedores convergem, um mesmo card em prosa com exemplos funciona nos três; a parte específica de cada modelo fica na camada de montagem e nos parâmetros.

### Gaps
- Não consegui abrir o artigo do RP|Fiend nem localizar a casa atual do preset universal da Marinara (v10); os detalhes dele vêm de terceiros.
- Não li as seções de personalidade do guia do GPT-5.5 nem as páginas específicas de cada modelo Claude.
- Não encontrei orientação oficial de nenhum provedor especificamente sobre roleplay de personagem de ficção em outro idioma.
- Nenhum tópico de Reddit ou Hugging Face de 2025–2026 comparando modelos para personagem canônico foi recuperado.

## 9. Como as plataformas estruturam definições (Character.AI, Janitor AI, Chub/Venus, Kindroid, Shapes) e dicas de criadores

### Takeaway
Todas as plataformas chegam à mesma arquitetura com nomes diferentes: um bloco permanente de definição, diálogos de exemplo, uma saudação inicial e algum tipo de memória acionada por palavra-chave. A dica mais transferível para Discord vem do Character.AI: usar nomes de usuários variados nos exemplos para o modelo não confundi-los com a conversa real.

### Cited Findings
- Character.AI: a Definition é opcional, com 0 a 32.000 caracteres; o uso mais comum é diálogo de exemplo no formato `nome: mensagem`; variáveis `{{char}}`, `{{user}}` e `{{random_user_N}}` (o mesmo número mapeia sempre para o mesmo nome aleatório); colocar o mais importante no início, porque o fim pode ser truncado conforme a conversa cresce; links não são seguidos. — [Character.AI, Definition](https://book.character.ai/character-guide/character-attributes/definition.md)
- Guia de terceiros afirma que o modelo do Character.AI prioriza os primeiros 3.200 caracteres da Definition e sugere 15–30 linhas de conversa de amostra para fixar hábitos verbais. Não confirmado pela documentação oficial. — [Shapes.inc, Character.AI Bot Creation & Settings](https://shapes.inc/fandom/character-ai/creation-guide)
- Janitor AI (guia de criador na central de ajuda, atualizado em 05/09/2025): campos Personality, Scenario, Initial message e Example dialogs. Tokens permanentes são os que o bot lembra (Personality, memória do chat); temporários são esquecidos quando o contexto estoura (respostas antigas, Example dialogs). Por isso a autora põe os exemplos de fala dentro da seção Personality. Recomenda não passar de 2k tokens permanentes (2,5k no máximo) por compatibilidade com o JLLM, manter tempo verbal consistente e não descrever ações de `{{user}}`, para o bot não assumir a persona do usuário. — [JanitorAI Help, Bot Creation Guide by Faylua](https://help.janitorai.com/en/article/bot-creation-guide-w-images-by-faylua-8jcbw1/)
- Janitor: JLLM é o modelo próprio e gratuito; "proxy" é a ponte para modelos externos como Gemini ou DeepSeek. — [JanitorAI Help, Bot Creation Guide by Faylua](https://help.janitorai.com/en/article/bot-creation-guide-w-images-by-faylua-8jcbw1/)
- Kindroid: comparação de 2026 descreve memória persistente (Backstory, Key Memories, example messages, directives) e memória recuperável (journal entries acionadas por frase-chave: até 8 por entrada, 500 entradas, no máximo três lembradas por mensagem). — [AI Companion Pick, Memory Showdown 2026](https://aicompanionpick.com/ai-companion-memory-kindroid-nomi-replika-long-term-2026)
- Kindroid: tutorial de terceiros recomenda 3–5 trocas curtas de exemplo mostrando voz, humor e alcance emocional. — [AI Indigo, Getting started with Kindroid](https://aiindigo.com/tutorials/getting-started-with-kindroid-crafting-deeply-personal-ai-companions)
- O formato de card dessas plataformas é interoperável via Character Card V2/V3 (campos `first_mes`, `mes_example`, `character_book`, `alternate_greetings`). — [Character Card V2 spec](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)

### Inferences
- Duas escolas sobre onde pôr os exemplos: no campo temporário (padrão SillyTavern, caem quando o contexto enche) ou dentro do bloco permanente (prática do Janitor e do Ali:Chat). Para personagem canônico com contexto grande, a segunda é a mais segura: a voz nunca deve sair do prompt.
- O journal do Kindroid é o mesmo mecanismo do lorebook por palavra-chave, com limites embutidos (no máximo três entradas por mensagem). É uma boa regra de bolso também para um lorebook próprio.
- Para Discord multiusuário: escrever os exemplos com dois ou três interlocutores de nomes diferentes e prefixar cada mensagem do histórico com o nome de quem falou, à maneira do "Include Names" do SillyTavern.
- A regra do Janitor de não escrever ações do usuário nos exemplos vale para o bot: os exemplos devem mostrar só a Closure respondendo, sem narrar o que o interlocutor faz ou sente.

### Gaps
- Não encontrei documentação oficial do Shapes sobre os campos de personalidade; só páginas de perfil público.
- Não consultei a documentação do Chub/Venus; assumo, sem fonte lida, que segue os campos V2/V3.
- A documentação oficial do Kindroid não foi lida; os limites citados vêm de um site comparativo.
- Dicas de "top creators" em primeira mão (Reddit, Discord) não foram recuperadas; as de Janitor vêm de um guia de criadora publicado na central de ajuda oficial.

## 10. Avaliação: como testar a fidelidade

### Takeaway
A pesquisa acadêmica avalia roleplay em dimensões separadas (habilidade de conversa, consistência de papel, atratividade, personalidade), e a comunidade testa de forma artesanal: fixar tudo, mudar uma coisa por vez e gerar várias respostas. Não encontrei protocolo de comunidade documentado para personagem canônico, então o checklist abaixo é derivado das fontes.

### Cited Findings
- CharacterEval (Tu et al., 2024): benchmark chinês com 1.785 diálogos multi-turno e 77 personagens de romances e roteiros, 13 métricas em quatro dimensões (habilidade conversacional, consistência de personagem, atratividade do roleplay, teste de personalidade). — [CharacterEval (arXiv 2401.01275)](https://arxiv.org/abs/2401.01275v1)
- RoleLLM/RoleBench (Wang et al., 2024): 100 papéis e 168.093 amostras; separa imitação de estilo de fala e conhecimento específico do papel. — [RoleLLM (arXiv 2310.00746, via arxiv-vanity)](https://www.arxiv-vanity.com/papers/2310.00746)
- Estudo de 2026: com o nome do personagem anonimizado o desempenho cai, o que separa fidelidade real ao perfil de simples lembrança do personagem. — [Rethinking Role-Playing Evaluation (alphaXiv 2603.03915)](https://www.alphaxiv.org/abs/2603.03915)
- Prática de depuração da comunidade: manter card, prompt e seed constantes e alterar um controle de cada vez; gerar várias respostas antes de julgar um ajuste. — [TechTactician, Fix LLM Repetition in SillyTavern](https://techtactician.com/sillytavern-repetition-fixes-best-settings/); [Aituts, SillyTavern Guide 2026](https://aituts.com/sillytavern-guide/)
- OpenAI: começar com uma personalidade mínima e validar com avaliações antes de expandir. — [OpenAI Cookbook, Shaping your agent's personality](https://developers.openai.com/cookbook/examples/gpt-5/prompt_personalities)
- Anthropic: pedir ao próprio modelo que avalie os exemplos quanto a relevância e diversidade, ou que gere exemplos adicionais a partir do conjunto inicial. — [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Drift aparece em poucas rodadas e nenhuma intervenção o elimina, o que justifica testar conversas longas e não só a primeira resposta. — [arXiv 2402.10962](https://arxiv.org/abs/2402.10962); [arXiv 2609.24532](https://arxiv.org/abs/2609.24532)

### Inferences
Protocolo sugerido para a Closure, derivado das fontes acima:

- **Conjunto de falas reservadas.** Separar falas canônicas que NÃO entram no card. Para cada uma, reconstruir a situação, pedir a resposta do bot e comparar lado a lado: tamanho, tema, tipo de piada, tratamento do interlocutor.
- **Teste cego.** Misturar respostas do bot com falas canônicas adaptadas para PT-BR e pedir a quem conhece a personagem que aponte quais são do bot. É o equivalente caseiro das métricas de consistência.
- **Bateria fixa de sondagens, sempre com as mesmas 15–20 mensagens.** Conversa fiada; pedido de ajuda técnica real (o tom de assistente volta?); pergunta sobre lore; pergunta fora do universo (política atual, "você é uma IA?"); provocação; momento triste; tentativa de tirá-la do personagem; pergunta sobre algo que ela não sabe (ela inventa lore?).
- **Checklist por resposta.** Uma a três frases? Português natural, sem cara de tradução? Sem lista, sem negrito, sem oferta de ajuda no final? Tocou num tema dela sem repetir bordão do card? Não narrou ações do usuário? Fato de lore correto?
- **Teste de drift.** Conversa de 30 turnos ou mais, comparando o turno 3 com o turno 30, com e sem o lembrete no fim do contexto.
- **Teste de cópia.** Procurar nos logs trechos literais dos exemplos. Se aparecerem com frequência, reduzir ou variar os exemplos.
- **Teste de dependência do nome.** Trocar "Closure" por um nome neutro no card. Se a voz desaparecer, o card estava se apoiando na memória do modelo e não no próprio texto.
- **Regra de método.** Mudar uma variável por vez e gerar pelo menos cinco respostas por condição antes de concluir.

### Gaps
- Não encontrei checklist ou protocolo publicado pela comunidade de botmaking para fidelidade de personagem canônico; o protocolo acima é inferência.
- Os benchmarks acadêmicos são em chinês e inglês; não achei avaliação de roleplay em português.
- Não encontrei dados sobre a confiabilidade de usar um LLM como juiz de fidelidade para personagem de nicho.
