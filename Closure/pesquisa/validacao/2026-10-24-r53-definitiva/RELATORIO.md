# R53 definitiva · validação da Closure · 24/10/2026

Entrega na PR 73, com merge autorizado pelo Mizuki e ZIP para atualização manual, sem deploy nesta sessão. Inventário completo, fontes e
procedimentos: [R53-DEFINITIVA.md](../../../docs/R53-DEFINITIVA.md).

## Resultado

| Verificação | Resultado |
|---|---|
| Contrato nativo | 18.393 chaves únicas; 10.173 `r53.*`; formato 12 |
| Comparação com manifesto do bot | Zero chaves ausentes ou extras |
| CSV da API e XLSX nativo | Todos os campos idênticos, incluindo metadados |
| Coluna C desatualizada | Não altera valores, resultado ou pendências de aprovação |
| Formato futuro 13 | Interrompe antes do corretor mecânico |
| Contexto de Closure e Kal'tsit | Recebe os guias vigentes; continuação e consulta em inglês cobertas |
| Pacote | 90/90 arquivos idênticos ao workspace; leitura/correção repetida do ZIP extraído; sem `.env` ou SQLite |
| Suíte final | 959 executados: 958 aprovados, 1 opcional pulado; 198,335 s |

Seis testes novos em `test_r53_definitiva.py`. As asserções anteriores que
ensinavam o rótulo Emitida ou a rotina diária foram atualizadas ao comportamento
aprovado da definitiva. As expectativas mecânicas e a recusa de formato
desconhecido foram preservadas.

A primeira execução completa teve uma falha textual: o teste em inglês ainda
exigia “Emitida”. Corrigido para exigir os identificadores portugueses atuais
“EMITIR” e “Não emitida”; a suíte completa foi executada novamente.

## Ensaio nativo e limites

A [cópia descartável](https://docs.google.com/spreadsheets/d/17INKENHpxKhYUYkBRiIh-G833Uz4DwztlMpAzYyNAQM/edit)
foi criada a partir da definitiva e mantida para revisão. Foi preenchida com
nome sintético, Caminho Bastião, Trilha Muro, nível 2 e atributos 3/2/2/1/1.
As entradas foram relidas após o preenchimento; preservaram-se fórmulas e menus.

O leitor e o corretor concluíram normalmente. Como o personagem é parcial,
o resultado identifica treinos faltantes e Famílias ainda sem as duas escolhas
Livres e três Fechadas: três problemas, seis pendências e onze limites.
Os zeros reportados são contagens de escolhas, não configurações divergentes. Não se alterou a regra para obter um resultado verde.

A exportação não contém salário, dinheiro ou emissão. W86 foi conferida
separadamente em leitura: ¥150.000; a carteira está não emitida. Não há
certificação financeira na análise. Não foi alterado o contrato ANALISE.

O CSV foi montado da leitura autenticada da API e processado pelo parser real;
o XLSX veio da exportação nativa. Não é uma prova do transporte gviz anônimo.
Não se executaram scripts onEdit pela API, ensaio do aplicativo Android,
mensagens no Discord ou chamadas pagas de modelo.

As bases definitiva/Original e fichas de jogadores não receberam escritas.
Não houve alteração de compartilhamento, force push ou deploy. O merge da PR 73
foi autorizado expressamente pelo Mizuki nesta continuação.
O arquivo `nativa.json` contém somente evidência agregada e hashes; snapshots
integrais permanecem fora do Git. `pacote.json` identifica o ZIP local não publicado.

## Prova adicional com o modelo público nível 2

Modelo vigente registrado em [MODELOS.md](../../../dados/ficha/MODELOS.md).
A [segunda cópia descartável](https://docs.google.com/spreadsheets/d/1irYpSOJpjrLMvEbRhrDabiJvFhv_bVZSUpYPMk0oafQ/edit)
veio diretamente da ficha pública indicada pelo Mizuki. Nível 2 confirmado,
Bastião/Muro, atributos 3/2/2/1/1. Exportações nativas foram enviadas ao método
real `Ficha.analisar_fonte` por um adaptador de anexo em memória, sem substituir
leitor, corretor ou geração de páginas. Nenhuma mensagem enviada ao Discord.

| Estado da cópia | Painel do bot |
|---|---|
| Fórmulas originais: Vida 23, Defesa 13 | Nenhum erro nessas duas contas |
| Vida e Defesa temporariamente em 999 | Vida: está 999, o certo é 23; Defesa: está 999, o certo é 13 |
| Fórmulas restauradas | API relida: Vida 23, Defesa 13 |
| Código extraído do ZIP | Mesmos resultados e quatro páginas em ambos os casos |

As 18.393 chaves foram lidas nas duas exportações, com 10.173 `r53.*`.
A ficha parcial mantém os três diagnósticos de escolhas faltantes; com os erros
injetados, são cinco. Isso não representa aprovação integral de personagem.
As regras de Famílias são 2/3 tanto na API quanto no XLSX. A verificação do
código confirmou que o “0” do diagnóstico conta escolhas ausentes.

`nivel2.json` contém resultados agregados e hashes dos anexos sintéticos;
nenhum XLSX ou snapshot de jogador foi versionado. O ZIP entregue chama-se
`closure-r53-nivel2-discloud.zip`; hash e tamanho estão em `pacote.json`.
Os guias e respostas públicas em PT/EN usam o novo link e rejeitam o antigo
no teste de regressão. A referência nativa ao modelo público foi registrada no Git.

## Ambiente e reprodução

O sandbox sem permissão de rede travou até um exemplo mínimo de
`asyncio.run(asyncio.to_thread(lambda: 42))` no encerramento do executor.
Com a permissão adicional, o exemplo terminou imediatamente; a suíte foi
executada nesse modo, mantendo os testes offline e os provedores simulados.
Mensagens de custos/indisponibilidade nos testes são cenários simulados,
não chamadas faturadas.

```sh
# Closure/
.venv/bin/python ferramentas/empacotar.py
# Closure/src/
../.venv/bin/python -m unittest discover -s testes
```

Recomendação: GPT-6.1 com esforço alto para integração e médio para a revisão
final de texto. A publicação do bot permanece uma etapa separada desta entrega.
