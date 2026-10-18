# Lacunas e reprodução separada do produtor B47

Fonte examinada: `Ficha---RPG-JJK@ccbd053c8f7e68f8b4ac223f721b309111d2dcc0`.
Nenhum arquivo desse repositório ou da ficha oficial foi alterado. Esta lista
não autoriza publicação, migração ou uso de Google/LibreOffice.

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
