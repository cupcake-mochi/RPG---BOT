# Guias do Ciclo

**Produção: consulta R68/v0.379 · mecânica R53, com a Técnica Máxima da R67.**

Kal’tsit e Closure conversam, explicam regras do **Ciclo Maldito** e conferem
partes da ficha. O projeto atual fica em [`Closure/`](Closure/). A Arquivista
é um [bot independente](https://github.com/cupcake-mochi/Arquivista-do-Ciclo),
responsável pelo arquivo de aparências.

## Comece por aqui

- **Usar o bot:** `/ajuda` lista comandos; `/guia` explica cada recurso.
- **Criar uma ficha:** `GC:guia criar`, da cópia até a emissão na Carteira.
- **Modelo público nível 2:** [ficha para copiar](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit?usp=drivesdk).
- **Conhecer a planilha:** `GC:guia planilha`, com abas e configurações.
- **Analisar:** `GC:f LINK_DA_FICHA` ou XLSX anexado à mensagem de `GC:f`.
- **Revisar como mestre:** `GC:gm`, junto do painel e do livro da mesa.

Português e inglês são configuráveis por servidor. A lore original de Arknights
e a lore Nova Terra são opções separadas do idioma. A análise da ficha é parcial:
**zero erros não equivale à aprovação do mestre**.

## Estado e documentação

A consulta **R68/v0.379** foi publicada com 576 trechos.
[Registro da preparação](Closure/docs/CONSULTA-R68-2026-11-19.md)
Desde 19/11, a análise da ficha confere a Técnica Máxima pela **R67** nas fichas
formato 13, a mesma conta das oficiais. O resto da mecânica segue a revisão 53.
[O que mudou](Closure/docs/ANALISE-MAXIMA-R67-2026-11-19.md)
O Acerto da Expansão das invocações agora é aceito como resultado, então as fichas
formato 13 chegam às contas e os cartões R53 são conferidos.
[O que mudou](Closure/docs/EXP-ACERTO-R53-2026-11-19.md)

A publicação está no runtime `921e7c8`, online desde 20h51 de 19/11/2026
(Brasília). [Registro da publicação](Closure/docs/PUBLICACAO-EXP-ACERTO-R53-2026-11-19.md)

A **Carteira viva** está em desenvolvimento separado, nos PRs
[#77–#84](https://github.com/cupcake-mochi/RPG---BOT/pull/84), sem publicação.
Etapas 1–6 implementadas, etapa 7 parcial e etapas 8–10 pendentes.
A criação automática de fichas continua bloqueada. O próximo marco é revisar
o tempo da preparação e testar eventos reais de abertura, edição, missão,
gasto e correção de data em uma cópia descartável nova. O estado atualizado
fica na [retomada da Carteira viva](https://github.com/cupcake-mochi/RPG---BOT/blob/codex/carteira-viva-etapa-7/Closure/docs/carteira-viva/RETOMADA.md).

| Preciso de… | Onde encontrar |
|---|---|
| Visão do projeto e organização | [Closure/README.md](Closure/README.md) |
| Instalação e execução | [Closure/src/LEIA-ME.md](Closure/src/LEIA-ME.md) |
| Guias oferecidos no Discord | [Guias de uso](Closure/docs/GUIAS-DE-USO.md) |
| Última revisão e entrega | [Publicação R63](Closure/docs/PUBLICACAO-R63-2026-11-04.md) |
| Testes e limites R53 | [Fechamento R53](Closure/pesquisa/validacao/2026-10-21-r53/FECHAMENTO.md) |
| Contrato da ficha | [Contrato e cobertura](Closure/dados/ficha/INTEGRACAO-B47.md) |
| Estado para continuar o trabalho | [Fila atual](Closure/docs/FILA-ATUAL.txt) |

Credenciais, bancos e cadastros reais ficam fora do Git e dos pacotes públicos.
`Closure Legado/` e os [registros anteriores](README-HISTORICO.md) são referências
históricas; não substituem o estado atual.
