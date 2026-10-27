# Nova ficha R53 — proposta de contrato de inicialização 1

27/10/2026. **Proposta para implementação e validação no produtor. Não é uma
rotina disponível nem um certificado aceito pela Carteira.** A criação segue
bloqueada. Este documento define o trabalho necessário para sair desse estado,
com inventário ancorado nas fontes atuais e critérios verificáveis.

Repositórios reconferidos nesta continuação:

- Ficha---RPG-JJK: `d0836390f90b435b4796313e898eaaa1a4a4da8b`.
- JJK---Project: `353d7728fa4f505f830dc6c0421929a0ab2668c1`.
- Consumidor: PR 84 de RPG---BOT, dependente da etapa 6; sem publicação.

Os fontes abaixo não substituem uma inspeção do código instalado na cópia.
`r53/OFICIAIS.md` registra os incrementos das oficiais; o pacote integral
gerado não foi instalado por esta tarefa e não deve ser promovido por rotina.

## Inventário mínimo comprovado no fonte

Referências fixadas no commit do produtor:
[Salarios.gs](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/d0836390f90b435b4796313e898eaaa1a4a4da8b/apps-script/Salarios.gs),
[SalarioLote](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/d0836390f90b435b4796313e898eaaa1a4a4da8b/r53/diagnostico-android/salario_lote.gs) e
[EditorR53](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/d0836390f90b435b4796313e898eaaa1a4a4da8b/apps-script/EditorR53.gs).

| Área | Estado que exige tratamento de nova ficha | Preservação/decisão necessária |
|---|---|---|
| EXTRATO A2:C até o fim físico | Lançamentos e saldo de personagem anterior | Preservar cabeçalhos, formatos e proteção; não criar saldo anterior a partir de O86 |
| SALÁRIOS A2:L até o fim físico | Créditos/fechamentos anteriores | Preservar estrutura; total inicial não pode somar crédito herdado |
| DADOS_SALARIOS A2:G até o fim físico | Registro de identidade, nome, tipo, data e vínculo de missão | Deve concordar com as missões novas; só apagar o livro não elimina essas identidades |
| DADOS_SALARIOS H2:J até o fim físico | Histórico de mudanças de Grau/regras/emissão | Não herdar regras históricas de um personagem; conservar regras atuais da campanha na CONFIGURAÇÃO |
| DADOS_SALARIOS L2 | JSON do módulo legado: início, graus, última emissão e possível agenda | Produtor precisa definir o estado inicial válido para as versões instaladas; apagar L2 ou gravar `{}` sem essa prova não basta |
| DADOS_SALARIOS N2 | Data efetiva da emissão | Nova ficha sem emissão; preservar o cabeçalho N1 e as fórmulas que exibem N2 |
| FICHA PESSOAL AW:AX, BC:BD, BI:BJ, BO:BP, linhas 15–87 | Nome/tipo de missão e nota com `[Salário: ...]` | A identidade viaja na nota. Remover texto visual não remove a identidade; definir as demais entradas de cada missão sem apagar XP calculado |
| FICHA PESSOAL O86 | Caixa de lançamento, inclusive fórmula customizada | Não converter conteúdo herdado em saldo inicial; valor inicial permitido precisa ser definido pelo produtor |
| FICHA PESSOAL BI11 e BO11 | Caixas/resultado de correção de data de missão | Não preservar correção do personagem anterior |
| Fórmulas financeiras | Q2:Q8, P11 e AA2 de DADOS_SALARIOS; W86 da FICHA PESSOAL; painel da CONFIGURAÇÃO | Preservar âncoras e seus derramamentos; não limpar a aba inteira nem sobrescrever totais com zero |
| Emissão na interface | CONFIGURAÇÃO O38/O39 e CARTEIRA AH3/AT3 | Preservar fórmulas de apresentação e desarmar a ação de emitir; copiar não equivale a emitir |
| Nível e XP | FICHA AH11 e AN11/DADOS CZ47 | Nível atual é entrada própria. XP é calculado. Regra inicial F46/G46 da CONFIGURAÇÃO é separada e deve ser preservada |

As colunas auxiliares de missão além de nome/tipo e os dados do editor de
cartões ainda precisam de inventário completo do produtor. Essa tabela é um
escopo mínimo financeiro e não declara que todos os dados de personagem foram
enumerados. Nenhuma dessas linhas é uma lista de comandos de limpeza pronta.

## Estado fora das células

O fonte usa DocumentProperties `salario_extrato`, `salario_trocas`,
`salario_correcao_nome` e `salario_proximo` como contadores/cache, e
ScriptProperties `salario_edicao` para distinguir a rotina instalável.
`L2.agenda`, quando presente, referencia o projeto da agenda.

