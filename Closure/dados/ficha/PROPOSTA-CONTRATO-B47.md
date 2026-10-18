# Proposta separada de ampliação do produtor · 18/10/2026

**Proposta para revisão, não implementada na ficha nem aceita como novo formato
pelo bot.** Base examinada: `Ficha---RPG-JJK@ccbd053`. A entrega atual permanece
ANALISE 11/8.190 chaves. Aprovar esta proposta é uma decisão separada; não basta
alterar `formato.versao` numa cópia para obter as conferências abaixo.

## Regras do contrato proposto

- Preservar as identidades/partes/semânticas atuais e as variantes antigas. A
  próxima versão deve ser acordada com o produtor; não reservar um número apenas
  neste documento. Atualizar emissor, manifesto, leitor e regressões juntos.
- Exportar posições vazias, sem compactar registros. A quantidade de posições
  deve vir do esquema da entrega, não de um total declarado pelo jogador.
- Texto literal; marcações 0/1; números finitos na unidade indicada. Vazio não
  equivale a zero. Campo inexistente é exportação incompleta para a nova versão.
- Resultados são comparados, nunca usados para deduzir seletores, quantidades,
  fonte de benefício ou permissões. `.mestre_viu` continua sendo lembrete.
- Nas 485 adições TR-v4 ausentes, reutilizar a chave histórica somente se tipo,
  unidade e significado forem comprovadamente iguais. A versão 4 da campanha
  continua distinta da variante TR-v4.

## Seletores pessoais e competências

| Chaves propostas | Parte/tipo | Semântica e dependência |
| --- | --- | --- |
| `cd_de_feitico.atributo`, `conjuracao.atributo`, `corpo_a_corpo.atributo`, `a_distancia.atributo` | entrada/texto | Seletor efetivamente usado em cada caixa, nome literal do atributo; quando compartilham seletor, exportar o vínculo real para ambas, sem inferi-lo do total. Conferir as opções permitidas pelo produtor/livro. |
| `tr.<slug>.atributo/ajuste/bonus` | entrada/texto; entrada/número; resultado/número | Físico preserva a escolha fixa Força/Destreza; os outros três TR usam seu atributo obrigatório. Ajuste é independente; bônus é o total, sem o d20. |
| `pericia.<slug>.atributo/ajuste/bonus` | mesmos tipos | Atributo do catálogo, ajuste separado e total. Treino/especialista já existentes permanecem nas mesmas chaves e orçamentos. |
| `oficio.<slug>.atributo/ajuste/bonus` | mesmos tipos | Atributo efetivamente escolhido para a tarefa. Mudança do padrão exige revisão humana da tarefa, mesmo com número correto. |
| `invocacao.N.tr.<slug>.bonus` | resultado/número | Quatro totais finais. Reutilizar `tr_treinado`, `atributo_fisico`, atributos base/buff e os quatro ajustes atuais como entradas. `buff.pericia.K` continua resultado histórico; não renomear nem somar como Buff. |

`<slug>` é a identidade estável publicada para as quatro resistências e os
catálogos do livro; `N` percorre as doze posições de entidade, inclusive vazias.
Competências custom já exportam atributo/ajuste/resultado e não precisam de
campos duplicados para esta ampliação.

Testes exigidos: atributos diferentes com resultados coincidentes; cada seletor
alterado sem alterar o total; treino/especialização inválidos; efeitos somar e
trocar por zero; competência sem ajuste versus ajuste zero; Ofício com atributo
editado; entidades com atributos/TR diferentes; nenhuma comparação do bônus
exportado pode definir qual atributo foi escolhido.

## Inventário e carga

O namespace abaixo é novo para não reutilizar as linhas agregadas `equipavel.N`
e `item.N` da B47. A revisão do produtor deve fixar suas capacidades/identidades
de posição e o sentido de cada linha, incluindo menu e linhas livres.

