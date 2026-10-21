# Guias do Ciclo 1.0.0 · versão estável

Entrega de 21/10/2026, revisada nas PRs 67 e 68. Kal’tsit e Closure são duas personagens do mesmo bot e compartilham esta versão de software. Versões dos cards, do lorebook e da edição das regras são identificadores separados.

A estabilidade aqui cobre a operação do bot: guias, atalhos, análise determinística parcial de fichas, mídia, clima, preferências de idioma e lore, permissões e persistência. Não significa que toda resposta de IA está correta nem que a ficha inteira foi aprovada pelo mestre.

## Evidências

- 944 testes: 943 aprovados e um online opcional pulado; CI do GitHub aprovada no código revisado.
- Bateria real com duas contas Discord, idiomas, permissões, guias e análise por link, contexto de lore e links públicos sem modelo.
- 88 arquivos instalados iguais ao ZIP; bancos/WAL, ambiente, campanha, dados anteriores e configurações preservados. Zero novas chamadas de modelo na bateria.
- Núcleo do pacote extraído conferido nos quatro perfis personagem/mundo; 57 páginas inglesas e controles conferidos.

O pacote 1.0.0 é o já publicado e auditado em 21/10 às 13:25:45 de Brasília. A formalização da versão e os ajustes de documentação não pedem novo deploy. O manifesto identifica esse pacote; compare seu SHA-256 ao baixar os arquivos da release. Não distribuir backups privados de produção.

## Limites e próximos trabalhos

Não foi certificada uma conversa nova com o modelo real nesta entrega. O ciclo Discord→Google com concessão de editor não foi repetido na Arquivista nesta rodada; o cálculo inglês passou em arquivo Google privado e o fluxo tem regressões simuladas.

No bot de fichas, continuam separados: comparação integral do corpus R51/R52 com o livro R53, ensaios nativos ampliados, campos/defeitos do produtor e revisão do mestre. Histórico de aprendizado, requisitos livres, autorizações, efeitos narrativos, distribuição entre alvos e interações de Alma não viram aprovação automática.

Correções continuam em versões posteriores. Relatório detalhado: ../pesquisa/validacao/2026-10-21-publico/RELATORIO.md. Estado do merge e versão publicada: PR 68 e releases do repositório no GitHub. Após o merge, main é a base das próximas alterações.
