# Guias de uso · atualização de 24/10/2026

A ficha definitiva atualiza emissão, salário por fórmula, gasto/ganho, datas,
paleta e invocações nos guias PT/EN e no contexto de conversa das duas guias.
Inventário, fontes e limites do teste nativo: [R53 definitiva](R53-DEFINITIVA.md).
Esta atualização está preparada para revisão, ainda sem publicação no bot.

O bot oferece `/guia`, com o campo opcional **assunto**, e `GC:guia assunto`.
`/ficha guia`, `GC:ficha guia` e `GC:ajuda ficha` abrem a orientação de ficha.
`/ajuda` continua sendo a lista dos comandos disponíveis para quem pediu.

## Conteúdo e navegação

São doze assuntos: início, criar uma ficha, conhecer a planilha, análise da
ficha, revisão do mestre, customizações, livro, clima, conversa, mídia, memória e
configuração do servidor. O menu de assuntos
permanece disponível mesmo quando o assunto tem uma página só. Outro menu
escolhe a página; as setas percorrem o assunto. Trocar de assunto volta à
primeira página. Após dez minutos sem interação, o texto permanece e os
controles orientam a reabrir o guia.

Pela barra, a resposta é privada. Pelo prefixo `GC:`, é pública, sem marcar
quem pediu. O guia é orientação estática: não consulta IA, não lê uma ficha,
não acessa memória pessoal nem modifica preferências ou aprovações.
Os comandos administrativos continuam exigindo suas permissões originais.

O passo a passo de ficha explica envio por link e XLSX, cores por página,
veredito geral, nova análise após edição e erros de leitura. A revisão humana
cobre aprendizado, história de marcos/treinos, requisitos livres, COMO É,
distribuição entre alvos, estados de entidades e interações de Alma.

Customizações têm orientação própria: **MESTRE VIU não autoriza**;
aprovação exige a definição exata e o servidor correto; prosa não vira
bônus. Peças próprias sem recálculo independente continuam assim mesmo
quando aprovadas. Não foi criado um comando de autoaprovação.

## Revisão de escrita

Foram lidas as saídas fixas dos módulos de ajuda/administração, atalhos,
ficha/paginação, livro, clima e dados pessoais, além dos avisos de falha e
das orientações de mídia/conversa. A revisão considera: próxima ação clara,
exemplos executáveis, distinção entre conferência e autorização, e limites
explicados sem inventar funções.

Além do guia, mudaram a descoberta dos assuntos no `/ajuda`, a orientação
de comando desconhecido, os plurais dos contadores e dias de conversa,
os rótulos de customizações, o limite de fatos expresso em caracteres e
o aviso de cidade não encontrada. A memória agora explica que uma fala
**pode** originar um fato, sem prometer que isso sempre ocorre.

Os cards, prompts das personagens, regras e cálculos não foram alterados.
A revisão das saídas fixas não certifica toda resposta futura gerada pelos
modelos. Não houve chamadas pagas para esta tarefa.

## Verificação e publicação

Os testes do guia cobrem rotas da barra e do prefixo, aliases com acentos,
privacidade, ausência de análise/chamada de modelo, limites dos embeds,
troca de assunto, navegação, retorno à primeira página e cliques depois
do timeout. A paginação de ficha conserva seu aviso padrão de encerramento.

Resultados completos, pacote e ensaio externo são registrados em
`pesquisa/validacao/2026-10-21-guias/RELATORIO.md` ao encerrar a publicação.

Para retomar: conferir o relatório e o remoto; testar `/guia`,
`/guia assunto:Analisar uma ficha`, `/ficha guia`, `GC:guia ficha` e o seletor de assuntos.
Não refazer a bateria mecânica R53 só por uma alteração de texto.

## Criar e conhecer a ficha · ampliação de 21/10

- `GC:guia criar` / `/guia assunto:Criar uma ficha`: 14 etapas, da cópia
  oficial à emissão na CARTEIRA. Inclui campanha, identificação, atributos,
  Origem, Caminho/Trilha, treinos, rotas, cartões, repertório, entidades,
  compras, valores atuais, análise e revisão com o mestre.
- `GC:guia planilha` / `/guia assunto:Conhecer a planilha`: 14 páginas de
  consulta. Explica as sete abas, grupos recolhidos, versões por Classe,
  progressão, regras de campanha, bônus, cadastros próprios, emissão,
  salários e manutenção. `GC:guia manual` também abre esse assunto.
- `GC:guia ficha` e `/ficha guia` continuam dedicados à análise. O início e
  a ajuda indicam os três caminhos para evitar misturar criação e avaliação.

