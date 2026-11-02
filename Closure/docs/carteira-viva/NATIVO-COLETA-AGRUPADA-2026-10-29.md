# Coleta agrupada no Google

29/10/2026 · PR 84 · **leitura agrupada da progressão validada no caminho observado; ensaio encerrado**.
Código testado `88d84a958ae547e484c6753093678a0c26e85dc9`, sem alterações locais em `Closure/src`.
Limpeza concluída às **09:19:43 de Brasília**, sem recursos ativos do piloto.

## Preparação

Cópia nova da oficial Ciclo feita pela própria interface do Sheets ("Fazer uma cópia"),
na conta Google que faz o consentimento, com nome **QA Carteira — coleta agrupada —
DESCARTÁVEL — 29-10-2026**. Ficou privada no Meu Drive dessa conta; a limpeza conferiu
pela API `ownedByMe`, `shared=false` e uma única permissão de dono. Nenhuma célula
editada, nenhuma oficial ou ficha de jogador alterada.

Uma primeira cópia, feita pelo conector numa conta diferente da que deu o consentimento,
não aparecia no Picker. Nada foi escolhido nessa tentativa; essa cópia foi para a
lixeira recuperável. Lição: **a cópia tem que ser da mesma conta do consentimento**.

Piloto loopback em `127.0.0.1:8876`, banco, chave e token de serviço novos fora do Git,
app já existente. Discord (`identify`) e Google (`drive.file`) reais; o aviso de app não
verificado foi aceito pela própria pessoa. Só a descartável foi escolhida no Picker e o
personagem fictício foi cadastrado na base isolada. O transporte bloqueava qualquer
escrita Drive/Sheets. O runner rodou desacoplado do terminal, com PID, batimento a cada
5 s e registro por chamada (sem URL, ID ou token).

## Resultado

Diagnóstico da origem, intenção preparada, domínio progressão, `agrupar=True`:

- Duas amostras completas **8/8 páginas**, cobertura compatível, oito páginas comparadas.
- **Zero páginas com mudança** em literais, fórmulas, resultados, notas e formatos numéricos.
- Versões iniciais iguais, nenhuma divergência durante a coleta nem antes/depois.
- Diário preparado idêntico antes/depois; quatro indicadores de liberação falsos.
- Fluxo concluído em **59,429 s** (inclui a conferência do modelo do servidor).

| Fase do diagnóstico | 28/10, individual (10df9c2) | 29/10, agrupada (88d84a9) |
|---|---|---|
| GET Sheets | 18 | **6** (2 sem faixa + 4 com quatro faixas) |
| GET Drive | 42 | 18 |
| GET membro Discord | 188 | 80 |
| Servidor/cargos/OAuth | 2/2/1 | 2/2/1 |
| Total HTTP200 | 253 | **109** |

Os números batem exatamente com o A/B fictício (253→109). Zero HTTP429, zero erro.
Cada GET de quatro faixas levou de 3,1 a 3,3 s; os de metadados 1,5 a 2,0 s.

Tempo de fluxo 59 s contra 164 s em 28/10 é uma observação de uma execução cada, com
fontes e momentos diferentes. Não é benchmark nem prova de causa.

### Hipóteses decididas

- **H1 confirmada:** com vários ranges o Google devolveu só as abas pedidas (o parser
  recusaria aba extra).
- **H2 confirmada:** ranges da mesma aba chegaram numa única entrada com vários blocos
  `data[]` (o parser recusaria aba repetida).
- **H3 confirmada:** GET de quatro faixas cabe com folga nos 15 s (máx. 3,3 s observado).

## Encerramento

- Runner parado normalmente; porta 8876 livre e nenhum runner ativo.
- Descartável na lixeira **recuperável**: PATCH HTTP200 seguido de GET HTTP200 com
  `trashed=true` e propriedade confirmada. Nada excluído em definitivo.
- Revogação Google HTTP200. Nova chamada do próprio diagnóstico recusada com `revogada`
  (OAuth HTTP400), cinco GETs Discord HTTP200 e **zero Drive/Sheets** após revogar.
  O consentimento anterior da mesma conta (sem arquivo escolhido) pertence ao mesmo
  grant do app e caiu junto.
- Zero personagens, fontes, cópias, financeiro, modelos, fluxos web, sessões, conexões
  ativas e segredos retidos. Integridade `ok` no banco e no ledger.

## O que esta prova não conclui

Prova real do dono, numa fonte privada descartável, **somente em progressão**. Não
confere se as contas da progressão estão certas, não é prova financeira nem de
estabilidade global, e não mede velocidade de forma comparável. Financeiro, auditoria,
propriedades Apps Script, demais domínios, concorrência, preservação, automações e
prova integral seguem pendentes. Criação bloqueada; quatro indicadores falsos. Sem modelo
pago, escopo novo, Gateway, merge, Discloud ou alteração do produtor/oficiais/jogadores.

## Próximo passo

Com H1–H3 confirmadas e o resumo idêntico, o agrupamento pode ser avaliado para o
financeiro **um fluxo de cada vez**: primeiro o diagnóstico financeiro (leitura, 25+
faixas), com as mesmas regressões e um ensaio nativo próprio, antes de tocar na
auditoria ou na escrita.
