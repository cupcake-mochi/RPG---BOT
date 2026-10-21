# Guias de uso · 21/10/2026

O bot oferece `/guia`, com o campo opcional **assunto**, e `GC:guia assunto`.
`/ficha guia`, `GC:ficha guia` e `GC:ajuda ficha` abrem a orientação de ficha.
`/ajuda` continua sendo a lista dos comandos disponíveis para quem pediu.

## Conteúdo e navegação

São nove assuntos: início, ficha, customizações e mestre, livro, clima,
conversa, mídia, memória e configuração do servidor. O menu de assuntos
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
