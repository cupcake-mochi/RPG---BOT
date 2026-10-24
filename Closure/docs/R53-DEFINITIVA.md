# Closure e a ficha R53 definitiva · 24/10/2026

Atualização da [PR 73](https://github.com/cupcake-mochi/RPG---BOT/pull/73),
a partir do bot `8752c82`, com merge autorizado pelo Mizuki. O ZIP é entregue
para atualização manual na Discloud; não houve deploy nem alteração de acesso.
Modelo recomendado: GPT-6.1, esforço alto para integração; médio para revisão textual.

## Inventário e compatibilidade

| Caminho | Comportamento conferido |
|---|---|
| `ficha_leitor.de_link` | Exportação CSV da aba ANALISE pelo gviz, quatro colunas, cabeçalho explícito |
| `ficha_leitor.de_csv` / `de_xlsx` | Identidade pela coluna A; valor pela B; C apenas metadado descritivo; D identifica a parte |
| `ficha_esquema.variante` / `ficha_corretor.conferir` | 1, 2, variante histórica TR-v4, B47-v11 e R53-v12; versão/variante desconhecida interrompe a conferência |
| `ficha_esquema.campos_r53` / `ficha_r53` | 18.393 chaves, incluindo 10.173 `r53.*`; cartões com esquema 2 |
| Dinheiro, salário e emissão | Não há leitura direta dessas células nem campos correspondentes na ANALISE; o bot não exibe nem certifica esses valores |

O formato 12 já era aceito antes desta atualização. Não foi necessário mudar
o leitor, relaxar a validação ou acrescentar suporte especulativo aos formatos
3 e 5–10, que não eram aceitos. Os formatos anteriores suportados permanecem.
Os limites de linhas e tamanho comportam a exportação real testada.

Não há quebra por O86 ter mudado de saldo para caixa de lançamento: o consumidor
não usa essa célula. O total para consulta humana é FICHA PESSOAL!W86. Não se
criaram chaves financeiras nem formato 13; essa ampliação não é necessária ao
escopo atual e exigiria proposta e autorização próprias.

As referências antigas em C de `custom.2.*`/`custom.3.*` não são endereços que
o bot consulta. Os valores continuam vindo de B. A regressão troca esses
metadados e exige resultado e pendências idênticos, sem alterar aprovações.

## Explicações atualizadas

Guias de criação, planilha e mestre, em português e inglês:

- emissão obrigatória em AT3/O39; repetir EMITIR não muda a data;
- correção em O38 somente da emissão atual até hoje; sem emissão, somente hoje;
  salários vencidos preservados e ciclo aberto reiniciado na data nova;
- salário por fórmula, sem exigir ativação diária; período padrão de 30 dias,
  Grau no fechamento, mínimo de 25%, 100% com 3 participações e pesos atuais;
- O86 como ± GASTO / GANHO, exemplos −500/+2000, espera até limpar, W86 como
  total e consulta ao EXTRATO e aos últimos dez créditos;
- correção de missão por BI11/BO11 no celular, confirmação e motivos de recusa;
- paleta em C27, espera de aproximadamente 20 segundos sem fechar/recarregar;
- invocações 2–6 e 8–12 recolhidas, + da lateral e « no celular;
- Android por edição de células, sem depender de menus ou abertura do arquivo.

`prompt.montar` recupera os mesmos textos editoriais de `guias_ficha` para
perguntas relacionadas e continuações nos quatro turnos recentes. Vale para
Closure e Kal'tsit; a configuração de idioma continua prevalecendo. Perguntas
selecionam as páginas, sem serem interpoladas nas instruções de referência.
Não há segunda cópia das regras no prompt nem chamada paga para essa seleção.

O link de modelo oficial nos guias e nas respostas de recursos públicos aponta
para a [ficha pública nível 2](../dados/ficha/MODELOS.md), indicada posteriormente
pelo Mizuki. A definitiva do servidor permanece somente como referência
histórica do ensaio abaixo, sem ser oferecida pelo bot.

## Fontes

Produtor: [cupcake-mochi/Ficha---RPG-JJK, commit 53cb869](https://github.com/cupcake-mochi/Ficha---RPG-JJK/commit/53cb869c52d4f9d1063ef7a053ab7eb9b69e36ab),
HEAD observado de `codex/otimizacao-android-r53`.

- `ESQUEMA-ANALISE.md` e `apps-script/Analise.gs`;
- `r53/ENTREGA.md` e `r53/RETOMADA.md` (histórico da migração 11 → 12);
- `salarios/README.md`, seção **Emissão obrigatória**, que prevalece sobre a emissão antiga;
- `r53/diagnostico-android/SALARIO-PLANO-2026-10-24.md`;
- `r53/diagnostico-android/PALETA-LOTE-2026-10-24.md`;
- `r53/diagnostico-android/FICHA-DEFINITIVA-2026-10-24.md`.

Há registros históricos com 18.394 “chaves”; a leitura atual distingue
**18.394 linhas com cabeçalho** de **18.393 chaves de dados**. O trecho do
primeiro nome emitir automaticamente também é histórico: a seção posterior
de emissão obrigatória e a leitura nativa confirmam EMITIR explícito.

## Teste nativo

Foi criada uma cópia integral descartável da definitiva, sem alterar a base,
a Original ou fichas de jogadores. Personagem sintético: Bastião/Muro, nível 2,
atributos 3/2/2/1/1, nome de teste. Entradas foram lidas antes, respeitando os
menus e preservando fórmulas, validações e formatação.

O XLSX foi exportado nativamente pelo Drive. A ANALISE foi lida também pela
API em faixas delimitadas e convertida para CSV, passando pelo mesmo `de_csv`
do bot. **18.393/18.393 campos coincidiram**, incluindo valor, célula e parte;
nenhuma chave faltou ou sobrou em relação ao manifesto do bot.

A conferência terminou normalmente, com três diagnósticos do preenchimento:
treinos ainda incompletos e nenhuma Família escolhida como Livre/Fechada,
quando a campanha exige duas/três. O zero do diagnóstico é a contagem de
escolhas, não o valor configurado da regra. Também retornou seis pendências e onze limites. Esse ensaio
comprova leitura e diagnóstico da cópia, não aprovação integral do personagem.

O painel nativo permaneceu “Não emitida”, O38 vazio e W86 em ¥150.000.
As escritas por API não disparam onEdit: não se afirma ensaio de execução dos
scripts, emissão, paleta ou operação no aplicativo Android nesta rodada.
O transporte HTTP anônimo do gviz não foi exercitado nessa cópia; a comparação
CSV usou valores autenticados da API, sem mudar compartilhamento.

Snapshots integrais e XLSX sintético ficaram fora do Git. Evidência agregada
e resultados da suíte ficam no relatório de validação desta rodada.

## Modelo público nível 2 e prova de correção

Na segunda rodada, a cópia descartável do modelo público indicado pelo Mizuki
foi preenchida com o mesmo personagem sintético. O método real
`Ficha.analisar_fonte`, usado pelos comandos de análise, recebeu os XLSX nativos
como anexos e gerou quatro páginas de painel. Leitor, corretor e renderizador
foram executados sem substituições; somente o transporte Discord foi simulado.

Com Vida 23 e Defesa 13, nenhuma dessas duas contas foi apontada como erro.
Após trocar temporariamente ambas para 999 **somente na cópia**, o painel exibiu
“Vida: está 999, o certo é 23” e “Defesa: está 999, o certo é 13”. As fórmulas
originais foram restauradas e a API confirmou novamente 23 e 13.
A mesma prova passou com o código extraído do ZIP de entrega.

O personagem segue parcial (treinos e Famílias por escolher); o ensaio comprova
essas contas e a integração do anexo, sem certificar toda possível ficha.
O bot aponta correções, mas nunca escreve na planilha. O modelo público está
registrado no Git em `dados/ficha/MODELOS.md`, com o link nativo para cópia.

## Reproduzir

Em `Closure/`, prepare o núcleo com `.venv/bin/python ferramentas/empacotar.py`.
Em `Closure/src/`, execute:

```sh
../.venv/bin/python -m unittest discover -s testes
```

Os testes específicos ficam em `test_r53_definitiva.py`: volume/paridade
CSV/XLSX, coluna C sem efeito semântico, recusa do formato 13 e recuperação
das explicações no contexto de ambas as personagens. Os testes existentes
continuam cobrindo os formatos legados, cartões R53, aprovação e interface.
