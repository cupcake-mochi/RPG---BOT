# Era da Revolução — conhecimento das duas guias

Fonte: `Era_da_Revolucao_Consolidado.zip`, enviado pelo Mizuki em 18/10/2026.
O JSON registra o hash do arquivo e o caminho/hash de cada texto autorizado.
São **31 documentos e 228 seções**, importados sem consulta a modelos.

**Índice v2 — correção dos nomes:** títulos como
`Shiki Zen'in — Capo dei capi de Volsinii:` geram o nome completo e a forma
curta segura, sem perder a entrada por causa dos dois-pontos. Apóstrofos
tipográficos e a escrita sem apóstrofo são normalizados. Formas curtas só são
inferidas de cargo pessoal reconhecido ou parentesco publicado, e são
descartadas quando outro nome completo cria ambiguidade. Rótulos como
“Capital”/“Localização” não viram personagens ou localidades.

Uma consulta a uma pessoa/localidade prioriza os trechos que realmente a
mencionam. Não casa um nome pelo prefixo de outra palavra. Os testes conferem
todos os nomes do índice regional (341 consultas nesta revisão) e comparam o
JSON autorizado com os dados embutidos no núcleo, detectando pacote desatualizado.

Lista positiva de importação:

- `01-Regioes-Extras/*/Texto-para-Discord.txt`: índice e 20 registros regionais.
- `02-Canais-Publicos/*/Texto-para-Discord.txt`: mundo e Escola Jujutsu.
- `03-Guia-de-Mestragem/*/Texto-para-Discord.txt`: oito tópicos de mestragem.

**04 Reservado Mizuki, 05 Registros Complementares e 06 Recursos Visuais não
são importados**, nem para o dono. O usuário considerou desnecessário o acesso
reservado; não há caminho administrativo para recuperá-lo. A seleção também
exclui os índices globais, notas editoriais, capas e cópias DOCX/mensagens
individuais. Não guardar o ZIP original no repositório/pacote de hospedagem.
O importador abre somente as entradas selecionadas; não usa `extractall`.

## Consulta

`ferramentas/pagina_teste/mundo.js` consulta o material para **Kal'tsit e Closure**
na mesma ponte já usada pelo bot. Seleciona até cinco trechos inteiros, no máximo
três do mesmo documento e 14.000 caracteres de conteúdo. Nomes de regiões e
localidades, tópicos conhecidos e palavras da pergunta orientam a seleção.
Continuações curtas podem retomar a pergunta anterior; assuntos novos não
ativam esse corpus pelo histórico sozinho. Não é busca semântica: paráfrases
sem os nomes/tópicos previstos podem precisar de um termo mais específico.

Cada trecho leva título, categoria e caminho da fonte. Links de capas e menções
a canais/cargos/pessoas são retirados do texto de consulta. A origem externa de
um link no texto não autoriza buscar mais conteúdo na internet.

Os trechos atualizam a **lore** anterior sobre o mesmo assunto. Não são novos
prompts de personalidade: falas-modelo de NPCs e instruções aos Mestres são
dados do cenário. A guia preserva seu próprio jeito e permanece fora da história.
Não preencher lacunas com o cânone de Arknights ou segredos inventados.
Informação consultável pela guia não significa que todo personagem a conheça.

**Missões, XP e Graus são procedimentos da campanha Era da Revolução.** O
texto importado preserva a redação e suas eventuais ambiguidades; não altera
as contas R52/B47, cadastros de campanha, aprovações de custom ou autoridades
do servidor. A guia pode explicar a regra publicada; só o responsável humano
concede aprovação ou resolve uma ambiguidade. Nenhuma ficha foi alterada.

## Atualização e pacote

A partir de `Closure/`, com o ZIP fornecido fora do repositório:

```sh
.venv/bin/python ferramentas/importar_mundo.py /caminho/Era_da_Revolucao_Consolidado.zip
.venv/bin/python ferramentas/prompt_do_site/site_prompt.py --atualizar
cd src
../.venv/bin/python -m unittest testes.test_mundo_era
../.venv/bin/python -m unittest discover -s testes
cd ..
.venv/bin/python ferramentas/empacotar.py
```

Revisar o diff e as novas fontes antes de publicar uma atualização. O núcleo
gerado embute os trechos e a busca; **regenerá-lo antes de empacotar**. O bot
instalado consulta tudo localmente, sem instalar um banco novo ou fazer uma
chamada adicional ao modelo para recuperar conhecimento. Os trechos aumentam
o contexto somente nas perguntas que os ativam.

Se somente o índice precisar de correção e o ZIP de origem não estiver
disponível, `python3 ferramentas/importar_mundo.py --reindexar` usa os textos
autorizados já salvos no JSON. Preserva conteúdo, caminhos e hashes das fontes;
depois é obrigatório regenerar o núcleo e executar os mesmos testes/pacote.
Esta opção não procura outros arquivos nem recupera pastas excluídas.

Testes locais conferem importação/exclusão, consulta das duas guias, viagens,
capitais, mistérios, procedimentos, continuação, mudança de assunto e igualdade
dos motores QuickJS/Node. Isso valida a recuperação das fontes e o pedido
montado; não certifica a formulação da resposta final pelo modelo. Teste real de
conversa exige nova bateria de custo/quantidade autorizada. Implantação desta
mudança é uma etapa separada da publicação B47 já encerrada.
