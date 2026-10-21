# Guias de uso · 21/10/2026

O bot oferece `/guia`, com o campo opcional **assunto**, e `GC:guia assunto`.
`/ficha guia`, `GC:ficha guia` e `GC:ajuda ficha` abrem a orientação de ficha.
`/ajuda` continua sendo a lista dos comandos disponíveis para quem pediu.

## Conteúdo e navegação

São onze assuntos: início, criar uma ficha, conhecer a planilha, análise da
ficha, customizações e mestre, livro, clima, conversa, mídia, memória e
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
`/guia assunto:Ficha`, `/ficha guia`, `GC:guia ficha` e o seletor de assuntos.
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

A última etapa explica que marcar **Emitida** grava a data de Brasília e
se desmarca ao salvar; não envia análise ou aprovação. Reemitir pode
reiniciar o ciclo aberto. A automação salarial precisa ser ativada na cópia,
pois os acionadores não são copiados. Não houve emissão nem mudança salarial
em uma ficha real durante este trabalho.

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
A base geral do chat permanece R51/R52; este guia estático foi conferido nas
fontes R53 atuais, sem alterar o corpus nem os cálculos do bot.

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
