# Revisão do mestre, ajuda e atalhos · 21/10/2026

## Estado entregue

Publicado na Discloud pelo navegador do aplicativo, conforme pedido do usuário.
Runtime **162b39c6a5849cd1707aaaec7af5daf3cf5fcb3e**, online em cinco servidores
às **10:28:26 de Brasília**. Branch `codex/guias-de-comandos`,
[PR 68](https://github.com/cupcake-mochi/RPG---BOT/pull/68) aberta em rascunho,
sem merge. Commits posteriores de documentação não exigem outro deploy.

O usuário pediu uma segunda revisão da orientação do mestre, abreviações
para comandos curtos/longos, uma página própria na ajuda, configuração por
servidor quando viável e conhecimento desses comandos pelas duas guias.

## O que mudou

- **Revisar uma ficha como mestre**: oito páginas por `GC:guia mestre`,
  `GC:gm` ou `/ficha mestre`. Cruza criação, progressão, habilidades,
  orçamento, entidades, ajustes, conteúdo próprio, equipamento, salários e
  decisão humana com a análise. O Resumo do painel aponta para esse roteiro.
- **Ajuda**: duas páginas, Comandos disponíveis e Abreviações. `/ajuda` é
  privado, `GC:ajuda` é público. `GC:ab`, `GC:atalhos` ou
  `GC:ajuda abreviações` abre diretamente os atalhos. Os nomes completos e
  os aliases anteriores continuam funcionando.
- **Padrões curtos**: a, g, f, l, c, p, s; gc/gp/gf/gm abrem criação,
  planilha, análise e mestre; ab abre a lista de abreviações. Argumentos e
  anexos seguem para o destino original, sem análise ou chamada extra.
- **Por servidor**: `/atalho definir`, `/atalho remover` e `/atalho listar`,
  com Gerenciar servidor verificado na execução. Até 20 nomes próprios,
  destinos públicos fechados, sem macros, URLs fixas, encadeamento,
  dados pessoais ou comandos administrativos; nomes existentes protegidos.
- **Conhecimento operacional**: `prompt.py` acrescenta os comandos e os
  atalhos válidos do servidor atual às duas guias. Não é memória pessoal,
  não muda cards/núcleo e não permite que a fala execute um comando ou
  conceda autorização. Contexto verificado sem chamada paga.

São doze assuntos e 55 páginas de guia; as duas páginas da ajuda ficam à
parte. O assunto mestre deixou de ser alias de custom, mas aponta para o
cadastro exato quando necessário. Cálculos, veredictos e cores da análise
não mudaram. MESTRE VIU e Emitida continuam sem conceder aprovação.

Conteúdo, limites e instruções completas em
[GUIAS-DE-USO.md](../../../docs/GUIAS-DE-USO.md). O roteiro reaproveita as
fontes R53 e a extensão salarial conferidas na rodada anterior; não há
novos números mecânicos ou edição da ficha oficial.

## Testes

| Verificação | Resultado |
|---|---|
| Suíte completa local | **912 executados, 911 aprovados e um online opcional pulado**, 300,707 s |
| CI do mesmo runtime | [Aprovada](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/39608001610) |
| ZIP final extraído | **107 aprovados**: 9 atalhos + 9 guias + 21 painel + 68 Discord |
| Migração em cópia do banco real | somente a tabela de atalhos acrescentada, todas as tabelas antigas preservadas e integridade ok |

Regressões cobrem abreviação e argumentos, XLSX/link, isolamento entre
servidores, persistência após reabrir banco, migração de banco anterior,
limite de 20, atualização no limite, remoção, colisões, destinos privados,
encadeamento, caracteres inválidos, permissão, páginas da ajuda e tamanho
máximo com 20 atalhos. O contexto das duas personagens inclui só os
atalhos válidos do servidor atual e rejeita destino livre adulterado.

Durante a implementação, o primeiro ensaio detectou uma tentativa de tratar
o estado de conversa como dicionário. Corrigido para acrescentar os atalhos
ao dicionário retornado por para_a_ponte, antes da publicação. As fixtures
Discord receberam um ID numérico de servidor, como no SDK real, e as
expectativas de comandos refletem `/atalho` e `/ficha mestre`. Não foram
alteradas expectativas mecânicas nem ocultados erros para obter verde.

### Ensaio real no Discord

Servidor autorizado **1357866906341736488**, tópico Testes
**1561410667108368575**, usando a sessão do usuário no aplicativo.

1. [GC:gm](https://discord.com/channels/1357866906341736488/1561410667108368575/1562457619615195250):
   oito páginas percorridas, chegada à decisão final e limites explícitos.
2. [GC:ab](https://discord.com/channels/1357866906341736488/1561410667108368575/1562457788356231311):
   lista padrão, nomes antigos e alternância para Comandos disponíveis.
3. `/atalho definir nome:qa_mestre destino:Guia de revisão do mestre`:
   confirmação privada, resposta ID 1562458636649758770. O menu real
   apresentou os 20 destinos permitidos. O cliente precisou recarregar a
   lista e receber entrada pelo teclado para mostrar as sugestões novas;
   não houve mudança de código ou falha de autorização por causa disso.
4. [GC:qa_mestre](https://discord.com/channels/1357866906341736488/1561410667108368575/1562458711874863286):
   abriu o roteiro correto. Nova ajuda exibiu esse nome na seção do servidor.
5. `/atalho remover nome:qa_mestre`: confirmação privada ID
   1562458898223595561. Ajuda reaberta e backup final confirmaram remoção.
6. [GC:f com XLSX sintético](https://discord.com/channels/1357866906341736488/1561410667108368575/1562459148560629831):
   R53-01 Coruja simples, zero erros/pendências/ajustes, conferência parcial
   preservada e campo Revisão do mestre visível. Foi reutilizado o arquivo
   nativo de ensaio de 19/10; nenhuma cópia Google foi criada ou modificada.
7. `/ficha mestre`: resposta privada ID 1562459605123080293, primeiro texto,
   oito páginas e aviso “Só você pode ver esta mensagem” conferidos.

Não houve chamada paga ao modelo. A orientação operacional foi testada por
montagem dos pedidos das duas guias; não se fez uma bateria de respostas
naturais. Negação a outro papel/servidor, limites e persistência entre
reinícios foram cobertos offline; não se simulou outra pessoa na sessão real.

## Publicação e integridade

- App Guias do Ciclo `1773761486581`, recursos 700 MB/0,68 vCPU preservados.
- Backup anterior privado de Downloads com sufixo **(17)**, baixado pela
  Discloud do aplicativo, íntegro e permissão local 0600.
- ZIP final **80 arquivos**, todos iguais aos fontes e aos bytes instalados.
  SHA-256 `f1e716c20e9dab3d05116a132813a4fac6b15832462e45ac712f7698766195e5`.
- Nove fontes de runtime mudaram; sem `.env`, bancos ou campanha no ZIP.
- Backup posterior **(18)**: ambiente, campanha, núcleo e banco legado
  idênticos. Banco do bot íntegro e todas as linhas das tabelas existentes
  iguais; somente `atalhos_servidor` foi acrescentada, vazia após o ensaio.
- Sem erros de aplicação no trecho observado. Avisos PyNaCl/davey já
  existentes não se referem a esses comandos.
- Personalidades, memória pessoal, mídia, contas e aprovações preservadas.

Auditoria sem conteúdo real em [pacote.json](pacote.json). Capturas e logs
locais ignorados em `Closure/src/var/mestre-atalhos-2026-10-21/`.

A [política pública existente](https://gist.github.com/cupcake-mochi/7439b3894cf8ad935601e0f521e16c08)
foi atualizada e relida igual à local, com a data de 21/10. Explica o
armazenamento dos nomes/destinos por servidor, sua exibição, contexto das
guias e remoção administrativa. URL, termos e permissões não mudaram.

## Retomada e limites

Esta manutenção está publicada e conferida. Verificar remoto e PR 68 antes
de continuar. Runtime 162b39c; não repetir deploy por documentação. Rever
atalhos.py, guia_mestre.py, GUIAS-DE-USO.md e este relatório se mudar um
destino ou a interface. Abrir GC:ab, GC:gm e /ficha mestre para um novo ensaio
somente quando houver mudança relevante.

Não há comando de aprovação automática ou avaliação narrativa por modelo.
Histórico, aprendizado, autorização real, requisitos livres, alvos e Alma
continuam com o mestre. A comparação do corpus geral R51/R52 com R53 é uma
fila independente. Revisão/merge da PR e observação com jogador novo seguem
separados; não foram certificados por esta rodada.
