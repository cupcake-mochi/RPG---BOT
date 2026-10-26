# Continuar a Carteira viva

Atualizado em 26/10/2026. **Etapas 1 local e 2 concluídas; OAuth nativo pendente.
Etapas 3–10 não iniciadas.**

## Situação

- Base remota consultada nesta etapa: `main de42447`. Esse commit documental
  já está na main; runtime registrado da publicação anterior continua `a7afebb`.
- PR 77: planejamento, branch `codex/plano-carteira-viva`, ainda aberta.
- Branch da etapa 1: `codex/carteira-viva-etapa-1`, sobre `3ac230b` do plano.
- CI da PR 78 passou. Branch da etapa 2: `codex/carteira-viva-etapa-2`, sobre
  `daa5627`. PR 79 tem a 78 como dependência, sem merge. Conferir o CI do SHA atual.
- Produção: último estado documentado é R57 de consulta, mecânica R53,
  runtime `a7afebb`. Nenhum deploy ou alteração de conta neste planejamento.
- Entrega atual: [banco e recuperação](BANCO.md), [relatório da etapa 2](ETAPA-2.md).
  62 testes novos e os 39 anteriores: 101 direcionados aprovados.
  Suíte local no checkpoint 3b18330: 1.076/1.075/1 opcional; correção posterior
  de inicialização validada nos 101 e no CI do novo SHA (conferir resultado).
- Próxima tarefa: **etapa 3** de [PLANO.md](PLANO.md), conexão e serviço web.
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

Leia também CONTRATO.md, BANCO.md, ETAPA-2.md e ACESSO-GOOGLE.md. Execute a
etapa 3: serviço web e adaptadores OAuth Google/Discord, seleção pelo Picker,
reconexão e troca de arquivo. Reaproveite src/carteira_viva; não exponha os
métodos diretamente como endpoints ou aceite identidades fornecidas pelo
navegador. O laboratório da etapa 1 continua sendo uma simulação.

Use uma biblioteca OAuth mantida, estado/sessão e proteção contra repetição,
conta errada e retornos antigos. Grave somente autorização verificada e use
a versão da credencial para processar falhas de renovação. Ligue manutenção
local e confirme membros/cargos no Discord. Não compartilhe o SQLite por rede.

A prova OAuth nativa continua pendente: faltam configuração Google/Discord e
origem web. Google Auth ainda não está configurado no projeto Rhodes Bot e
nos outros dois projetos visíveis. A Discloud está em Gold e a documentação
exige Platinum para site. Avance localmente; prepare configuração concreta
antes de pedir a ação sensível necessária. Não contrate hospedagem nem
reutilize tokens da Arquivista. Use somente planilhas descartáveis no ensaio.

Preserve cadastro livre dos próprios personagens, múltiplos personagens por
jogador, isolamento por servidor, cartão público básico, detalhes privados,
edição separada e atualização somente na consulta. Não herde leitura privada
dos cargos de idioma/lore. Não altere fichas oficiais ou de jogadores.
Não implemente edição de ficha nem use tokens da Arquivista nesta etapa.
Não faça chamadas pagas ao modelo nem merge/deploy sem autorização específica.

Use o navegador lateral para os ensaios autorizados, verificando conta e
servidor antes. Não peça senha/código no chat. Salve decisões, testes reais,
limites e o prompt da próxima etapa no Git. Ao finalizar, diga a próxima
tarefa e recomende GPT-6.1 Sol com esforço Alto para a etapa 4, destacando
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
