# Retomada R53 · atualizada em 21/10/2026

**Guias e limpeza · 21/10:** `/guia`, `/ficha guia` e `GC:guia ficha`
publicados, com nove assuntos e orientação de revisão humana. Suíte final:
896/895/1 online opcional. As cópias sintéticas B47/R53 foram levadas à
lixeira a pedido do usuário; os links dos ensaios abaixo são históricos.
Estado publicado, verificações e limpeza em
[relatório das guias](../pesquisa/validacao/2026-10-21-guias/RELATORIO.md).

**Encerramento posterior:** defeitos da entidade corrigidos e publicados
(`11cdc9f`), negativos preservados, suíte Linux 890/889/1 opcional pulado.
Troca rápida revelou um defeito do produtor: corrigido, ensaiado em cópia,
aplicado à oficial com autorização e registrado em `Ficha---RPG-JJK@5441801`.
Painel público conferido com duas identidades simuladas; ensaio manual com
outra pessoa permanece complementar. Merge da PR 67 autorizado pelo usuário.
[Estado final, evidências e limites](../pesquisa/validacao/2026-10-20-r53-pendentes/CORRECOES.md).
Os estados pendentes nas seções abaixo são históricos.

**Publicado em 20/10, 09h49, por pedido posterior do usuário:** pacote do
commit testado `939d2ed`, operação concluída, bot online em cinco servidores
e nova redação confirmada no tópico de testes. Recursos permaneceram 700 MB/
0,68 vCPU. [Registro da publicação e pendências atuais](../pesquisa/validacao/2026-10-20-r53-pendentes/PUBLICACAO.md).
O estado “não publicado” abaixo descreve o encerramento anterior da bateria.

## Execução de 20/10/2026

Registro completo, expectativas, mensagens Discord, defeitos e limites:
[bateria dos casos pendentes](../pesquisa/validacao/2026-10-20-r53-pendentes/RELATORIO.md).
Código local testado `939d2ed`; publicado permanece a referência `c1724f0`
fornecida pelo usuário, sem nova implantação ou auditoria do hash instalado.

| Caso | Situação em 20/10 |
|---|---|
| Ampliação entre Classes permitidas | Executado; preservação/recuperação e negativo passaram; link/XLSX nativo concordaram. |
| Entidade completa | Executado válido/excesso; excesso detectado, porém o válido sofre seis falsos erros: Famílias R53 e cinco resultados de perícias com sinal `+`. Correção funcional pendente. |
| Liberação do personagem/entidade | Válidos e sem acesso executados; cartões e rejeição de acesso passaram. Veredito global tem os seis falsos erros da entidade. |
| Técnica Máxima do personagem/entidade | Válidas e sem acesso executadas, mesmo limite global da entidade. |
| Forma custom em cartão | Pendente, aprovação sintética exata anterior e alteração posterior executados; 0/2 → 0/0 → 0/2. Limite sem recálculo explícito; definição restaurada, sem gravar aprovação. |
| Troca rápida | Parcial: versões preservadas em oito capturas, todas estáveis; janela transitória/releitura real ainda não capturada. Primeira tentativa com aba errada descartada. |
| Segunda pessoa | Não executado; depende de outra pessoa/sessão real autorizada. |
| Dois ajustes de texto | Implementados com regressões no `939d2ed`, sem alterar veredito/limites. Não publicados. |

34 testes R53 e 246 da ficha passaram (um online opcional pulado).
Suíte completa no Windows: 874 executados, 29 erros, uma falha, 65 pulados;
limitações de plataforma/mídia documentadas, sem declarar suíte verde.
Pacote regenerado e auditado, não publicado. Próxima execução: corrigir os
dois defeitos funcionais da entidade, repetir os casos afetados, capturar a
transição rápida, testar outra pessoa e verificar a suíte em Linux compatível.

As seções seguintes conservam o roteiro e o ponto de partida de 19/10;
o status atual é a tabela acima.

## Ponto de partida