Os comentários do produtor indicam que contadores de propriedades não vêm
numa cópia; isso não foi convertido em garantia nativa desta tarefa. É preciso
inspecionar a cópia e rederivar o estado de acordo com seu próprio projeto.
Não copiar IDs de agenda, não cadastrar gatilho em nome do antigo responsável
e não usar `deleteAllProperties()` para resolver o problema: propriedades de
montagem, paleta e editor têm outros papéis e exigem tratamento explícito.

O EditorR53 também mantém Classe visível, amparo e recuperações de edições.
Restaurar uma recuperação antiga depois de limpar as células pode recolocar
dados do personagem anterior. O contrato do produtor deve cobrir esse estado
antes de declarar uma nova ficha pronta.

## Por que os preparadores atuais não inicializam uma nova ficha

- `salarioPrepararCarteira_` retorna sem limpar quando EXTRATO já existe.
- `salarioPrepararEmissao_` retorna se N1 já tem conteúdo; o cabeçalho copiado
  não prova que o estado financeiro da nova ficha foi zerado.
- `prepararSalarioLote` prepara fórmulas/painel e invalida cache, sem limpar
  livro ou missões, conforme seu próprio comentário.
- Reemitir/corrigir emissão preserva/congela pagamentos vencidos. Essas
  operações são de continuidade de personagem, não de criação de outro.

Não chamar essas rotinas em sequência e anunciar “inicialização concluída”.
Também não simular `onEdit` para tentar obter indiretamente seus efeitos.

## Protocolo exigido antes de implementar escrita

1. **Alvo:** vincular operação a uma cópia nova, distinta do modelo e de todos
   os arquivos registrados; recusar as oficiais e qualquer ficha preenchida.
   Identidade do novo responsável e acesso à cópia são provas independentes
   da autorização usada pelo administrador para escolher o modelo.
2. **Versões e prévia:** fixar versões do contrato, produtor instalado, modelo
   e cópia; listar os domínios tratados e o que será preservado. Alteração
   durante a espera invalida a prévia. Nenhum “pronto” vindo do navegador é prova.
3. **Responsabilidade:** produtor enumera todas as entradas, notas, propriedades,
   caches e recuperações envolvidas, inclusive os domínios ainda não cobertos.
   Parâmetros aceitos e estado salarial inicial recebem regras explícitas.
4. **Recuperação:** definir uma operação idempotente com ID estável, diário
   e resultado verificável. Interrupção parcial fica incompleta e não é
   cadastrada. Retentativa não relança dinheiro, emite carteira ou paga salário.
5. **Execução explícita:** decidir o que roda pela API e o que requer uma ação
   do responsável no Apps Script. Não ampliar o OAuth drive.file das Guias.
   Se a arquitetura exigir outro escopo, essa solução permanece indisponível
   dentro dos limites atuais; não contornar pelo conector de outra aplicação.
6. **Pós-condições:** conferir saldo/créditos/participação/emissão sem herança,
   notas e propriedades coerentes, fórmulas e proteções preservadas, parâmetros
   aplicados no lugar correto e editor sem recuperação de personagem anterior.
7. **Ativação:** provar com a conta do responsável as automações efetivamente
   necessárias, inclusive limitações no Android. Instruções manuais só aparecem
   no produto quando houver um procedimento existente e validado.
8. **Aceite:** repetir criação, falha, retomada e segunda execução em cópias
   descartáveis de Era, Ciclo e servidor sintético. Conferir independência do
   modelo, preservação dos personagens cadastrados e duas identidades Google.

## Papel da sondagem 2 do consumidor

A PR 84 passou a conferir a grade antes dos dados e ler o fim físico dos
livros EXTRATO, SALÁRIOS e DADOS_SALARIOS A:J. Limite de 5.000 linhas por
livro; uma grade maior é recusada, sem truncar para uma amostra aparentemente
vazia. A resposta Google continua limitada a 512 KiB e o timeout HTTP
configurado continua em 15 s.
Lê somente os campos necessários de CellData, inclusive as notas das missões.
Não guarda nomes de missão, valores de lançamentos ou texto de notas na prévia:
só sinais constantes de presença.

Referências anteriores continuam identificadas como sondagem 1; as novas,
como 2. A confirmação não mistura essas versões. Isso melhora o diagnóstico,
mas **não é inicialização**: propriedades, gatilhos, código instalado, editor
e todos os demais dados ainda não são certificados. Ausência de sinais nunca
habilita criar_por_modelo; a barreira continua incondicional.
