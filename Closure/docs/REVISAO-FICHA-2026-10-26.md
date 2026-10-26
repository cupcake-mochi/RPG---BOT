# Revisão das fichas oficiais — 26/10/2026

## Resultado

As atualizações conferidas não exigem mudar o leitor nem as contas das Guias. O ajuste desta rodada esclarece o inventário nos guias de criação e de abas, em português e inglês, e inclui essas orientações no contexto de perguntas sobre inventário. Digitar um nome não concede benefícios nem dispensa autorização do mestre.

Branch do bot: `codex/guia-inventario-2026-10-26`, sobre main `07836153b017399a634586447f36b1664ae5d90a`. Não houve publicação, alteração de ficha, campanha ou chamada paga.

## Fontes e mudanças do produtor

A main de Ficha---RPG-JJK continua em `9d932c55c2be2e478399e5fadbad9330f36c292d`. Os PRs 18–21 foram integrados em `codex/otimizacao-android-r53`, atualmente `ca1292e485008eed7613f2ec6e62355afc485f84`. Foram comparados os fontes e os fechamentos de PENDENCIAS.md e r53/OFICIAIS.md; cabeçalhos históricos não substituem esses fechamentos.

- Otimização de onEdit, índices estáticos e leituras menores: instalada conforme o registro do produtor, pacote com remendos 1–32.
- Inventário: validações liberadas nas duas oficiais, também confirmado diretamente abaixo.
- Limpeza de 31 arquivos Apps Script sem uso em cada projeto: registrada pelo produtor, com versões de backup. Não foi executada nem revalidada por esta manutenção do bot.
- Remendo 33 de altura dos cartões: ainda não instalado nas oficiais.
- Experimentos de bordas e listas sem INDIRECT: não instalados. Não tratá-los como comportamento atual.
- O gerador ainda precisa incorporar a liberação das validações do inventário; pendência do produtor, sem edição nesta rodada.

Não houve mudança nos arquivos de contrato, esquema e conteúdos mecânicos comparados. JJK---Project permanece em `353d7728fa4f505f830dc6c0421929a0ab2668c1`.

## Conferência nativa, somente leitura

Modelos conferidos:

- [Era da Revolução](https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit)
- [Ciclo Maldito](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit)

Ambos têm 30 abas físicas e ANALISE com 18.394 linhas incluindo cabeçalho: 18.393 chaves únicas, formato 12. Foram lidas A1:D18394 em três intervalos por modelo. Nenhum effectiveValue retornou erro de cálculo nessa aba. Isso não é uma varredura das fórmulas de todas as abas nem um ensaio de onEdit.

A estrutura chave/referência/parte (colunas A/C/D, sem os valores B) coincide entre ambas e com o XLSX nativo preservado da cópia descartável do ensaio de 25/10. Impressão FNV-1a 64 da lista JSON compacta dessas triplas: `4ba0d93317a1c579`. Nenhuma chave, referência ou parte mudou nessa comparação. Valores de personagens não foram copiados para este relatório.

Validações em FICHA PESSOAL, confirmadas nas duas oficiais:

- D92:D97: seis menus de EQUIPÁVEIS GUARDADOS, com validação estrita.
- D98:D99: dois nomes livres, sem validação.
- D104:D109 e Z104:Z109: ITENS GUARDADOS com nomes livres, sem validação.

Os guias agora explicam esses campos e lembram de preencher quantidade e Volume. Cópias antigas não recebem automaticamente as alterações das oficiais.

## Validação do bot

51 testes direcionados passaram, em 29,519 s. Comando a partir de Closure/src:

```sh
PYTHONPATH=.:testes ../.venv/bin/python -m unittest testes.test_guias testes.test_r53_definitiva testes.test_ficha_ingles testes.test_servidor_publico
```

Cobertura: limites e navegação dos guias, contrato atual CSV/XLSX, apresentação em inglês, configuração por servidor e regressão de perguntas sobre inventário (cinco exemplos e um negativo). Não foi repetida a suíte completa local nesta alteração de orientação. A tentativa inicial usou um nome de módulo inexistente e não incluiu o caminho necessário a test_r53; o comando acima corrigiu a coleta, sem alterar expectativas para contornar falhas.

Pacote regenerado com ferramentas/empacotar.py: 90 arquivos, 1.804.337 bytes, SHA-256 `200eb75ea23038c593b9f30d0fc1e63aa5866225f0a22f2de54435e478212303`. Os 90 arquivos foram comparados byte a byte com os fontes previstos; sem .env, bancos ou cadastro de campanha. ZIP ignorado pelo Git e não enviado à hospedagem.

## Estado e retomada

Este ajuste parte da main R53 e não inclui a consulta R57. A consulta R57 está no PR 75, commit `c6d6b2e5ba0a214bbbd782da2f09c1e4904e0f06`, com CI verde na conferência desta rodada, ainda aberto. Mecânica permanece R53 em ambos.

Última publicação comprovada continua `20773855e098f8c8b738bba3614bb3318611db27`, em 25/10; a Discloud não foi inspecionada nem alterada nesta rodada. Antes de publicar, integrar os PRs desejados, resolver eventuais conflitos documentais preservando os dois registros e regenerar o pacote a partir do resultado. Não reutilizar este ZIP R53 para declarar consulta R57.

Permanecem os limites já documentados de revisão humana e de dados ausentes; esta conferência não equivale a uma nova bateria completa de preenchimento no Discord. O filtro Aptidão/Bênção e o orçamento Sem Técnica de Origem custom sem base do livro continuam fora deste escopo.
