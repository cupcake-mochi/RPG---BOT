# Continuar a Carteira viva

Atualizado em 26/10/2026. **Etapa 1 local concluída; OAuth nativo pendente.
Etapas 2–10 não iniciadas.**

## Situação

- Base remota consultada nesta etapa: `main de42447`. Esse commit documental
  já está na main; runtime registrado da publicação anterior continua `a7afebb`.
- PR 77: planejamento, branch `codex/plano-carteira-viva`, ainda aberta.
- Branch da etapa 1: `codex/carteira-viva-etapa-1`, sobre `3ac230b` do plano.
- Produção: último estado documentado é R57 de consulta, mecânica R53,
  runtime `a7afebb`. Nenhum deploy ou alteração de conta neste planejamento.
- Entrega atual: [contrato](CONTRATO.md), prova local e [relatório](ETAPA-1.md).
  39 testes novos; 67 no conjunto direcionado, todos aprovados.
- Próxima tarefa offline: **etapa 2** de [PLANO.md](PLANO.md), banco e cadastro.
- Modelo recomendado: **GPT-6.1 Sol, esforço Alto (`high`)**.
- Pendência da etapa 1: [OAuth/hospedagem](ACESSO-GOOGLE.md) e prova nativa.
  Rhodes Bot ainda sem Auth configurado; conta Discloud Gold, sem site listado.
- Matriz: [TESTES.md](TESTES.md). Nenhum comando novo testado no Discord.

## Prompt para a próxima tarefa

```text
Continue a Carteira viva das Guias do Ciclo. Responda em português informal.
Leia Closure/docs/carteira-viva/PLANO.md, TESTES.md, RETOMADA.md e o topo de
Closure/docs/FILA-ATUAL.txt. Confira AGENTS.md, remoto, PRs, branch e árvore
local antes de editar. Não presuma que este plano já está na main.

Leia também CONTRATO.md, ETAPA-1.md e ACESSO-GOOGLE.md. Execute a etapa 2:
banco definitivo separado, migrações, cadastro com múltiplos personagens,
permissões, retenção, exclusão, backup e restauração. A prova da etapa 1 é
local, com provedores simulados; não promovê-la como OAuth ou API pública.
Normalize conexões e use revisão de fonte para impedir troca concorrente
ou análise antiga gravada sobre arquivo novo. Não inicie serviço de produção.

A prova OAuth nativa continua pendente: falta configuração Google/Discord e
origem web. Avance no trabalho offline e preserve essa pendência para a
etapa 3. Não contrate hospedagem nem reutilize tokens da Arquivista. Nada
nesta fase exige mexer nas fichas reais.

Preserve cadastro livre dos próprios personagens, múltiplos personagens por
jogador, isolamento por servidor, cartão público básico, detalhes privados,
edição separada e atualização somente na consulta. Não herde leitura privada
dos cargos de idioma/lore. Não altere fichas oficiais ou de jogadores.
Não implemente edição de ficha nem use tokens da Arquivista nesta etapa.
Não faça chamadas pagas ao modelo nem merge/deploy sem autorização específica.

Use o navegador lateral para os ensaios autorizados, verificando conta e
servidor antes. Não peça senha/código no chat. Salve decisões, testes reais,
limites e o prompt da próxima etapa no Git. Ao finalizar, diga a próxima
tarefa e recomende GPT-6.1 Sol com esforço Alto para a etapa 3, destacando
quais configurações externas ainda faltam.
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
