# Nova ficha R53 — proposta de contrato de inicialização 1

27/10/2026. **Proposta para implementação e validação no produtor. Não é uma
rotina geral disponível nem um certificado aceito pela Carteira.** A criação segue
bloqueada. Este documento define o trabalho necessário para sair desse estado,
com inventário ancorado nas fontes atuais e critérios verificáveis.

Repositórios reconferidos nesta continuação:

- Ficha---RPG-JJK main: `b0dc6aacef08b2c01a7f8a3519bbcc9bff9546ed`; PR 31 incorpora em `84bcd56` os protótipos `280a7dc`.
- JJK---Project: `353d7728fa4f505f830dc6c0421929a0ab2668c1`.
- Consumidor: PR 84 de RPG---BOT, dependente da etapa 6; sem publicação.

Os fontes abaixo não substituem uma inspeção do código instalado na cópia.
`r53/OFICIAIS.md` registra os incrementos das oficiais; o pacote integral
gerado não foi instalado por esta tarefa e não deve ser promovido por rotina.

## Domínios adicionais do produtor · 27/10

PR 31 em rascunho, código `280a7dc`, incorpora a main acima (merge `8cb12ac`).
O executor financeiro foi extraído para perfis fixos sem mudar o diário v1;
a assinatura anterior tem regressão. Não aceita plano enviado pelo navegador.

| Protótipo | Escritas | Preservação e limite |
|---|---|---|
| Nível/base XP | FICHA AH11; DADOS CZ54 | Usa regra inicial e curva da campanha; exige fase financeira da mesma operação e missões vazias. Não altera fórmulas ou distribui atributos/marcos. |
| Textos pessoais | 14 entradas e notas em CARTEIRA/FICHA PESSOAL | Rótulos e espelhos conhecidos; nome volta ao texto de preenchimento. Imagens em célula recusadas; imagens sobrepostas ainda não tratadas. |

Leitor recusa CellImage/objetos em vez de misturar imagens como `{}`. Regra
G46 aceita `,` ou `;` da fórmula conhecida, sem afrouxar outras diferenças.
259 cenários offline (101/80/78) e 20.643 verificações XP passaram. Projeção
nativa dos efeitos via Sheets API, numa cópia nova privada da Era: 14 entradas
limpas, nível 10/base 3.700, missão de 50 levou XP a 3.750 e retirada voltou
a 3.700. 8.998 comparações delimitadas preservadas sem diferença; cópia na
lixeira, aba fechada. [Alvos e prova](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/280a7dcd0b3fb56b0a43dd6e0d88aaadcb08d634/r53/inicializacao/NIVEL-TEXTOS-2026-10-27.md).

No fechamento, main avançou para `b0dc6aacef08b2c01a7f8a3519bbcc9bff9546ed`
(PR 37 salarial) e foi incorporada no merge `84bcd56` do produtor. Fórmulas
protegidas/alvos dos inicializadores não mudaram. 15 verificações de abertura,
95 salariais e 101 financeiras passaram após o merge. O ensaio nativo descrito
é anterior; não valida execução desse código Apps Script. Nada foi instalado.

CI final do integrado `84bcd566ae74d73bd8fdaf3889aa1ab5d7c68722`
aprovado: [40535287570](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40535287570), 27/10 às 12:53:51 Brasília.
Os 259 cenários, pacote de nove arquivos e regressões passaram; 277 fontes
Python/208 JS-GS com sintaxe válida. Run duplicado cancelado. Registro final
posterior só documental. Prova do OAuth/Apps Script completo continua pendente.

CI anterior, antes da PR 37, aprovado no código `280a7dc`:

[40534237271](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40534237271), 27/10 às 12:47:26 Brasília.
Confirmados os 259 cenários, pacote de nove arquivos sem inicializadores,
sintaxe e regressões. Run duplicado do push cancelado; registro posterior
só documental, sem repetir a bateria do bot.

**Não executou os novos diários Apps Script nem OAuth próprio das Guias.**
Ensaio financeiro antigo `4f3555d` não valida o executor extraído. Todos os
perfis mantêm `criacaoDisponivel=false`; bot não os chama e criação continua
bloqueada. Falta orquestração e conferência conjunta: depois de mudar o nível,
não repetir o financeiro antigo nem apagar diários para reiniciar fases.

