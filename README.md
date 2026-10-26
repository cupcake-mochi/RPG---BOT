# Guias do Ciclo

**Versão estável 1.0.3 · publicada em 21/10/2026.**

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

Nesta atualização, a consulta usa o texto **v0.367 (revisão 57)**. As contas dos
cartões da ficha continuam na **revisão 53**; formatos antigos conservam sua
compatibilidade documentada. A consulta R57 e a orientação de inventário foram
publicadas em 26/10/2026 ([registro](Closure/docs/PUBLICACAO-R57-2026-10-26.md)). As versões estáveis e seus pacotes
ficam em [Releases](https://github.com/cupcake-mochi/RPG---BOT/releases).

| Preciso de… | Onde encontrar |
|---|---|
| Visão do projeto e organização | [Closure/README.md](Closure/README.md) |
| Instalação e execução | [Closure/src/LEIA-ME.md](Closure/src/LEIA-ME.md) |
| Guias oferecidos no Discord | [Guias de uso](Closure/docs/GUIAS-DE-USO.md) |
| Última revisão e entrega | [Clareza de termos](Closure/docs/CLAREZA-SIGLAS.md) |
| Testes e limites R53 | [Fechamento R53](Closure/pesquisa/validacao/2026-10-21-r53/FECHAMENTO.md) |
| Contrato da ficha | [Contrato e cobertura](Closure/dados/ficha/INTEGRACAO-B47.md) |
| Estado para continuar o trabalho | [Fila atual](Closure/docs/FILA-ATUAL.txt) |
| Próximo projeto: cadastro e galeria | [Plano da Carteira viva](Closure/docs/carteira-viva/PLANO.md) — ainda não implementado |

Credenciais, bancos e cadastros reais ficam fora do Git e dos pacotes públicos.
`Closure Legado/` e os [registros anteriores](README-HISTORICO.md) são referências
históricas; não substituem o estado atual.
