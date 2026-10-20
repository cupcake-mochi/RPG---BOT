# Encerramento das correções R53 · 20/10/2026

Este registro atualiza os estados pendentes dos relatórios anteriores.

## Bot: entidade corrigida e publicada

Código: `11cdc9fc6417ff33eb03f38864c6912968081a00`.
CI e preparação do núcleo: `6250466b7fca4dd28bc02646bdb5755ec6bfe7b7`.

- Formato 12 passa pelo validador de Famílias com contexto/campanha, como o
  formato 11. As escolhas próprias da entidade não usam as Famílias da técnica.
- Leitor aceita sinal `+` em números, preservando nomes/textos literais e
  rejeitando conteúdo não numérico. Perícias `+3/+4/+5` são conferidas como números.
- A abertura das duas guias também deixou de afirmar pendências inexistentes.
- Regressões cobrem famílias repetidas/excesso, bônus adulterado, preservação
  de texto literal e navegação pública por participantes simulados distintos.

GitHub Actions/Linux: **890 executados, 889 aprovados, um online opcional
pulado**, em 121,359 s. [Execução completa](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/39427442467).
A primeira execução pulava 65 casos por ausência do núcleo local preparado;
o workflow foi corrigido para montar o núcleo antes da descoberta dos testes.
Nenhuma chamada paga a modelo; sem segredos de produção no runner.

Pacote de 75 arquivos auditado e publicado no app Guias do Ciclo em **10h14**.
SHA256 `19449c9a224d703bd13fe9d87125d2151c10fa3c21b9046e0e19b3fc08dd5098`.
Discloud confirmou Concluído e startup às `10:14:31,163`, em cinco servidores.
Nenhuma edição de variáveis, bancos ou recursos da hospedagem.

| Reensaio externo após publicação | Resultado |
|---|---|
| [Entidade e oito cartões válidos, link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562092020426608663) | 0 erros/0 pendências; cinco bônus de perícia conferidos |
| [Mesmo estado, XLSX nativo 15](https://discord.com/channels/1357866906341736488/1561410667108368575/1562092213326979097) | 0/0; mesmo resultado |
| [XLSX nativo com excesso](https://discord.com/channels/1357866906341736488/1561410667108368575/1562092544370802771) | Um erro real de saldo; os seis falsos erros desapareceram |
| [XLSX nativo sem acesso](https://discord.com/channels/1357866906341736488/1561410667108368575/1562092666303291435) | Seis erros reais de acesso/contagem; os seis falsos erros desapareceram |

As mesmas 18.393 chaves do estado antes reprovado foram reanalisadas, sem
editar a exportação para obter verde. `24-entidade-corrigida-resultado.json`
tem a paridade CSV/XLSX sem diferenças. Veredito geral continua **pendente**
pelas partes não conferidas; 0/0 não certifica autorização, história ou narrativa.

## Salvamento rápido: defeito novo no produtor e correção

A rodada de estresse capturou a transição real. Também reproduziu perda de
versão: a Classe 1, que tinha Dano 3, passou a guardar Dano 6 da Classe 2.
Não é um defeito do leitor do bot nem uma fixture adulterada. A exportação
nativa do defeito foi preservada localmente antes da restauração.

No controlador do produtor, o document lock era liberado antes de confirmar
as escritas pendentes. A correção chama `SpreadsheetApp.flush()` mantendo o
lock e o libera em `finally`, inclusive se o flush falhar. É a ordem recomendada
pela [documentação do Google](https://developers.google.com/apps-script/reference/lock/lock.html).

Foi aplicado primeiro só à cópia sintética 05. Após restaurar os três pontos
originais por edição nativa, três rodadas de 12 trocas preservaram C1=3/C2=6.
Foram capturadas transições reais; o método `_ler_estavel` foi instrumentado
sem substituir respostas: todas vieram por HTTP do Google. Na rodada 30,
o bot leu duas vezes e terminou estável. A rodada 29 já leu estado estável
nas duas chamadas; não é prova de retry. O estado final da cópia voltou a
coincidir com o XLSX de referência nas 18.393 chaves.

O usuário então autorizou **oficial e fonte**. Somente `EditorR53.gs` foi
alterado no projeto vinculado à oficial, após backup privado e comparação
da fonte anterior com a fonte ensaiada (idênticas). A fonte final é idêntica
à testada e à versionada; uma única substituição. Antes/depois da oficial:
18.393 chaves, zero alterações de valores. Sem construir/continuar, migração
ou preenchimento de teste na oficial. O pacote comprimido não foi substituído.

Fonte registrada no produtor, branch `codex/publicacao-r53`, commit `5441801`.
550 verificações do runtime direto passaram, incluindo falha do flush com
liberação do bloqueio; pacote de sete arquivos/25 abas/249 cartões conferido.
O patch `produtor-flush-proposta.patch` foi aplicado; a nomenclatura registra
a proposta preparada antes da autorização. Provas resumidas em
`salvamento-rapido-correcao.json` e `oficial-salvamento-corrigido.json`.

## Painel, revisão e limites finais

A navegação é pública de propósito. O teste automático usa duas identidades
simuladas distintas, verifica acesso, navegação, timeout usando o último clique
e rejeição de cliques após encerramento. Após esclarecer a necessidade,
a confirmação manual com outra pessoa real permanece complementar,
sem ser tratada como erro conhecido ou bloqueio das correções.

A revisão focal das alterações e a suíte Linux foram concluídas. O usuário
autorizou o merge da PR 67; seu estado e SHA de merge são registrados no GitHub.
Nenhum merge do produtor/PR 4 foi autorizado ou realizado nesta manutenção.

Os limites do mestre e o escopo do corpus R51/R52 continuam: este trabalho
confere os cartões R53, não uma revisão integral de todas as mudanças do livro.
Não há defeito funcional conhecido restante nos casos corrigidos acima.
As sequências finitas de estresse não garantem todo comportamento de rede possível.

Artefatos integrais, logs, fontes antes/depois e snapshots privados estão no
diretório ignorado `src/var/testes-r53-2026-10-20/`. Nenhum conteúdo da ficha
real, credencial, banco ou arquivo de aprovação foi versionado.