| Chaves propostas | Parte/tipo | Semântica |
| --- | --- | --- |
| `inventario.equipavel.N.nome/quantidade/grau` | entradas/texto, inteiro, texto | Identidade selecionada, quantidade física não negativa e grau realmente escolhido; posição vazia permanece exportada. |
| `inventario.equipavel.N.volume_declarado` | entrada/número ou vazio | Volume **unitário** livre somente onde o molde permite. Zero explícito é válido; item tabelado usa o catálogo. |
| `inventario.equipavel.N.volume_unitario/volume_total` | resultados/número | Unitário resolvido e quantidade × unitário, exportados separadamente. Não usar esses resultados para reconstruir entradas. |
| `inventario.item.N.nome/quantidade/volume_declarado` | entradas/texto, inteiro, número ou vazio | Mesma regra nas posições de itens. Explicitar a unidade dos antigos campos antes de reconciliar com TR-v4. |
| `inventario.item.N.volume_unitario/volume_total` | resultados/número | Mesma regra dos equipáveis. |
| `carga.ajuste_limite` | entrada/número ou vazio | Buff/Debuff do limite, sem confundir com o limite final. Efeitos identificados permanecem nas linhas atuais. |
| `carga.total/limite` | resultados/número | Volume carregado e teto após ajustes/efeitos. Uniforme vestido entra uma vez, conforme a regra; não multiplicar novamente um Volume total. |
| `invocacao.N.carga.item.K.nome/volume` | entradas/texto e número | Cada linha armazenada com **Volume total declarado**, como a variante TR-v4. Se mudar para unitário, usar chave diferente e exportar quantidade própria. |
| `invocacao.N.carga.total/limite` | resultados/número | Totais reconstruíveis por linhas, atributos e regra; autorização/anatomia do armazenamento continua humana. |

Testes exigidos: quantidade 0/1/várias; posição vazia entre preenchidas; item
tabelado com Volume adulterado; livre com zero e decimal; uniforme vestido sem
contagem dupla; arma de duas mãos com secundária; armazenamento sem multiplicar
duas vezes; total/limite adulterados; falta de uma posição; falta de Força,
meia marcha e carga acima do dobro sem multiplicar penalidades.

## Estado das entidades e CDs de Controle

| Chaves propostas | Parte/tipo | Semântica |
| --- | --- | --- |
| `invocacoes.limite_ativas` | resultado/inteiro | Teto após a base autorizada da Trilha e efeitos próprios. As doze fichas cadastradas não são doze entidades ativas. |
| `invocacao.N.estado.ativa` | entrada/0 ou 1 | Declaração atual e explícita do jogador. Conferir quantidade contra o teto; não afirmar que prova o estado real da cena ou o consentimento do mestre. |
| `invocacao.N.<carta>.bonus_acerto` | resultado/número ou vazio | Bônus do ataque da carta quando aplicável, separado de prosa. |
| `invocacao.N.<carta>.cd_dano/cd_controle` | resultados/número ou vazio | CDs distintas quando a montagem tem os dois testes. +2 de saldo zero somente na CD do Controle. Não alterar a CD global da entidade. |
| `invocacao.N.<carta>.controle.tr_escolhido` | entrada/texto ou vazio | Escolha explícita quando a regra permitir selecionar TR para o Controle. Não derivar da frase de resolução. |

`<carta>` usa os prefixos já existentes `bas.K`, `esp.K` e, onde cabível,
`ext.K`. Confirmar cada aplicabilidade no emissor; carta sem Controle mantém
`cd_controle` vazia, sem transformar ausência de teste em CD zero.

Testes exigidos: troca de Trilha/base exige nova aprovação; duas entidades com
Famílias independentes; declaração de ativa sem nome; teto 2/4 e alteração por
efeito autorizado; Principal com mais de uma ativa; ataque+Controle com saldo
zero/positivo; Precisão; Sem dano não fabrica saldo zero; CDs diferentes no
mesmo especial. O bot deve recalcular saldo por Classe, Forma, peças e descontos.

## O que continuará dependendo do mestre

Aprendizado, sequência histórica dos marcos, concessões sem vínculo, requisitos
livres, aplicação narrativa, alvos/distribuição antes da rolagem e interações de
Alma não automatizadas. Novos totais não transformam esses fatos em prova.

## Processo de entrega futura

Revisar proposta → implementar no **produtor**, em tarefa separada → ensaiar
em cópia sintética autorizada no Sheets → conferir erros/fórmulas/entradas e
restauração → publicar esquema/manifestações e exemplos sem dados pessoais →
adaptar o bot e testar compatibilidade por identidade → piloto de link/XLSX e
painel → revisão/merge/implantação somente com suas autorizações próprias.

Os dois defeitos estáticos já registrados permanecem separados em
[LACUNAS-PRODUTOR-B47.md](LACUNAS-PRODUTOR-B47.md). Não houve mudança do produtor,
teste Google ou migração para executar esta proposta.