A última etapa agora explica que **EMITIR** grava a data de Brasília uma vez
e se desmarca; não envia análise ou aprovação. Repetir a marcação não altera
a data. A correção em O38 só permite avançar até hoje, preservando salários
vencidos e reiniciando o ciclo aberto. Na definitiva, o salário é por fórmula
e não exige ativar uma rotina diária. Abaixo ficam as fontes históricas da
criação dos guias; as fontes vigentes estão em R53-DEFINITIVA.md.

### Fontes verificadas

Produtor consultado no main `fbd6d156602958dc0f9da467a4a80100ad7b913f`,
posterior à integração R53 e com emissão/salários. Livro consultado no main
`1432c477f812aaaf1e0e8fdff8ed54d1709a663d`, cujo fechamento identifica R53.
Não se usaram os cabeçalhos B47 históricos como estado vigente.

| Parte do texto | Fonte primária |
|---|---|
| Cópia, padrão nível 2/Grau 4, 9 pontos, treinos, rotas e recursos | JJK---Project, `sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`, capítulo 4 e Equipamento inicial |
| Cartões no local, funções, Classe e espera ao trocar | Ficha---RPG-JJK, `r53/ENTREGA.md`, `ficha-v01/cartoes_diretos.py`, `apps-script/EditorR53.gs` |
| Abas, campos e navegação | `ficha-v01/ficha_amaldicoada.py`, `ficha_pessoal.py`, `glossario.py`, `configuracao_horizontal.py` e fechamento R53 |
| Regras de campanha e ajustes | `ficha-v01/campanha.py`, `configuracao.py`, cadastros `custom*.py` |
| Emitida, datas, ienes, missões e rotina na cópia | `salarios/README.md`, `apps-script/Salarios.gs` |
| Análise e aprovação exata | Contrato/consumidor do próprio bot e assunto Customizações |

O roteiro dá os valores padrão e manda conferir exceções com o mestre.
Não concede acesso a capacidades por haver um cartão, não converte texto
em bônus e não certifica aprendizado, história ou salários pela análise.
Na entrega original deste guia, a base geral ainda era R51/R52. A migração
posterior para R53 já foi concluída; consulte o fechamento R53 para a fonte
e a cobertura atuais.

### Revisões de texto

1. Conferência factual com o livro e os emissores: regras padrão, nomes de
   campos, rotas, versões, checkbox e rotina salarial.
2. Leitura como jogador novo: cada etapa indica onde ir, o que preencher e
   o que conferir antes de seguir. Siglas relevantes têm explicação; abas
   e configurações ficam no assunto de consulta, separado da criação.
3. Conferência de ponta a ponta: pontos, treinos, aquisições, inventário,
   recursos, revisão humana e emissão. Foram acrescentados progressão,
   paleta, aviso de dupla contagem de salário e desmarcação da emissão.
4. Revisão no formato de páginas e menus: páginas curtas por tarefa,
   assuntos distintos e rótulos completos para os três painéis CONFIGURAÇÃO.

Isso registra revisão editorial e testes de interface; não é um estudo de
usabilidade com jogadores novos. As provas e o estado da publicação ficam
em `pesquisa/validacao/2026-10-21-guias-criacao/RELATORIO.md`.

5. Após o pedido adicional do usuário, nova revisão dos nomes: o assunto de
   análise passa a se chamar **Analisar uma ficha**. Títulos como “Cartões:
   Classe, peças e versões” e “Missões, datas e manutenção” passam a explicar
   a tarefa: **Como montar e editar uma habilidade** e **Como registrar
   missões e atualizar a ficha**. Nomes de abas permanecem nos títulos que
   precisam orientar a localização, com subtítulos que explicam sua função.

## Revisão do mestre e abreviações · 21/10

`GC:guia mestre`, `GC:gm` e `/ficha mestre` abrem um roteiro de oito páginas
para cruzar a análise com a conferência humana da criação, progressão,
habilidades, espaços, entidades, efeitos, customizações, inventário,
salários e decisão final. `mestre` passou a ser esse assunto próprio;
`custom`/`aprovação` permanecem dedicados ao cadastro exato. O Resumo da
análise aponta para o roteiro. Nenhuma conta, cor ou aprovação muda.

A ajuda tem duas páginas: **Comandos disponíveis** e **Abreviações**.
`/ajuda pagina:Abreviações`, `GC:ajuda abreviações`, `GC:atalhos` e `GC:ab`
abrem a segunda diretamente. O menu e as setas trocam de página; a barra
continua privada e o prefixo público. Reabrir atualiza a lista do servidor.

