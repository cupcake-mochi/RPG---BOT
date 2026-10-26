# Guias do Ciclo · projeto atual

**Versão estável 1.0.3 · publicada em 21/10/2026.**

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

A consulta desta atualização usa o texto **v0.367 (revisão 57)**, com 576 trechos
de referência. As revisões editoriais R54–R57 foram registradas pelo autor sem
mudança de regras. A mecânica da análise continua R53.
A consulta R57 foi publicada em 26/10/2026, com a orientação de inventário
([registro da publicação](docs/PUBLICACAO-R57-2026-10-26.md)).
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
- [Clareza de siglas e entrega atual](docs/CLAREZA-SIGLAS.md)
- [Revisão final de clareza e apresentação](docs/REVISAO-FINAL-APRESENTACAO.md)
- [Plano da Carteira viva e galeria](docs/carteira-viva/PLANO.md) — futuro;
  ainda não implementado. Inclui etapas, modelos recomendados, testes e retomada.

## Executar e manter

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