Ainda faltam fotos/arte, escolhas, atributos/treinos/marcos/recursos,
inventário, entidades/cartões e recuperações/editor; considerar também os
caches novos `r53_versoes`/`r53_marcas_custom`. Automação, latência, prova do
novo responsável e integração permitida com drive.file continuam exigidas.
Nenhum pacote instalado, merge em main ou deploy nesta continuação.

## Registro anterior: esclarecimento e financeiro

O usuário confirmou: o modelo do servidor é a ficha do sistema com
configurações extras da mesa. Preservar regras e catálogos do servidor;
não herdar identidade, progressão, inventário, missões, cartões ou dinheiro
de personagem anterior. Não solicitar uma lista de escolhas prontas novamente.

O primeiro domínio ganhou implementação **separada no produtor**:
[PR 31, em rascunho](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31),
branch `codex/inicializacao-financeira-carteira`, código
`4f3555d2634c84899e5004733245ae69d0f83c6d`, base `d0836390`;
registro nativo/documentação em `352929a` (sem alteração de código).
`r53/inicializacao/financeiro.gs` faz prévia, aplicação explícita e retomada
financeira. Conteúdo, notas e cada propriedade têm passos distintos para
retomar após interrupção. Não expõe endpoints nem instala eventos/acionadores;
não entra no pacote atual e não é chamado pelo bot.

99 cenários offline novos passaram, incluindo falhas antes/depois de todas
as escritas, edição concorrente, prévia antiga, notas, estado parcial e
preservação. Regressões focais: 95 verificações salariais e 64 cenários/611
verificações de missões. CI Linux do produtor aprovado no mesmo SHA:
[40505846627](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40505846627).
A execução duplicada do push foi cancelada; a execução da PR passou no
mesmo código; não é falha de teste. Não somar esses resultados à suíte do bot.

Leitura nativa pontual das duas oficiais confirmou grade de 1.000 linhas e
as âncoras financeiras esperadas, sem alteração. Prévia do protótipo em uma
cópia descartável do Ciclo concluiu em 115,013 s. Não é latência aceitável de
comando Discord nem prova de inicialização completa; o protótipo é executado
explicitamente no Apps Script. Primeira aplicação atingiu 360,813 s; a mesma
operação retomou e concluiu
em 236,503 s. Foram implementados orçamento de 210 s, limite de quatro passos
por execução e retirada de conferências duplicadas, com retorno incompleto
retomável. O orçamento não cancela chamadas Google nem garante duração.
Ver [registro nativo no produtor](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/codex/inicializacao-financeira-carteira/r53/inicializacao/NATIVO-2026-10-27.md).
Na segunda cópia, a versão corrigida concluiu em 283,416 s; repetição em
150,489 s, estado comparado igual. Regras, fórmulas, formatos e financeiro
conferidos externamente; ambas as cópias estão na lixeira. A lista de
acionadores ficou vazia para a conta conectada. Ainda falta otimizar a
latência e provar automações/identidade/integração, sem tratar esse ensaio
financeiro como uma ficha inteira pronta.

O retorno financeiro mantém `criacaoDisponivel=false`. L2 sem emissão é
`{"versao":1,"graus":[]}` somente no modo salarial por fórmula; o leitor real
o aceita e as fórmulas condicionam o ciclo a N2 numérica. Isso não libera o
modo legado nem cria dinheiro inicial. Nível/XP e regras da mesa são
preservados neste domínio, não inicializados como personagem novo.

Os flags do contexto são pré-condições de um futuro criador confiável,
**não autenticação ou prova vinda do navegador**. Ainda faltam inventário
pessoal completo, propriedades de recuperação, automações, responsabilidade
e execução compatível com drive.file. O consumidor permanece bloqueado,
mesmo com o domínio financeiro concluído. Não declarar a etapa 7 pronta.

## Inventário financeiro anterior e domínios ainda exigidos

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

As quatro entradas por missão foram inventariadas no protótipo financeiro.
Os dados do editor de cartões ainda precisam de inventário completo do produtor.
Essa tabela é um
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