| Atalho padrão | Comando completo |
|---|---|
| GC:a / GC:g / GC:f | GC:ajuda / GC:guia / GC:ficha |
| GC:l / GC:c | GC:livro / GC:clima |
| GC:p / GC:s | GC:ping / GC:status |
| GC:gc / GC:gp | GC:guia criar / GC:guia planilha |
| GC:gf / GC:gm | GC:guia ficha / GC:guia mestre |
| GC:ab | GC:ajuda abreviações |

Os argumentos e anexos continuam com o comando de destino: por exemplo,
`GC:f LINK` ou XLSX anexo, `GC:c BH`, `GC:g mestre`. Os nomes completos e
os aliases antigos permanecem. A lista de padrões e destinos permitidos
vem de `src/closure_bot/atalhos.py`, usada também na ajuda e no contexto.

### Atalhos por servidor

Quem tem **Gerenciar servidor** usa `/atalho definir nome destino`,
`/atalho remover nome` e `/atalho listar`. O nome tem até 24 caracteres,
começa por letra e aceita letras, números e sublinhado. Até 20 por servidor;
é possível alterar o destino de um próprio existente mesmo no limite.

Só destinos públicos da lista são aceitos. Não há frases/macros livres,
URLs fixas, encadeamento de aliases, comando pessoal/administrativo ou
substituição de nomes canônicos, aliases antigos e padrões. Permissão e
servidor são conferidos na execução, além da configuração do comando Discord.

O SQLite existente ganha somente `atalhos_servidor(guild_id,nome,destino)`.
Os dados persistem após reiniciar e ficam separados por servidor. A ajuda
expõe apenas os daquele servidor. Nenhuma preferência existente é removida.
O conteúdo cadastrado também passa por validação na leitura.

### Conhecimento das duas guias

As duas personagens recebem uma orientação operacional do produto em
`prompt.py`: existência dos guias, análise determinística, abreviações,
configuração e seus limites, mais os atalhos válidos do servidor atual.
Isso não grava fatos sobre pessoas nem muda os cards ou o núcleo do site.
A personagem deve orientar o usuário a executar o comando, sem fingir que
o executou ou registrou autorização do mestre. O contexto das duas foi
conferido com montagem simulada, sem chamada paga ao modelo.

A política de privacidade registra o armazenamento desses nomes/destinos,
exibição na ajuda, envio no contexto e remoção administrativa. Dados pessoais
não se confundem com configurações compartilhadas do servidor.

Validação, publicação e ensaios externos desta rodada:
`pesquisa/validacao/2026-10-21-mestre-atalhos/RELATORIO.md`.

## Idioma e mundo por servidor · publicado em 21/10

Os 57 painéis dos doze assuntos têm versão em inglês. `/idioma` ou `/language` muda as respostas novas do servidor; os nomes no menu de comandos seguem a preferência do cliente Discord. Com `GC:`, os aliases `guide`, `sheet`, `book`, `weather` e `help` também são aceitos. A ficha oficial continua com seus rótulos portugueses: a tradução preserva nomes de opções e chaves para que o jogador localize os campos.

`/lnt` consulta; `ativar:Sim` seleciona Nova Terra e `ativar:Não` seleciona a referência original de Arknights. Idioma e mundo são independentes. Os três servidores indicados pelo mantenedor começam em Nova Terra; outros começam em Arknights. Quem tem Gerenciar servidor pode delegar apenas essas duas opções por `/cargo_admin`; isso não autoriza outros comandos administrativos, fichas ou criações próprias.

Histórico de conversa é reiniciado na troca. Fatos duradouros ficam separados por servidor e mundo. Fatos antigos sem origem conhecida não são reinjetados: `/meus_dados legado:Sim` permite consultá-los, `/esquecer_fato legado:Sim` os remove, e `/meus_dados todos:Sim` entrega uma exportação privada dos fatos de todos os contextos. Exclusão pessoal continua abrangendo todos.

A ajuda descreve canais de forma genérica, sem IDs da hospedagem. O livro oferece normal e escuro. Pedidos simples de links públicos conhecidos, como “pode me mandar o link do livro?”, são atendidos na conversa sem IA; não executam análise, configuração ou aprovação.

Conferência mecânica continua determinística. Inglês é uma camada de apresentação; contas, aprovações por definição exata, campos e dados do jogador não mudam. Base original é uma referência curada limitada, com conhecimento canônico do jogo quando há confiança, e não um corpus integral de todos os eventos. As pastas reservadas 04/05/06 continuam excluídas.
