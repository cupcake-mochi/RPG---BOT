Reprodução dos 28 casos avançados B47

Estes são arquivos técnicos de contrato para o consumidor, de uma aba ANALISE.
Não são fichas completas prontas para jogar nem recalculam o produtor nativo.
Não executar Apps Script, importar arquivos na oficial ou instalar aprovações
em servidor real a partir destes scripts. As aprovações geradas são somente
para a validação local sintética.

Pré-requisitos:
- Python e dependências do bot, incluindo testes; openpyxl apenas para leitura
  do endereço da célula de A02. Não instala nada automaticamente.
- Runtime Node com @oai/artifact-tool disponível/resolvido; no Codex, consultar
  load_workspace_dependencies. Não há cópia dessa dependência no repositório.
- Os XLSX sintéticos 01-base.xlsx e 02-custom-aprovada.xlsx da bateria nativa,
  guardados fora do Git em Closure/src/var/testes-b47/ ou na entrega do usuário.
- Pasta de saída nova e separada; não apontar para dados de produção.

A partir de Closure/, com a pasta de saída indicada pelo operador:

.venv/bin/python pesquisa/validacao/2026-10-18-b47-avancados/preparar.py --base src/var/testes-b47/01-base.xlsx --custom src/var/testes-b47/02-custom-aprovada.xlsx --saida /tmp/b47-repro
node pesquisa/validacao/2026-10-18-b47-avancados/exportar.mjs /tmp/b47-repro
.venv/bin/python pesquisa/validacao/2026-10-18-b47-avancados/invalidar_cache.py /tmp/b47-repro/02-sem-cache.xlsx
.venv/bin/python pesquisa/validacao/2026-10-18-b47-avancados/validar.py --saida /tmp/b47-repro

preparar.py monta entradas/resultados de ensaio e aprovações locais; exportar.mjs
autora os XLSX. invalidar_cache.py retira deliberadamente o cache de A02 para
provar que o leitor recusa uma fórmula sem cálculo salvo. validar.py compara
todos os campos normalizados do contrato, os diagnósticos e invariantes-alvo
independentes. Casos altos conservam 11 pendências de contexto intencionais.
As páginas esperadas de preparar.py refletem o código atual, não reproduzem a
cor global do runtime PR 64 usado nos ensaios reais anteriores à correção.

Nesta entrega, a versão portátil de preparar.py reproduziu as 28 definições e
Resultados originais sem diferenças. A validação portátil passou nos 28 XLSX
já ensaiados; a corrupção deliberada de A02 foi reexecutada. A exportação inteira
não foi repetida apenas para validar a mudança de caminhos dos scripts.

Evidências públicas: relatorio.txt, verificacao.json, casos-alvo.json e
validacao-local.json. Links, capturas do Discord e cadastro operacional ficam
fora do Git. O ZIP do bot não inclui nenhum destes dados de ensaio.

Regressões do patch, a partir de Closure/src/:
../.venv/bin/python -m unittest testes.test_ficha_painel testes.test_ficha_analise_v4
../.venv/bin/python -m unittest discover -s testes

O relatório documenta também as tentativas com timeout de mídia no disco
externo e a execução final com as mesmas dependências em disco local.
