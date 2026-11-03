# Guias do Ciclo · projeto atual

**Última publicação: 30/10/2026 · consulta R60/v0.369 · mecânica R53.**

Um bot, duas personagens: Kal’tsit atende das 9h às 21h e Closure das 21h às 9h,
no horário de Brasília. Elas conversam, consultam o livro do Ciclo Maldito,
recebem mídia e oferecem análise determinística de partes da ficha.

## Usar no Discord

| Quero… | Comando |
|---|---|
| Ver os comandos | `/ajuda` ou `GC:a` |
| Aprender a usar o bot | `/guia` ou `GC:g` |
| Montar a ficha até a emissão | `GC:guia criar` |
| Consultar abas e configurações | `GC:guia planilha` |
| Analisar a ficha | `GC:f LINK_DA_FICHA`, ou XLSX anexado a `GC:f` |
| Fazer a revisão do mestre | `GC:gm` |
| Abrir o livro normal ou escuro | `GC:l` |
| Consultar o clima | `GC:c Belo Horizonte` |
| Ver as abreviações | `GC:ab` |

Guias pela barra são privados; por `GC:`, aparecem no canal. A análise da ficha
é pública. Dados pessoais são consultados pelos comandos privados próprios.
[Orientações completas](docs/GUIAS-DE-USO.md).

Quem administra o servidor pode escolher português/inglês e a lore original
ou Nova Terra. Idioma e lore são independentes. `/cargo_admin` permite delegar
somente essas duas configurações. Arquivista e Guias têm configurações separadas.

## Regras, ficha e limites

A consulta publicada usa o texto **R60/v0.369**, com 576 trechos de referência.
A mecânica da análise continua R53. O último deploy registrado ocorreu em
**30/10/2026, às 23:23 (Brasília)**, runtime `229e539`, com 990 testes
(989 aprovados e um online opcional pulado) e 91/91 arquivos instalados
conferidos ([validação e publicação](docs/PUBLICACAO-R60-2026-10-30.md)).
As duas fichas oficiais, Era da Revolução e Ciclo Maldito, mostram a versão pública **1.0**, que não é a
revisão do livro nem a versão do bot ([modelos](dados/ficha/MODELOS.md)). Os cartões ANALISE 12 usam
o motor R53; formatos antigos mantêm sua referência histórica separada.
A análise não usa um modelo de linguagem para decidir contas ou aprovações.

O painel distingue erro, pendência e parte não conferida. A cor descreve a
página aberta; o rodapé mantém o resultado geral. **Zero erros não aprova a
ficha.** Histórico de aprendizado, autorizações reais e partes narrativas
continuam com o mestre. Aprovação de texto não cria benefício numérico.

- [Contrato e cobertura da ficha](dados/ficha/INTEGRACAO-B47.md)
- [Auditoria R53, testes e publicação](pesquisa/validacao/2026-10-21-r53/FECHAMENTO.md)
- [Idioma e lore por servidor](docs/RETOMADA-PUBLICO.md)
- [Entrega atual e clareza da análise](docs/PUBLICACAO-R60-2026-10-30.md)
- [Revisão final de clareza e apresentação](docs/REVISAO-FINAL-APRESENTACAO.md)
- [Carteira viva e galeria](docs/carteira-viva/RETOMADA.md) — em desenvolvimento,
  sem publicação: etapas 1–6 implementadas e 7 parcial. Inclui plano, testes e retomada.

## Executar e manter

A **Carteira viva** segue em desenvolvimento separado, nos PRs #77–#84:
etapas 1–6 implementadas, etapa 7 parcial e 8–10 pendentes. Ainda não está
publicada e a criação automática de fichas permanece bloqueada. O próximo
marco é revisar o tempo de preparação das cópias e provar os eventos reais
de abertura, edição, missão, gasto e correção de data em nova descartável.
Consulte a [retomada da branch de desenvolvimento](https://github.com/cupcake-mochi/RPG---BOT/blob/codex/carteira-viva-etapa-7/Closure/docs/carteira-viva/RETOMADA.md).

Siga [src/LEIA-ME.md](src/LEIA-ME.md) para dependências, ambiente e execução.
Não publique `.env`, bancos, chave mestra ou cadastro real de campanha.
O pacote de hospedagem é gerado por `ferramentas/empacotar.py`; ele preserva
os dados já existentes na hospedagem.

Antes de continuar o desenvolvimento, confira remoto e árvore local, leia a
[fila atual](docs/FILA-ATUAL.txt) e o fechamento mais recente. Não repita uma
publicação só por um commit documental. Pilotos pagos precisam de quantidade e
custo autorizados; a última autorização de 24 chamadas já foi consumida.

| Pasta | Conteúdo |
|---|---|
| `src/closure_bot/` | Código do bot e recursos da interface |
| `src/testes/` | Testes de regras, leitura, interface e integração |
| `dados/sistema/` | Corpus gerado e manifestos de origem |
| `dados/ficha/` | Contratos, cobertura e roteiros de validação |
| `dados/personagem/` | Cards e referências das duas personagens |
| `ferramentas/` | Sincronização, preparação e empacotamento |
| `docs/` | Documentação de uso, execução e decisões |
| `pesquisa/validacao/` | Evidências de testes e publicações |

A [Arquivista do Ciclo](https://github.com/cupcake-mochi/Arquivista-do-Ciclo)
tem repositório e execução próprios. O [README anterior](README-HISTORICO.md)
e `../Closure Legado/` ficam preservados como história do projeto.
