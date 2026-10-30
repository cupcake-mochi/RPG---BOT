# Equivalência não renova a retenção

30/10/2026 · PR84 · correção offline; não publicada.

## Defeito reproduzido e correção

`registrar_equivalencia_copia` usava `_guardar_copia`, que também atualiza o horário
de transição da operação. Uma prova de versão equivalente, apesar de não mudar
recibo, estado ou autorização, passava a renovar o prazo de 30 dias usado por
`Cadastro.limpar` para remover cópias identificadas. A retenção era adiada também
num backup feito depois dessa observação técnica.
Datas históricas já renovadas não são recalculadas: não há uma data de identificação
original separada para reconstruí-las com segurança. O conserto impede novas
renovações técnicas, sem inventar uma migração a partir de `criado`.

Quatro testes novos foram executados antes da correção: três falharam, mostrando
mudança de horário e uma cópia vencida que não era removida após restauração.
O cenário de prova inválida já recusava corretamente.

A equivalência agora altera apenas o conteúdo cifrado, dentro da mesma transação
e com as mesmas conferências de identidade, referência, modifiedTime, conteúdo
e limite. Mantém `criado` e `atualizado`. Não há mudança de schema, contrato, hash
de contexto, versões originais ou política das intenções ainda pendentes.

## Verificação

117 testes direcionados aprovados em 67,846 s: cópia, financeiro e diagnóstico no
serviço; quatro casos novos. Cobrem origem e destino, duplicação da mesma prova,
reinício, vencimento na data original, liberação posterior da conexão órfã,
backup/restauração, prova inválida e operação enviada ainda pendente que não
pode desaparecer nem armar outro POST.

Comando em `Closure/src`:

    ../.venv/bin/python -m unittest testes.test_carteira_copias testes.test_carteira_financeiro_rest testes.test_carteira_diagnostico_servico

CI completo do código deste checkpoint ainda pendente. O CI anterior de 1.639
valida 583a95b e não deve ser atribuído a esta correção. Não repetir o ensaio nativo
financeiro encerrado: nenhum caminho de rede ou payload de escrita mudou.

## Outras conclusões desta rodada

[Propriedades e ativação](PROPRIEDADES-E-ATIVACAO-2026-10-30.md) delimita as cinco
chaves e propõe o aceite do produtor sem ampliar OAuth ou aceitar aprovação do
cliente. Não implementa ativação nem conclui as propriedades.

`preparada × versão configurada` e `validar_modelo` continuam estritos. A impressão
financeira cobre suas faixas; não prova que as demais configurações/catálogos do
modelo não mudaram. Usá-la para liberar uma revisão diferente do modelo seria uma
expansão indevida da garantia. Resolver exige referência adequada do modelo ou
nova escolha administrativa validada; não afrouxar essas guardas por conveniência.

Criação bloqueada, etapa 7 parcial, etapas 8–10 pendentes. Nenhum piloto/grant/recurso
novo, chamada paga, oficial/jogador/produtor alterado, scope, Gateway, merge/deploy.

Pacote ignorado regenerado e comparado com os fontes:90 arquivos, CRC íntegro,
sem Carteira/env/bancos/campanha; SHA256 `e7a3bf38fc72a229a4cbef47ce5afc59446f2cbbf7d766d094daa769155f7579`. Não publicado.
