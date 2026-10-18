# Lacunas e reprodução separada do produtor B47

Fonte examinada: `Ficha---RPG-JJK@ccbd053c8f7e68f8b4ac223f721b309111d2dcc0`.
Nenhum arquivo desse repositório ou da ficha oficial foi alterado. Esta lista
não autoriza publicação, migração ou uso de Google/LibreOffice.

Revisão seguinte de 18/10: acrescentados abaixo o teto de Quebra Coisa e a
apresentação fixa da Máxima com Toca a Alma. São quatro reproduções estáticas,
sem ensaio nativo. Evidência adicional em
`pesquisa/validacao/2026-10-18-b47-maxima/produtor-estatico.json`.

Reexame estático em 18/10: fragmentos entregues ainda contêm os critérios A54
diretos e a apresentação de Controle com CD-base, conforme o relatório
`pesquisa/validacao/2026-10-18-b47-cobertura/produtor-estatico.json` (hashes dos
fontes/artefatos). A leitura pública CSV/XLSX da oficial não ensaiou esses dois
cenários. Proposta separada de campos/semântica/testes em
[PROPOSTA-CONTRATO-B47.md](PROPOSTA-CONTRATO-B47.md); nenhuma mudança do produtor.

## Entradas/resultados ausentes do contrato entregue

O manifesto `src/closure_bot/recursos/b47-campos.tsv` enumera exatamente o
contrato emitido. As 485 entradas exclusivas do rascunho TR-v4 estão no
`MAPA-B47-DELTA.tsv`; adicionar seu número de versão não recupera esses dados.

| Conta | O que existe | O que falta para conferir integralmente | Proposta no produtor, em entrega futura |
| --- | --- | --- | --- |
| CD/conjuração/ataques pessoais | Resultado e Buff de cada caixa | Seletores dos atributos pessoais; não confundir com `invocacao.N.atributo_acerto` | Exportar cada seletor como entrada própria, por chave estável |
| TR, Perícias e Ofícios do livro | Treino/especialização | Atributo escolhido quando variável, ajustes e resultados numéricos | Exportar as entradas e os resultados separados, reconciliando o rascunho TR-v4 por significado |
| TR da entidade | TR treinado, atributo físico e quatro ajustes | Quatro resultados finais | Exportar resultados, sem renomear os ajustes existentes |
| Carga | Texto final agregado e nomes de inventário | Quantidades, Volumes livres, ajuste de limite e total/limite separados | Exportar entradas de cada posição, inclusive vazias, e resultados numéricos próprios |
| Deslocamento | Resultado, Buff e Exaustão | Carga independente e ajuste do limite, que decidem a penalidade | Completar carga; opcionalmente exportar os estados intermediários como resultados, sem tomá-los por entradas |
| Teto de invocações ativas | Definição do efeito e aviso | Resultado do teto, identidades/estado de quais estão ativas | Exportar resultado e estados, sem tratar as 12 fichas cadastradas como 12 entidades ativas |
| Histórico/aprendizado | Escolhas finais e texto | Ordem dos marcos, aquisições e autorizações | Vincular registros verificáveis do mestre; não transformar narrativa do jogador em prova |

Reprodução offline: comparar as chaves do manifesto e inspecionar os fragmentos
JSON dos GS, sem executá-los. Em `apps-script/Ficha.gs`, os resultados de CD e
ataques usam os seletores de FICHA em Z67, AK67 e AE70, que não têm entradas
equivalentes no contrato. Essas coordenadas identificam a reprodução **nesse
SHA**, nunca a identidade de um campo no leitor.

O bot detecta totais impossíveis e confere resultados de troca independentes
dessas entradas. Um resultado compatível com várias escolhas não revela qual
delas foi selecionada. O painel mantém essa distinção.

## Critérios de efeito com nomes literais contendo curingas

A inspeção estática encontrou `SUMIFS`/`COUNTIFS` em
`ficha-v01/configuracao.py` e `ficha-v01/custom_progressao.py` com critério
`A<n>` direto para a caixa. Nomes custom com `*`, `?` e `~` são textos válidos,
mas esses caracteres têm significado especial em critérios dessas funções.
Há outros usos que já chamam `custom_criacao.criterio`; os critérios de efeito
citados ainda precisam da mesma proteção. Isto é uma reprodução estática e um
roteiro de teste nativo; não foi executado no Google nesta tarefa.
O JSON entregue em `apps-script/Configuracao.gs`, `DADOS_CONFIG!B54:E54`,
confirma o critério `A54` direto nas quatro contas, enquanto A54 já protege o
cadastro do nome. Assim, a proteção do cadastro não protege a aplicação do efeito.

Caso mínimo para futura cópia descartável autorizada:

1. Cadastrar as Perícias `Runa*` e `Runas`, ambas de Inteligência, sem treino,
   especialização nem ajuste. Usar Inteligência 1.
2. Ligar somente um efeito `somar 7` em `Perícia · Runas`.
3. Esperado por identidade: `Runa* = 1`; `Runas = 8`.
4. O critério não escapado `Perícia · Runa*` também casa com `Perícia · Runas`,
   podendo aplicar 7 à primeira. Repetir com `?`/`~`, trocas e conflitos.

