# Publicação R57 e inventário — 26/10/2026

## O que está publicado

PRs [75](https://github.com/cupcake-mochi/RPG---BOT/pull/75) e [76](https://github.com/cupcake-mochi/RPG---BOT/pull/76) mesclados. Runtime publicado: **a7afebb17fc4ff0297699de13861d56d81825612**. Aplicativo existente Guias do Ciclo, ID 1773761486581, online às **09:03:19 (Brasília)** em seis servidores.

A consulta usa o livro R57/v0.367 (576 trechos); a mecânica determinística e o contrato ANALISE 12 permanecem R53. Guias de criação e de abas em português e inglês explicam os seis menus e dois nomes livres de equipáveis guardados, os itens guardados livres e a necessidade de quantidade, Volume e aprovação quando aplicável.

## Preparação e preservação

- Backup manual criado antes do envio. O usuário concluiu o download após o controle do navegador não o salvar. Arquivo validado e preservado em armazenamento privado: 267 arquivos, 3.301.287 bytes, SHA-256 `99a137998b92bd18dce06fb5d044d14f14b5f566a24fabe1c456886be8c5c723`.
- Backup contém .env, src/var/bot.sqlite3, closure_lab.db e src/var/ficha-campanhas.json. ZIP íntegro; ambiente e campanha do backup coincidem com a auditoria anterior.
- Núcleo e pacote regenerados na árvore integrada. ZIP de publicação: 90 arquivos, 1.814.160 bytes, SHA-256 `4b2cd94a24be4a11bb79e16d508165d3dc56410c1f49cf1fd99892c03774fddf`.
- Pacote sem .env, bancos ou cadastros de campanha. Enviado por Commit; a reconstrução do próprio Commit concluiu normalmente, sem Rebuild separado.
- Após publicação: **90/90 arquivos instalados idênticos ao ZIP**. Ambiente efetivo (27 chaves), .env, campanha e conteúdo de todas as tabelas dos dois bancos iguais antes/depois. Ambos passaram na verificação de integridade. Comparação realizada antes dos comandos de teste, que naturalmente podem gerar registros novos.
- Evidências completas e backup ficam fora do Git, no armazenamento privado da manutenção. Nenhuma credencial, valor de ambiente ou cadastro real foi incluído neste registro.

## Validação

A CI do conjunto integrado passou antes do envio (run 40318919285). A suíte local, iniciada antes da publicação e concluída durante as verificações posteriores, executou **976 testes em 528,422 s: 975 aprovados, zero falhas e um online opcional pulado**. Comando em Closure/src:

```sh
../.venv/bin/python -m unittest discover -s testes
```

Auditoria com núcleo presente:

```sh
.venv/bin/python ferramentas/auditar_consulta_livro.py --saida /caminho/privado/fontes-r57.json
```

Resultado: **497/497 títulos recuperados**. É auditoria de fontes, sem modelo; não mede respostas geradas. Nenhuma chamada paga foi feita.

Discord, no tópico Testes autorizado:

- `GC:ping`: R57/v0.367, 576 trechos, resposta em 43 ms.
- `GC:guia criar`: página 1 com os dois modelos oficiais e explicação da versão pública 1.0; seletor abriu a página 11 com as seis linhas de menu e duas livres, quantidade/Volume e ressalva de aprovação.
- `GC:guia planilha`: seletor abriu a página 7, FICHA PESSOAL, com a mesma orientação de inventário.

Os logs confirmam o horário de online. Os avisos de dependências de voz ausentes (PyNaCl/davey) já correspondem ao escopo sem voz; não houve falha de inicialização. Não foi repetida a bateria nativa de Ritual/fichas desta publicação anterior, nem ensaiada conversa paga. Oficiais e fichas de jogadores não foram editadas.

## Pendências reais

Esta rodada encerra a publicação de consulta R57 e orientação de inventário. Continuam os limites humanos e de dados ausentes já registrados. O filtro Aptidão/Bênção e o +1 do orçamento Sem Técnica de Origem custom sem base no livro seguem fora do escopo; trabalhar somente se solicitado. O gerador da ficha ainda precisa incorporar as validações livres do inventário conforme a fila do produtor; não foi alterado aqui.

Este registro é um commit somente documental posterior ao runtime acima. **Não republicar por causa dele.** Antes de outra manutenção, ler o topo de FILA-ATUAL.txt, conferir remoto/local/produção e preservar os dados existentes.
