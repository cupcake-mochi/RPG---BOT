# Continuar a Carteira viva

Atualizado em 26/10/2026. **Planejamento salvo; etapas 1–10 não iniciadas.**

## Situação

- Base remota consultada: `main a7afebb17fc4ff0297699de13861d56d81825612`.
- Registro da publicação anterior: `de424478a7a120ecb43bd0c79eb93774d446fae6`,
  preservado como commit anterior nesta branch; só documentação.
- Branch deste plano: `codex/plano-carteira-viva`.
- Produção: último estado documentado é R57 de consulta, mecânica R53,
  runtime `a7afebb`. Nenhum deploy ou alteração de conta neste planejamento.
- Próxima tarefa: **etapa 1** de [PLANO.md](PLANO.md).
- Modelo recomendado para começar: **GPT-6 Astra, esforço Alto (`high`)**.
  Não é obrigatório gastar esforço máximo nem trocar o modelo do bot.
- Depois da etapa 1: **GPT-6.1 Sol, Alto**, para banco e cadastro.
- Matriz futura: [TESTES.md](TESTES.md). Discord aberto é disponibilidade
  informada pelo usuário, não teste realizado nem sessão garantida.

## Prompt para a próxima tarefa

```text
Continue a Carteira viva das Guias do Ciclo. Responda em português informal.
Leia Closure/docs/carteira-viva/PLANO.md, TESTES.md, RETOMADA.md e o topo de
Closure/docs/FILA-ATUAL.txt. Confira AGENTS.md, remoto, PRs, branch e árvore
local antes de editar. Não presuma que este plano já está na main.

Execute a etapa 1: feche o contrato de dados/permissões e faça uma prova
pequena do acesso Google guiado pelo Discord, apenas em ambiente de teste
e com planilha descartável. Inclua identidade Discord, drive.file, Picker,
renovação segura, revogação e troca de arquivo. Identifique hospedagem HTTPS,
persistência, requisitos OAuth públicos e custo antes de contratar serviços.
Se depender de configuração externa, avance nos contratos e testes locais;
registre exatamente o que não foi validado nativamente.

Preserve cadastro livre dos próprios personagens, múltiplos personagens por
jogador, isolamento por servidor, cartão público básico, detalhes privados,
edição separada e atualização somente na consulta. Não herde leitura privada
dos cargos de idioma/lore. Não altere fichas oficiais ou de jogadores.
Não implemente edição de ficha nem use tokens da Arquivista nesta etapa.
Não faça chamadas pagas ao modelo nem merge/deploy sem autorização específica.

Use o navegador lateral para os ensaios autorizados, verificando conta e
servidor antes. Não peça senha/código no chat. Salve decisões, testes reais,
limites e o prompt da próxima etapa no Git. Ao finalizar, diga a próxima
tarefa e recomende GPT-6.1 Sol com esforço Alto para a etapa 2.
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