- Repositório: `cupcake-mochi/RPG---BOT`; código atual em `Closure/`.
- Branch: `claude/project-thread-zzfh12`;
  [PR 67, rascunho](https://github.com/cupcake-mochi/RPG---BOT/pull/67).
- Código testado: `c1724f0effad9d14fd4bd02525fcf93395e1d93f`.
  Primeiro registro da bateria: `f560f23a36ae8b8b60794301bb2d543ae695df86`.
  Commits posteriores de documentação não significam runtime novo.
- PRs 65/66 já estão em `main` (`93271b7` na conferência desta retomada).
- Produtor R53: `Ficha---RPG-JJK`, branch `codex/publicacao-r53`, PR 4,
  commit `4b22da5420263a8885e28a508cbc39938dd9d9da`. O main da ficha ainda
  é B47: conferir os dois refs antes de escolher a fonte.
- Mizuki confirmou a atualização da Discloud; o comportamento R53 foi
  verificado em 13 respostas reais. Os hashes instalados não foram auditados
  nesta bateria. Não repetir implantação por rotina.

Primeiro conferir árvore local, remoto e PR; preservar mudanças existentes.
Não usar reset destrutivo ou force-push. Ler
[INTEGRACAO-R53.md](../dados/ficha/INTEGRACAO-R53.md) e
[BATERIA-NATIVA-R53.md](../dados/ficha/BATERIA-NATIVA-R53.md), que contém os
links das três cópias sintéticas, resultados, evidências e limites.

## Roteiro original da bateria nativa de 19/10

Cada caso deve partir de uma cópia sintética, ter expectativa anotada antes
do envio e passar por Sheets → exportação → Discord. Testar pelo link e
comparar com XLSX nativo quando houver salvamento ou recálculo envolvido.
Não alterar a oficial, importar XLSX no Google ou forjar MONTAGENS/ANALISE
para substituir o ensaio nativo. Fixtures técnicas têm de ser identificadas.

| Prioridade | Caso pendente | O que conferir |
|---|---|---|
| 1 | Ampliação em nível compatível, com duas Classes disponíveis | Guardar escolhas na Classe menor, ampliar, mudar apenas o que a regra permite, voltar e recuperar a versão anterior. Conferir versões exportadas, limite de pontos, custo e PE; mudança proibida de função/peça deve aparecer como erro. A tentativa de Classe indisponível em nível 2 não substitui este caso. |
| 1 | Entidade completa com básica e especiais | Nível, Classe, atributos, tipos, distribuição de Famílias própria da entidade, orçamento e resultados de cartões. Fazer um caso válido e outro com excesso; não inferir campos ausentes dos resultados que se quer conferir. |
| 1 | Liberação do personagem e da entidade | Classe/requisito de acesso, portas de função, orçamento, restrições, teto e avisos. Um caso válido e um sem acesso suficiente. |
| 1 | Técnica Máxima do personagem e da entidade | Requisito de acesso/trunfo, função fixa, custo, resultados e versões exportadas; não usar o resultado da própria ficha como única expectativa. |
| 2 | Peça/Forma custom em cartão, além de perícia | Cadastro pendente, definição exata aprovada e alteração posterior. Mostrar explicitamente o trecho **sem recálculo independente**; aprovação não transforma prosa em bônus. |
| 2 | Salvamento sob troca rápida entre Classes permitidas | Capturar análise durante a transição e depois de estabilizar; confirmar que o bot relê e não mistura versões. A releitura real em dois acessos já passou, mas não foi este cenário completo. |
| 2 | Segunda pessoa no painel | Conferir acesso/navegação e encerramento dos controles com outro participante autorizado. Depende de uma segunda sessão/pessoa; não compartilhar credenciais nem presumir teste multiusuário pela sessão atual. |

Para os casos de nível alto, usar progressão compatível com as regras da
campanha. Não modificar silenciosamente a configuração autorizada do servidor
para tornar um caso válido. Exceção sintética de campanha precisa ficar
separada, identificada e aprovada para o ensaio.

## Fila de código, dados e decisão humana

**Bot e sua base:** a integração atual recalcula cartões R53; o corpus geral
e o índice permanecem R51/R52. Falta comparar as demais mudanças do livro R53,
atualizar o que realmente mudou e criar regressões independentes. Também há
polimento de texto: “pendências abertas” com contador zero deve distinguir
partes não conferidas de pendências detectadas. Não mudar o veredito para
esconder limites. Revisão e merge da PR 67 continuam pendentes.

**Dados do produtor:** antes de retomar lacunas antigas, conferir o contrato
R53 atual e os emissores/consumidores. Só considerar resolvido o campo que
passou a ser exportado com semântica suficiente. Documentar ausências e
reproduções separadamente; não alterar a ficha oficial dentro deste trabalho.
Consultar `dados/ficha/LACUNAS-PRODUTOR-B47.md` sem presumir que um defeito
histórico foi corrigido ou continua presente sem nova conferência.

**Mestre:** aprendizado, histórico de marcos/treinos, autorização efetiva,
requisitos livres, COMO É, alvos, narrativa e Alma não são certificados pela
conta determinística. MESTRE VIU continua sendo lembrete. Os testes de custom
usaram aprovações sintéticas anteriores; não representam autorização real de
uma mesa. Zero erros e pendências não elimina partes não conferidas.

## Execução e encerramento

Suíte já executada: 882 testes, 881 aprovados, 1 online opcional pulado;
33 direcionados R53 passaram. Comandos a partir de `Closure/src/`:

```sh
../.venv/bin/python -m unittest discover -s testes -p test_r53.py
../.venv/bin/python -m unittest discover -s testes
```

Usar regressões apropriadas a mudanças novas; não repetir a suíte completa
nem a bateria encerrada apenas por rotina. Se mudar runtime, regenerar e
conferir o pacote sem segredos, bancos ou campanha real. Preservar memória,
mídia, personalidade e demais funcionalidades. Sem chamadas pagas a modelos.
Novos testes e eventuais publicações devem respeitar as autorizações vigentes;
registrar separadamente código testado, código publicado e evidência externa.
