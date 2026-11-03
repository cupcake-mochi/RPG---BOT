# Guias do Ciclo

**Última publicação: 30/10/2026 · consulta R60/v0.369 · mecânica R53.**

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

A consulta **R60/v0.369**, com 576 trechos, foi publicada no app existente da
Discloud em **30/10/2026, às 23:23 (Brasília)**, no runtime `229e539`.
As contas dos cartões da ficha continuam na **revisão 53**; formatos antigos
conservam sua compatibilidade documentada. A validação final registrou
990 testes: 989 aprovados e um online opcional pulado, além da conferência
dos 91 arquivos instalados. Veja o [registro da publicação](Closure/docs/PUBLICACAO-R60-2026-10-30.md).

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
| Última revisão e entrega | [Publicação R60 e clareza da análise](Closure/docs/PUBLICACAO-R60-2026-10-30.md) |
| Testes e limites R53 | [Fechamento R53](Closure/pesquisa/validacao/2026-10-21-r53/FECHAMENTO.md) |
| Contrato da ficha | [Contrato e cobertura](Closure/dados/ficha/INTEGRACAO-B47.md) |
| Estado para continuar o trabalho | [Fila atual](Closure/docs/FILA-ATUAL.txt) |
| Carteira viva em desenvolvimento | [Estado e retomada](Closure/docs/carteira-viva/RETOMADA.md) — etapas 1–6 implementadas, 7 parcial; não publicada |

Credenciais, bancos e cadastros reais ficam fora do Git e dos pacotes públicos.
`Closure Legado/` e os [registros anteriores](README-HISTORICO.md) são referências
históricas; não substituem o estado atual.
