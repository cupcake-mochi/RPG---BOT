# Continuar a Carteira viva

Atualizado em 26/10/2026. **Etapas 1–3 implementadas localmente;
prova OAuth/Picker nativa pendente. Etapas 4–10 ainda não implementadas.**

## Situação

- Main remota conferida: `de42447`. Produção registrada: `a7afebb`, consulta
  R57 e mecânica R53. Nenhuma Carteira publicada.
- PRs dependentes: 77 (plano), 78 (etapa 1), 79 (etapa 2). Sem merge.
- Etapa 3: branch `codex/carteira-viva-etapa-3`, sobre `b491409` da etapa 2.
  Serviço/fluxos e ponte opcional implementados, sem carregar no bot atual.
- Resultados e limites: [ETAPA-3.md](ETAPA-3.md). Execução: [SERVICO.md](SERVICO.md).
- Prova nativa aberta: [ACESSO-GOOGLE.md](ACESSO-GOOGLE.md). Configuração
  externa não alterada; demo no navegador usa somente provedores fictícios.
- Próxima implementação: **etapa 4**, leitura sob demanda e análise privada.
- Modelo recomendado: **GPT-6.1 Sol · Alto (`high`)**; pode continuar nele.

## Prompt para a próxima tarefa

```text
Continue a Carteira viva das Guias do Ciclo, em português informal.
Leia o topo de Closure/docs/FILA-ATUAL.txt e carteira-viva/PLANO.md, TESTES.md,
RETOMADA.md, ETAPA-3.md, SERVICO.md, BANCO.md e CONTRATO.md. Confira AGENTS,
remoto, branch, árvore e PRs antes de editar. PRs 77–79 são dependentes;
confira também a PR da branch codex/carteira-viva-etapa-3. Não dê merge.

Implemente a etapa 4 sobre o serviço existente: leitura autenticada de
ANALISE sob demanda e análise privada com os módulos determinísticos atuais.
Use a campanha/aprovações exatas do servidor; não transforme cadastro em
aprovação. A prova pequena A1:D32 da etapa 3 identifica formato, não confere
exportação completa. Preserve limites, fórmulas sem cache e inconsistências.

Implemente cache curto, deduplicação, fila justa, limite de resposta,
cancelamento e descarte de leitura antiga após troca de fonte/autorização.
Atualize só na consulta. Mostre origem/revisão/horário/campanha da análise;
isole cartão público de snapshot privado. Confirme membros e cargos atuais,
sem herdar permissão privada de cargos administrativos de idioma/lore.

OAuth/Picker nativos continuam pendentes de clientes/callbacks e configuração
Google/Discord. O demo é fictício. Avance offline e prepare ensaio real em
ambiente separado; não anuncie essa prova como feita. Use só cópias de teste,
nunca edite oficiais/jogadores nem reaproveite tokens da Arquivista. Não
contrate hospedagem, faça chamadas pagas ou publique integração incompleta.
O usuário permite testar pelo painel e atualizar Discloud quando necessário,
mas o app atual de bot não substitui a hospedagem web ainda inexistente.

Teste, documente, faça commit/push e PR dependente. Separe resultados locais,
nativos, Git e produção. Salve prompt e recomende GPT-6.1 Sol · Alto para a
etapa 5. Não inicie bot duplicado com token de produção.
```

## O que entregar ao fim de cada etapa

1. **Feito:** comportamento implementado e comparação com a etapa combinada.
2. **Conferido:** testes locais/nativos separados; contagem e evidência reais.
3. **Pendente:** defeitos, dependências externas e escolhas ainda necessárias.
4. **Salvo:** branch, SHA e PR; diferença entre Git, pacote e produção.
5. **Próxima tarefa:** etapa, objetivo, modelo/esforço e prompt curto de retomada.

Atualizar esta retomada em cada checkpoint. A recomendação de trocar modelo
é para o usuário configurar a próxima tarefa; não criar chat/subagente nem
mudar configurações automaticamente. Se a mesma configuração for suficiente,
dizer que pode continuar nela. Não parar no meio de uma etapa só para trocar.

## O que continua fora deste projeto

- Sala de treino: manter na fila futura.
- Resolver lacunas mecânicas do produtor ou automatizar decisões do mestre.
- Mudar personalidade, mídia, memória de conversa, clima ou modelo das guias.
- Editar livremente qualquer célula, publicar dados privados da ficha ou
  transformar cadastro em aprovação automática.
- Deploy/merge presumidos a partir de autorizações dadas para versões antigas.
