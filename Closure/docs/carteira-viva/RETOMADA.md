# Continuar a Carteira viva

Atualizado em 26/10/2026. Etapas 1–3 implementadas; piloto básico de conexão
real concluído. **Backend da etapa 4 implementado e testado offline; ensaio
nativo de leitura completa em preparação. Etapas 5–10 ainda pendentes.**
Nenhuma Carteira publicada na Discloud.

## Situação

- Main remota conferida: `de42447`. Produção registrada: `a7afebb`, consulta
  R57 e mecânica R53. Não confundir essas versões com as branches da Carteira.
- PRs dependentes 77 (plano), 78 (etapa 1), 79 (etapa 2) e 80 (etapa 3).
  Sem merge. PR 80 em `c44e9e5`, CI verde, base da etapa atual.
- Etapa 4: branch `codex/carteira-viva-etapa-4`, nova PR dependente da 80.
  Leitura autenticada completa, cache, fila justa, coalescência, cotas locais,
  cancelamento, revisão de fonte/autorização, motor e campanha confiável.
  Resultado privado com proveniência. [Entrega e limites](ETAPA-4.md).
- 49 testes novos passaram. Suíte local iniciada antes da última correção:
  1.176/1.175 aprovados/1 opcional, zero falhas; a correção final passou na
  bateria dos 49. Conferir CI do SHA final para o conjunto de 1.177 testes.
- API interna pronta para atualização, análise e abertura do resultado salvo.
  Não há novos comandos/botões da etapa 4 instalados no Discord. Etapa 5 vai
  consumir essa API, sempre com ator obtido da interação e resposta privada.
- Publicação exige hospedagem HTTPS persistente e sincronização confiável do
  cadastro de campanha entre bot/serviço. Não basta copiar uma vez o arquivo e
  prometer aprovações atualizadas. Piloto usa cadastro fictício local explícito.
- Credenciais de aplicativo privadas fora do Git em
  `~/.local/share/guias-ciclo/carteira-piloto`. Não exibir valores nem copiar
  para o disco externo que ignora permissões. Não usar tokens da Arquivista.
- Google próprio Externo/Testando, duas contas autorizadas, drive.file e chave
  Picker restrita; Discord usa as Guias oficiais por escolha do usuário. Não
  criar outro bot ou redefinir segredo/token novamente sem necessidade.
- [Piloto anterior](NATIVO-ETAPA-3.md): cadastro, reinício, refresh, revogação e
  reconexão passaram. Sua cópia foi à lixeira e grant revogado. A etapa 4
  precisa de outra cópia descartável e consentimento próprio para a prova real.
- Próxima implementação: **etapa 5, galeria e cartões**, com bateria nativa de
  leitura/análise pendente. Modelo: **GPT-6.1 Sol · Alto (`high`)**; pode manter.

## Prompt para continuar

```text
Continue a Carteira viva das Guias do Ciclo, em português informal.
Leia o topo de Closure/docs/FILA-ATUAL.txt e carteira-viva/RETOMADA.md, PLANO.md,
CONTRATO.md, BANCO.md, SERVICO.md, TESTES.md e ETAPA-4.md. Confira AGENTS,
remoto, branch, árvore e PRs. PRs 77–80 são dependentes e não devem ser mescladas.
Confira também a PR da branch codex/carteira-viva-etapa-4 e seu CI final.

O backend da etapa 4 lê ANALISE completa autenticada e reutiliza de_linhas,
ficha_corretor.conferir, regras e aprovações exatas por servidor. Há cache 60 s,
fila justa/coalescência/cotas/cancelamento e rotas internas privadas. Análise
explícita relê; abrir resultado salvo revalida membro/cargos, fonte, autorização,
leitura, campanha e motor. Não aceitar cadastro como aprovação ou prosa como
bônus. Manter limites/ausências do produtor e decisões humanas.

Conclua a prova nativa de leitura completa se ainda pendente, em nova cópia
DESCARTÁVEL. A etapa 3 só provou A1:D32. Registre paridade com exportação
calculada, consumo de chamadas, limpeza e revogação. Não anunciar simulação
como prova Google/Discord. Credenciais de app já existem fora do Git; não
exibir valores. Leia NATIVO-ETAPA-3.md e qualquer registro nativo da etapa 4.

Implemente a etapa 5 sobre a etapa 4: galeria /personagens [@jogador], múltiplos
personagens, cartão básico por servidor, detalhes/análise privados, botões que
conferem permissões atuais, atualização sob demanda e personalização prevista
no plano. Texto PT/EN claro, nomes curtos, sem menções inesperadas; não expor
link privado/snapshot no cartão público. Integrar a ponte opcional sem iniciar
um bot duplicado de produção. Preservar personalidade, mídia e análise existente.

Não há origem HTTPS pública nem publicação da Carteira. Antes de deploy,
resolver hospedagem e fonte confiável de campanha entre processos/hosts; não
compartilhar SQLite pela rede. Não publicar serviço incompleto no app de bot.
O usuário permite testes no painel e atualizações necessárias, mas não contratar
upgrade, editar oficiais/jogadores, fazer chamadas pagas ou presumir merge das
PRs dependentes. Usar cópias descartáveis e manter só abas necessárias abertas.

Teste, revise clareza e permissões, documente, faça commit/push e nova PR
rascunho dependente. Separe Git, simulação, prova nativa e Discloud. Salve prompt
para etapa 6 e recomende modelo/esforço conforme o plano; não criar outro chat.
```

## Entrega ao fim de cada etapa

1. Feito e conferido, com simulação e prova nativa separadas.
2. Pendências reais de código, produtor/mestre e configuração externa.
3. Branch, SHA e PR; diferença entre Git e produção.
4. Próxima tarefa, modelo/esforço e prompt de retomada atualizado.

Sala de treino permanece na fila futura. Não ampliar o escopo para resolver
lacunas do produtor, automatizar decisões do mestre ou editar livremente células.