Correção proposta: escapar `~`, `*`, `?`, nessa ordem, em **todos** os critérios
textuais de identidade dos efeitos, reutilizando o helper literal existente.
Validar soma, troca, contagem de trocas e diagnóstico de entrada inválida; não
escapar critérios que deliberadamente sejam padrões. Depois validar em cópia
descartável, rever contrato/artefatos e seguir o processo próprio do produtor.

Regressão do consumidor: `test_nome_literal_com_curinga_nao_recebe_efeito_da_outra_pericia`,
em `test_b47_derivados.py`. O bot compara os nomes literalmente e reprova a
contagem cruzada. Não reproduz o possível defeito do produtor para aceitar um
resultado incorreto. Esse teste não substitui o teste nativo da fórmula.

## Apresentação da CD exclusiva do Controle da entidade

Inspeção estática de `ficha-v01/ficha_invocacoes.py`, conta `resolve`:
o ataque exibe seu bônus e acrescenta `TR CD` usando a CD-base da entidade.
O texto de aviso reconhece saldo zero e +2 de Controle, mas essa apresentação
não soma o +2 à CD exclusiva. A conta também não separa CD do dano e do Controle
numa ficha que tenha ambos. Não se executou teste nativo nesta tarefa.

Reprodução em futura cópia descartável autorizada:

1. Dono no nível 2 (Maestria 1); entidade com Força 3 como atributo de acerto.
2. Especial Classe 1, Projétil, Prende e Precisão, sem Restrição; Famílias com
   preços normais. Dois pontos iniciais, um em cada Melhoria, saldo zero.
3. Ataque: `3 + 1 + 2 = +6`. CD-base: `8 + 3 + 1 = 12`. Precisão vai para o
   ataque. Saldo zero concede +2 somente à CD de Prende: **14**.
4. A apresentação atual monta `Ataque +6 · TR CD 12`, embora o TR mencionado
   depois do ataque seja o do Controle. Esperado: `Ataque +6 · TR CD 14`.
5. Remover Precisão deixa saldo 1: ataque +4, Controle CD 12; descartar esse
   dano escrevendo Sem dano não passa a conceder +2.

Correção proposta no produtor: calcular o saldo de forma independente e
apresentar a CD exclusiva do Controle com o acréscimo somente quando devido.
Se dano e Controle usarem CDs diferentes, apresentá-las separadamente e
exportar resultados distintos num contrato futuro. Não mudar a CD global da
entidade nem a do dano para aplicar o bônus exclusivo.

No bot, `test_formula_atual_sem_bonus_obrigatorio_fica_pendente` conserva
uma pendência precisa para essa fórmula conhecida e recusa outros números
incorretos. Saldo positivo não recebe a tolerância de +2. A montagem continua
parcial quanto a permissões, escolha do TR e resultado no sucesso.

## Teto de Quebra Coisa

O livro em `catalogo--cat-castigo-dano` manda contar o multiplicador de
Quebra Coisa na montagem. O produtor em `ficha_amaldicoada.py` declara
`MULTIPLICA = ("Remate", 1.25)`, sem Quebra Coisa em `PECAS_CITADAS`;
`ficha_invocacoes.py` também usa esse multiplicador único na conferência.
Esta é inspeção dos emissores, sem recálculo no Google.

Caso mínimo: Classe 3, Projétil, Quebra Coisa a preço normal, sem Restrição.
O saldo é `9 - 2 = 7`. Dobrar sete dados excede o teto 12; a base deve cair
para **6d8**, que dobra para 12 contra o objeto. O bot agora confere seis e
reprova sete, inclusive em Forma custom aprovada e Liberação. O adicional
de Salto/Queima/Estilhaço não reaplica o multiplicador. Remate vale contra
criaturas; não se multiplica 2 por 1,25 contra um mesmo alvo.

Proposta no produtor: incluir a identidade de Quebra Coisa e o multiplicador
de objeto na conferência do teto; preservar a diferença de alvo e os dados
secundários. Ensaiar seis/sete, adicionais, alias e Liberação em cópia
descartável antes de alterar o contrato/artefatos. Não se corrigiu a oficial.

## Apresentação fixa da Máxima com Alma

A fórmula emitida de `maxima.dano` imprime os dados da tabela de nível,
independentemente das Melhorias. Confirmada também no JSON entregue de
`apps-script/Ficha.gs`, tabela de remapeamento em `DADOS_AM`, linha 38,
coluna 308: destino `L356` e fórmula com `DADOS_AM!$HM$36` e sua média.
Coordenadas são diagnóstico desse artefato, nunca identidade no consumidor.

Caso mínimo: nível 17, Projétil, Toca a Alma. Montagem **3 de 8**, 25 PE,
tabela 24d8. O livro manda conservar a redução na Máxima: **12d8 de Alma**.
O campo fixo continua imprimindo `24d8 = 108`. O bot confere doze quando
exportados e mantém a permissão da Regra como revisão do mestre. Somente a
fórmula fixa exata recebe pendência específica; `999d8` continua erro.

Proposta no produtor: separar os dados da tabela e a quantidade efetiva da
aplicação, reduzindo Alma após as escolhas estruturadas. Manter genérica a
quantidade de Cura quando o campo não exporta tipo; não inferir um seletor
ausente do resultado. Combinações de Alma com adicionais/distribuição continuam
dependendo de regras e entradas suficientes, sem aprovação por prosa.
