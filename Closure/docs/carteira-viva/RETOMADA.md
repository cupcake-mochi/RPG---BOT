# Continuar a Carteira viva

Atualizado em 28/10/2026. **Etapas 1–6 implementadas; etapa 7 parcial; 8–10 pendentes.**
Carteira não publicada. Não confundir configuração de modelo com criação funcional.

## Cópia com recuperação · 28/10 — etapa 7B, offline

Backend interno agora guarda o envio antes do POST e, após resposta perdida,
só reconcilia a cópia existente. Schema 8/ledger 2, vínculo ao iniciador/modelo/
concessão, verificação do destino privado, backup sem replay e exclusão tratados.
Sem endpoint, escrita Sheets, cadastro ou liberação de criação. 195 locais distintos aprovados, 29 novos
com HTTP fictício; prova nativa da cópia ainda pendente.

A etapa 7 foi subdividida para mostrar o avanço: **7A** modelo/leitura/retomada
implementados; **7B** cópia implementada offline; **7C** limpeza/inicialização REST
pendente; **7D** preservação/automações e prova completa pendentes. Etapas 8–10
continuam na fila. Próximo: diário de escrita/reconciliação financeira; não repetir
a leitura nativa anterior como se validasse cópia ou limpeza.
[Implementação, testes e limites](COPIAS-REST-2026-10-28.md). Sol Alto; revisão Médio.

## Prova real de leitura e retomada · 28/10 — parcial, não publicada

OAuth/Picker próprios das Guias em uma cópia privada descartável, com
consentimento do usuário. Dois domínios lidos em 247,349 s: financeiro 25 páginas,
11 achados de estado herdado; progressão oito páginas, zero achados. Após
reiniciar, reabriu ambos em 8,551 s com um GET Drive e zero GETs Sheets, sem
novo consentimento. Revogação real recusou retomada antes de ler células;
credencial/trabalho e personagem fictício removidos. Cópia na lixeira e piloto
encerrado. Nenhuma escrita de célula/GS, oficial ou jogador alterado.

Prova nativa do dono, não de revisor/admin/429/cancelamento no meio do domínio.
Quatro indicadores falsos e criação bloqueada. Próximo: cópia/diário de escrita
REST com reconciliação, demais domínios/propriedades/preservação/automações e
responsável; não liberar criação. Código 45c03c8/CI 1.457 anterior intactos;
fechamento apenas documental [skip ci], sem suíte/ZIP novos, merge/deploy.
[Resultados, contagens e limites](NATIVO-CONFERENCIA-2026-10-28.md).
Sol Alto para implementar; Médio para revisão.

## Menos consultas de permissão · 28/10 — parcial, não publicada

GET novo de membro/cargos a cada contexto. Quando banco comprova dono/cargo
explícito, não busca flags administrativas. Caso contrário, consulta permissões
completas como antes. Sem cache/TTL e sem remover pontos de revalidação.
Perfil simulado do dono: Discord 1.686→578 (-65,72%), Google 183/cotas e um
OAuth iguais. Administrador/dono do servidor por prerrogativa conserva três GETs.
Código `45c03c877a85b31303ebc3d9bcd44a71457c2d2f`: [CI completo 40762548326](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40762548326)
aprovado em 28/10 às **17:27:25 Brasília**: 1.457 executados/1.456 aprovados/um
opcional, zero falhas, 334,900 s. Lotes locais: 144 distintos, 18 novos aprovados.
Fechamento posterior só documental [skip ci], sem repetir suíte/publicação.
Criação bloqueada, sem merge/deploy ou escrita Google nesse checkpoint. A prova
nativa posterior do dono está registrada acima; caminhos alternativos seguem pendentes.
[Prova, medição e limites](OBSERVACAO-MEMBRO-2026-10-28.md). Sol Alto; revisão Médio.

## Fila e renovação da conferência · 28/10 — parcial, não publicada

Método interno Consultas.conferir_inicializacao compõe fila/cotas/OAuth reais do
serviço com o auditor e o estado cifrado. Fonte/cargos reconferidos; prazos maiores
só para essa operação. Retomada não relê financeiro concluído e observa a versão
Drive; cancelamento mantém domínios completos. Renovação compartilhada com análises,
CAS do refresh e proteção da manutenção em cancelamento, sem autorizar leitura.
Sem endpoint/comando, cópia ou escrita Google. Criação segue bloqueada.
Perfil simulado: 183 GETs Google/um POST OAuth e 1.686 GETs Discord. Próximo:
reduzir observações redundantes sem afrouxar acesso; depois medir cotas/prova
nativa. Restam também cópia/diário de escrita,
propriedades/demais domínios, preservação global/arte, automações e responsável.
Código `fd2c4d68b3a9eb5dff19ef416ba1c2b85f521cc1`: [CI completo 40752104027](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40752104027)
aprovado em 28/10 às **16:18:17 Brasília**: 1.439 executados/1.438 aprovados/um
opcional, zero falhas, 356,405 s. Lotes locais: 176 distintos aprovados, 29 novos.
Fechamento posterior só documental [skip ci], sem repetir suíte ou publicação.

[Implementação e limites](SERVICO-CONFERENCIA-2026-10-28.md). Sol Alto; revisão Médio.

## Recuperação de leituras · 28/10 — parcial, não publicada

Schema 7: estado cifrado por personagem para os dois domínios REST. Retoma entre
domínios completos; página interrompida é relida desde o começo. Prazo absoluto
30 minutos, limite 32 KiB, versão/contexto originais, contador transacional,
revogação/exclusão/rotação e backup tratados. Adaptador interno usa o worker real;
sem endpoint novo. Fonte já cadastrada: não cria cópia nem é diário de escrita.
Os quatro indicadores seguem falsos e a criação permanece bloqueada.
Faltam composição com fila/OAuth real, cópia/diário de escrita e demais domínios,
propriedades, arte/automações/responsável e prova integrada. Produtor PR31 intacto;
sem Google/Discord real, merge/deploy ou acesso novo nesta rodada.
Código `4f2122d1dfc44716adefd77392c5e238724d29f3`: [CI completo 40747877347](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40747877347)
aprovado em 28/10 às **15:49:39 Brasília**, 1.410 executados/1.409 aprovados/um
opcional, zero falhas, 293,160 s. 25 novos + 179 regressões locais aprovados.
Fechamento posterior só documental [skip ci], sem repetir suíte ou publicação.

[Contrato, fluxo e limites](RECUPERACAO-REST-2026-10-28.md). Sol Alto; revisão Médio.

## Contrato REST e conferência parcial · 28/10 — não publicada

Exportador público no produtor e JSON com hash fixo no consumidor. Conferência
financeiro/progressão em fluxo, cobertura obrigatória/ordem/fonte, custos lidos
das entradas da configuração. Progressão agora oito páginas/1.894 posições,
27 GETs, ou 28 com finalização; financeiro 153/154. Recibo cifrado histórico
vincula contrato/contexto/fonte/versão, sem grade/token e sem liberar criação.
Não é diário persistido de limpeza ou retomada de escrita; schema 6 preservado.
Corrigido no produtor o piso do XP: “—” abaixo, zero no inicial. Caso falhou
antes/passou depois; fonte e sondagem Google em descartável confirmaram. Nível 1
sem custo 1→2 continua pendente. Cópia na lixeira/aba fechada; não executou GS ou
serviço OAuth das Guias. 23 novos e 95 existentes passaram nos lotes locais.
Código consumidor 22b6512, CI 40743430137: 1.385 executados/1.384 aprovados/um
opcional, zero falhas, 181,422 s, 15:19:00 Brasília. Produtor d7adec7, CI
40743272303: 2.999 cenários/zero falhas e demais regressões, 15:18:33 Brasília.
Fechamento só documental [skip ci]; código e recibo continuam fora do deploy. Faltam
estado/recuperação, propriedades/demais domínios, autorização/fila/cópia, arte/
automações/responsável e prova nativa integral. Criação bloqueada, sem merge/deploy.
[Implementação, provas e retomada](CONFERENCIA-REST-2026-10-28.md). Sol Alto; revisão Médio.

## Coleta REST de financeiro e progressão · 28/10 — parcial

Novo `grade_inicializacao.py`: lê fórmulas/entradas, resultados, notas e formato
numérico em faixas fixas. Até 4.096 células/página, histórico até 5.000 linhas;
50 páginas/153 GETs no financeiro máximo, sete/24 na progressão. Versão inicial
conservada, contexto reconferido antes/depois de cada GET e após aguardar cota.
Callbacks confiáveis obrigatórios; composição no serviço e fila ainda pendentes.
Sem rota, escrita, Apps Script ou escopo novo. Criação permanece bloqueada.
24 novos/95 direcionados locais aprovados. Código b5934be, CI 40735993584:
1.362 executados/1.361 aprovados/um opcional, zero falhas, 245,141 s. Job
concluído em 28/10 às 14:32:42 Brasília. CI anterior 40735653225 substituído
após revisão dos prazos; fechamento só documental [skip ci]. Pacote
90 arquivos regenerado/conferido sem Carteira/env/banco/campanha, não publicado.
Ainda falta traduzir contrato/estado do produtor: propriedades de Apps Script
não são fornecidas por Sheets REST. Leitura de célula não equivale a conferência
GS nem a inicialização pronta. Sem Google/Discord autenticado ou merge/deploy.
[Fluxo, limites e continuação](COLETA-REST-2026-10-28.md). Sol Alto; revisão Médio.

## Observação de versão entre lotes · 28/10 — ainda parcial

Produtor PR31, código `2427024`: plano e lotes de quatro perfis sem gravar
células nem propriedades; 631 perfis/158 páginas, 16 cenários locais passaram.
CI produtor 40731673476 aprovado no código 2427024: 2.952 cenários de
inicialização/zero falhas, pacote nove arquivos/sintaxe 277 Python/253 JS-GS e
demais regressões. Job concluído em 28/10 às 14:07:25 Brasília; duplicado
40731660220 cancelado.
Amostra produzida pelas funções GS reais em VM foi aceita no Python; isso prova
saída do protocolo, não chamada remota/autenticação/cálculo Google.

Consumidor agora tem código: `leitura_temporal.py`, guarda em memória de versão
Drive/contexto antes/depois do plano e de cada página, mais finalização. Sem
token armazenado, página duplicada, rebaseline silencioso ou liberação de
criação. Erro temporário/cancelamento não avança; diferença de versão/acesso
invalida a rodada. Cálculos/snapshot continuam sem certificado. Novo método
versao_arquivo corrige versão vazia antes aceita na leitura existente;
reprodução na base 73c2914 passou antes/recusou depois, sem flexibilizar teste.

Consumidor código `1c15ee5`: 24 novos + 47 de leitura/modelos locais, 71 aprovados.
CI completo 40731678916 aprovado: 1.338 executados/1.337 aprovados/um opcional,
zero falhas, 272,214 s; job concluído em 28/10 às 14:06:23 Brasília.
Pacote regenerado: 90 arquivos/CRC/fontes iguais, sem env/bancos/campanha ou
Carteira, não publicado. Contrato, fluxo e limites em
[LEITURA-VERSIONADA-2026-10-28.md](LEITURA-VERSIONADA-2026-10-28.md).

Dependência explícita: transporte de execução do produtor não foi entregue.
`scripts.run` exige projeto/implantação/escopos próprios, não basta presumir
`drive.file`. Próximo adaptador deve preservar permissão por arquivo escolhido
(REST/backend ou rota específica avaliada separadamente). Sem novo consentimento,
publicação Apps Script ou uso de credenciais da Arquivista. Criação continua
bloqueada, sem rota para contornar. Restam execução/código/isolamento, cálculos/
arte/preservação global/quota nativa, automações/treinos/notas e responsável.
Sem Google/Discord real, modelo pago ou merge/deploy; runtime publicado não foi
alterado. Sol Alto para adaptar/integrar; revisão Médio.

## Leitura conjunta e ordem de Classe 0 · 28/10 — ainda parcial

Produtor PR31, código `4987b50`; main `ef361cc` e bot main `de42447` reconferidas.
Mapa direto de 599 perfis: 10.178 operações, 17.316 guardas declaradas, zero
escritas cruzadas e 83 interseções escrita/guarda. Não enumera toda leitura
indireta/dinâmica. Encontrado defeito na ordem dos cinco Classe 0: cada guarda
lê campos da linha seguinte. Com todos preenchidos, ordem antiga falha; nova
ordem de baixo para cima passa e mantém os recibos/guardas dos cartões.

Sequência v2, chave nova: não adota v1/fases avulsas nem apaga diários. Guarda
uma projeção das proteções financeiras sem o nível que a progressão muda;
a guarda antiga completa continua igual. Cadeia dos registros dos filhos e
contador são fechados no avanço da fase. Ao terminar, compara a cadeia e salva
um retrato compacto; a leitura posterior detecta alteração de registro sem
reconstruir todos os elos por página. Checksum não é autenticação de cliente.

`conferencia.gs` lê um perfil por chamada, confere registros, guardas e todos
os pós-estados/fábrica, sem chamar Aplicar ou limpar células/propriedades.
Só grava seu checkpoint. O nível inicial é conferido pela progressão; o
financeiro conserva as outras proteções capturadas. Imagens atuais e
consistência temporal ainda não são certificadas. Todos os indicadores de
liberação continuam falsos mesmo ao terminar a leitura.

101 financeiros, 67 da sequência e 43 novos da leitura aprovados localmente.
Maiores registros: coordenador 1.773 bytes, checkpoint 354 bytes. CI completo [40722524965](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40722524965)
aprovado no código `4987b50a947208502934561ac0351670fcdaebc7`, 28/10 às
13:10:58 Brasília: **2.936 cenários/zero falhas**. Pacote nove arquivos,
sintaxe 277 Python/250 JS-GS e demais regressões passaram. Duplicado
40722509904 cancelado; fechamento só documental [skip ci], sem nova suíte/publicação.
Os 599 slots de protocolo usam perfis pequenos controlados, não uma aplicação integrada de todos os perfis reais numa ficha.
Há testes reais em VM de financeiro/progressão e dos cinco Classe 0 preenchidos.
Não executa fórmulas nem mede latência Google. Relatório produtor
`r53/inicializacao/CONFERENCIA-2026-10-28.md`, mapa JSON e gerador reproduzível.

Próximo: consistência temporal/imagens atuais/arte, preservação global, orçamento
nativo, automações/treinos/notas, novo responsável e integração/prova drive.file.
Não publicar ou liberar criação pelo CI. Sem Google/Discord, oficial/jogador,
novo acesso, modelo pago, merge/deploy/Gateway. Consumidor só docs, runtime
`26ec106`/CI histórico 40496955301, sem suíte/ZIP novo. Sol Alto; revisão Médio.

## Sequência fixa dos perfis · 28/10 — ainda parcial

Produtor [PR31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`408a31a`; main produtor `ef361cc` e bot main `de42447` reconferidas.
Coordenador de 599 perfis de escrita e duas inspeções de imagens, mais até 32
recuperações capturadas no início. Ordem fixa do produtor, sem plano do navegador.
Fotos antes de identidade/entidades; financeiro antes da progressão; memórias
depois dos cartões/MONTAGENS; recursos atuais no fim. Não recomeça pelo financeiro
após mudar o nível: a guarda antiga continua recusando essa mudança.

Uma chamada prepara a assinatura de um filho OU aplica esse filho. Assinatura
ativa fica durável antes do filho; cursor avança só após a conclusão. A mesma
trava cobre coordenador, filho e avanço, sem aquisição recursiva. Miolos dos
executores financeiro/imagens foram separados dos wrappers sem mudar contratos,
assinaturas, guardas ou orçamento inicial anterior. Cache volátil invalidado.
Não adota fases avulsas, apaga diários ou elimina recuperações novas por heurística.

67 cenários novos locais aprovados, maior coordenador 1.553 bytes com 32
recuperações. CI completo [40716269167](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40716269167)
aprovado no código `408a31abbdb8824bbe39f2e2997e80e30c65914e`, 28/10 às
12:32:28 Brasília: 2.893 cenários/zero falhas. Pacote nove arquivos, sintaxe
277 Python/247 JS-GS e demais regressões passaram. Duplicado 40716253746
cancelado; fechamento só documental [skip ci], sem nova suíte/publicação. Manifesto instancia os 599 perfis reais;
601 slots do protocolo exercitados com perfis pequenos controlados. Outro teste
usa financeiro/progressão reais (nível 29 → 10/base 3.700), retoma sem repetir
financeiro e confirma sua recusa antiga. Não é inicialização integrada dos 599
perfis sobre a mesma ficha, nem medição nativa da quota/latência.

Ao terminar: `fasesPercorridas=true`, `conferenciaConjuntaConcluida=false`,
`criacaoDisponivel=false`. Falta revalidar o conjunto atual, resolver consistência
entre páginas/arte, orçamento global, automações/treinos/notas, novo responsável
e integração/prova drive.file. Não expor a cópia entre fases nem executar editor.
Relatório produtor `r53/inicializacao/SEQUENCIA-2026-10-28.md`.

Sem Google/Discord, oficial/jogador, modelo pago, merge/deploy/Gateway ou acesso
novo. Consumidor só docs; runtime `26ec106`, CI histórico 40496955301, sem suíte
ou ZIP novo. Sol Alto para integrar; revisão Médio.

## Inventário de imagens · 28/10 — arte ainda parcial

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31),
código `b35436e`. Main produtor `ef361cc` e bot main `de42447` reconferidas.
Inventário de todas as células físicas, inclusive abas ocultas, com rodadas
fixas antes/depois, assinatura de estrutura e checkpoint por página. Conta
fotos, decoração marcada/ausente, outras imagens, fórmulas IMAGE, sobreposições
e desenhos sem alterar células. Até quatro páginas/chamada e 4.096 células/página;
excesso dos limites recusa sem truncar. Não persiste conteúdo, URL ou alt text.

79 cenários novos locais passaram; maior checkpoint 1.109 bytes. CI completo
[40713143485](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40713143485)
aprovado no código `b35436e`, 28/10 às 12:13:10 Brasília: 2.826 cenários/zero
falhas, pacote nove arquivos/sintaxe 277 Python/245 JS-GS e demais regressões.
Duplicado 40713131601 cancelado; fechamento só documental [skip ci]. Ensaio real em planilha técnica nova,
privada e descartável confirmou CellImage individual/em bloco/espelho, URL
igual dentro de cada execução e entre duas execuções próximas. Limpeza fictícia
preservou a fórmula e atualizou o espelho; releitura A1:H12 confirmou. Arquivo
na lixeira e abas do ensaio fechadas, sem mudar compartilhamento. Não executou
o inventário completo, a limpeza do protótipo ou a inicialização numa ficha.

Não é snapshot consistente: edição numa página já lida pode escapar daquela
rodada; uma nova rodada pode encontrá-la. Marcador não certifica pixels/origem.
`consistenciaTemporalVerificada`, `autenticidadeDecoracaoVerificada` e
`criacaoDisponivel` continuam falsos. Arte ainda parcial, criação bloqueada.
A identificação temporária da foto ainda recusa divergência; não apagar diário.

Relatório produtor `r53/inicializacao/INVENTARIO-IMAGENS-2026-10-28.md` e sonda
manual `probe_imagens.gs`, fora do pacote. Restam consistência/arte e conferência
conjunta, orquestração/quota total, automações/treinos/notas, responsável e prova
nativa da criação com drive.file. Sem oficial/jogador, merge/deploy/Gateway,
modelo pago ou escopo amplo novo. Consumidor só docs; runtime segue `26ec106`,
CI histórico 40496955301, sem suíte/ZIP novo. Sol Alto; revisão Médio.

## Fotos nas caixas conhecidas · 28/10 — arte parcial

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`350c56d`. Main produtor `ef361cc` e bot `de42447` reconferidas. Um perfil
restaura 13 caixas de foto + espelho pessoal e notas; dez decorações de fábrica
ficam fora dos alvos. Mesclas/validações protegidas, tipo interno `foto` no
executor sem mudar operações/assinaturas anteriores, diário/recibo e limites
existentes. Não remover imagens por posição ou só por alt text.

Reconhece texto/URL digitado, fórmula IMAGE e CellImage identificável por hash
de URL temporária/alt text, sem guardar URL/imagem/notas no retorno ou diário.
Não faz fetch. Identificação instável/ilegível provoca recusa. Se uma foto
pendente perder a identificação, não apagar o diário: revisar/descartar a cópia
incompleta e usar outra nova. Mesmo com alt igual, URLs diferentes não são
tratadas como a mesma imagem; isso não certifica os pixels.

Sobreposição ou desenho em qualquer aba bloqueia, sem remove. **Imagens em
outras células não são auditadas/limpas**; a pendência aparece no retorno,
com criação indisponível. Decoração custom ainda exige decisão de preservação.
Não chamar arte de concluída. O suporte nativo/estabilidade da URL precisa
ser caracterizado no Apps Script em cópia descartável, sem ampliar escopo.

137 cenários locais de fotos e 44 de quota passaram. Simulação ampliada para
572 perfis + reserva 100 KB: 412.570 bytes, pico 412.936. Coleção completa
**2.747/zero falhas**, confirmada no [CI 40706336130](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40706336130),
código `350c56d`, aprovado em 28/10 às 11:32:49 Brasília. Pacote nove arquivos,
sintaxe 277 Python/242 JS-GS e demais regressões passaram; duplicado
40706329406 cancelado. Fechamento só documental `[skip ci]`. A VM não executa
serviços nem recalcula fórmulas.
Nenhuma planilha lida/editada, cópia, Apps Script, OAuth/escopo novo ou modelo
pago nesta rodada. Consulta só à documentação pública Google. Relatório
produtor `r53/inicializacao/FOTOS-2026-10-28.md`.

Próximo: ensaio CellImage/URL e auditoria de imagens fora das âncoras; depois
orquestração/orçamento total/conferência global, memórias, automações/treinos/
notas e novo responsável, integração drive.file e prova nativa completa.
Fotos devem preceder identidade textual e entidades. Criação bloqueada,
protótipos fora do pacote/bot; consumidor só docs, runtime `26ec106` e CI
histórico 40496955301. Sem suíte/ZIP novo, merge/deploy ou Gateway.
GPT-6.1 Sol / Alto para implementar; Médio para revisão focal (AGENTS.md).
Entradas abaixo históricas.

## Histórico: dados das entidades · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`baf652d5dbd9db8ba5a0ca64ca04bfbebfb6738c`. Main produtor `ef361cc` e bot
`de42447` reconferidas. Acrescentados 73 perfis: seis por entidade e o conjunto,
1.165 entradas de identificação, atributos/treinos, recursos, Famílias,
inventário e talentos/Expansão. Matrizes de âncoras, valores/notas/fórmulas de
fábrica, contas e catálogos preservados. Menus conhecidos são mantidos e sua
rigidez real entra na assinatura. Mesclas exigem geometria exata. Recibos/quota
anteriores reutilizados; adaptador de validações extraído sem mudar descritores.
Executor e contratos anteriores intactos. Criação continua bloqueada.

305 cenários locais de entidades e 44 de recibos/quota passaram. 73 recibos
reais: 36.719 bytes, maior diário pendente 3.165. Simulação ampliada para 571
nomes reais de perfis com operações sintéticas + reserva 100 KB: 412.036 bytes,
pico 412.402. Coleção completa **2.610**, zero falhas, confirmada no
[CI 40701063975](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40701063975), aprovado no código `baf652d`
em 28/10 às 10:58:19 Brasília. Pacote nove arquivos/sintaxe 277 Python/238 JS-GS
e demais regressões passaram. Duplicado 40701053252 cancelado; fechamento
posterior só documental `[skip ci]`. Não é orçamento comprovado de todas as
fases futuras.

Leitura das duas oficiais: conjunto e primeira/última entidade, por arquivo
195 entradas/validações e 284 guardas. Valores/fórmulas e critérios/referências
dos menus coincidem. 105 menus estritos preservados; SPARKLINE pt_BR reconhecida
pela fórmula inteira, sem alterar conta. Duas notas contextuais por arquivo
são geradas a partir dos tipos; a rotina limpa herdadas e a fase de automações
precisa regenerá-las. Sem cópia, escrita nativa, Apps Script, OAuth ou acionador.
Relatório produtor `r53/inicializacao/ENTIDADES-2026-10-28.md`.

Próximo: arte. Fotos em célula/fórmula provocam recusa; só marcador/vazio aceito,
sem remoção automática, e imagens sobrepostas não foram tratadas. Depois,
orquestração/orçamento total/conferência combinada, automações/treinos/notas,
novo responsável, integração executável drive.file e prova nativa completa.
Protótipos fora do pacote/bot; consumidor só documentação, runtime `26ec106`
e CI histórico 40496955301. Sem suíte/ZIP novo, merge/deploy, Gateway, modelo
pago, escopo novo ou escrita em oficial/jogador. GPT-6.1 Sol / Alto para
implementação; Médio para revisão focal (AGENTS.md). Entradas abaixo históricas.

## Histórico: recibos e quota · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`af8e83f2869c01daa203fb5aa5c26c802c472850`. Main produtor `ef361cc` e bot
`de42447` reconferidas sem mudança. Cartões visíveis e MONTAGENS agora trocam
seus diários detalhados por recibos somente após a conferência final. Mesma
chave, sem exclusão; queda preserva diário ou recibo. Recibo terminal confere
operação/cópia/modelo/domínio, layout, guardas e resultados, sem nova limpeza.
Diários v1 desses perfis migram após conferência; demais formatos/assinaturas
preservados. Toda gravação de diário conta propriedades alheias e aplica teto
interno de 450.000 bytes, com 9.000 por valor e releitura de persistência.

44 cenários novos e seis focais de cartões passaram localmente. Coleção completa
**2.305**, zero falhas, confirmada no [CI 40697164990](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40697164990),
aprovado no código `af8e83f` em 28/10 às 10:34:44 Brasília. Pacote nove arquivos,
sintaxe 277 Python/234 JS-GS e demais regressões passaram. Duplicado 40697154581
cancelado; fechamento posterior só documental `[skip ci]`. As duas suítes de
249 cartões reais somam 125.247 bytes de recibos cada (maior 503).
Simulação conjunta: 498 recibos + reserva 100 KB = 372.263 bytes, pico 372.629.
As suítes reais também acumulam 249 recibos por domínio. Isso resolve a
retenção detalhada excessiva no protótipo, mas ainda não mede quota/latência
Google nem prova o orçamento de todas as etapas futuras. Relatório produtor:
`r53/inicializacao/RECIBOS-2026-10-28.md`.

Próximo: dados/recursos/equipamentos das entidades, arte, orquestração com
orçamento global e conferência combinada, automações/treinos/notas vivas,
responsável, integração drive.file e prova nativa completa. Criação bloqueada;
protótipos fora do pacote/bot. Nenhuma planilha foi editada nesta rodada.
Consumidor só documentação; runtime `26ec106`, CI histórico 40496955301.
Sem suíte/ZIP novo, merge/deploy, Gateway, modelo pago ou acesso novo.
GPT-6.1 Sol / Alto para implementação; Médio para revisão focal (AGENTS.md).
Entradas seguintes são históricas.

## Histórico: cartões visíveis · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`216e44c99c9aabc389f8f8811418dd538e6d5735`. Main produtor `ef361cc` e bot
`de42447` reconferidas sem mudança. Agora os 249 cartões têm protocolo para
3.863 entradas visíveis e 737 validações de função, além das versões guardadas
já tratadas. Restaura Classe/nome/COMO É e entradas/notas explícitas, protege
contas/rótulos/menus. Porta fechada recebe `—`, aberta zero ou caixa desmarcada;
regra antes do valor, com retomada separada. Amparo é relido e protegido por
fórmula; o destino usa a Classe de fábrica. Extras permitem Classe 0, mas o
modelo atual começa em 1. Não mudar defaults para satisfazer expectativas.

Executor ampliado só com operação de validação; contratos anteriores mantidos.
101 financeiros, 441 formação e sete focais passaram localmente. Coleção
completa no [CI 40694498546](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40694498546),
aprovado no código `216e44c` em 28/10 às 10:16:56 Brasília: **791 novos, 2.261
totais** (101/82/78/243/441/155/370/791), pacote nove arquivos e sintaxe
277 Python/233 JS-GS. Duplicado 40694490233 cancelado; fechamento produtor
`43c2f67` somente documental, `[skip ci]`. Leitura das duas
oficiais: nove contextos, 124 entradas, 210 guardas e 25 validações por arquivo,
sem diferença, escrita ou execução Apps Script. Relatório produtor
`r53/inicializacao/CARTOES-VISIVEIS-2026-10-28.md`.

**Quota conjunta é bloqueio real:** guardar todos os diários detalhados dos
cartões somou 1.396.929 bytes (maior 5.765), acima da capacidade conjunta de propriedades. Antes da integração, resolver
orçamento/compactação com recibos e proteção contra reinicialização; não apagar
diários para repetir. Também faltam dados/recursos/equipamentos das entidades,
arte, orquestração/conferência combinada, automações/treinos/notas vivas,
responsável, integração executável drive.file e prova nativa completa. Criação
segue bloqueada. Eventos/editor não podem rodar no meio da limpeza; MONTAGENS,
campos visíveis e memórias finais precisam ser conferidos juntos.

Consumidor só documentação; runtime `26ec106`, CI histórico 40496955301,
1.314 executados/1.313 aprovados/um opcional. Sem suíte/ZIP novo, merge, deploy,
Gateway, modelo pago, escopos novos ou escrita em oficial/jogador.
GPT-6 Astra / Alto para implementação integrada; revisão focal Médio.

## Histórico: MONTAGENS · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`5749b3af25f3b4082900a26685db655a696c4c26`. Main do produtor `ef361cc` e bot
`de42447` reconferidas sem mudanças. Implementado o protocolo das versões
salvas dos 249 cartões: 48.015 entradas, todas as Classes, um diário por cartão.
Defaults/notas de entrada restaurados; títulos, Classes máximas calculadas,
rótulos, instruções e demais domínios preservados. Validação/mescla inesperada,
fórmula desconhecida ou mudança concorrente causa recusa. Nenhuma alteração
no executor financeiro ou nos contratos anteriores.

370 cenários novos e 101 financeiros passaram localmente. Coleção completa
**1.470** confirmada no [CI 40690086385](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40690086385),
aprovado no código `5749b3a` em 28/10 às 09:45:06 Brasília. Sintaxe 277 Python/
228 JS-GS e demais verificações passaram. Duplicado 40690078538 cancelado.
Fechamento produtor `3cca7c5` apenas documental, `[skip ci]`. Os diários sintéticos dos 249 cartões somam 178.035 bytes;
isso não certifica a quota global da cópia. Leitura das duas oficiais: oito
modos em cada uma, 990 entradas e 310 guardas por arquivo, zero divergências,
sem escrita. Não criou cópia nem executou Apps Script/OAuth nesta rodada.
Relatório produtor: `r53/inicializacao/MONTAGENS-2026-10-28.md`.

**Os cartões visíveis ainda faltam.** Seus valores e validações dependem das
funções liberadas: não restaurar números/checkboxes por cima de listas `—`.
Também faltam dados/recursos das entidades, arte, orquestração/quota e conferência
global, automações/treinos/notas vivas, responsável, integração drive.file e
prova nativa completa. O leitor real comprovou que limpar MONTAGENS mantém o
cache persistente antigo; a limpeza do domínio de memórias precisa terminar
antes de religar o editor e conferir o conjunto. Criação continua bloqueada.

Consumidor só documentação; runtime `26ec106`, CI histórico 40496955301,
1.314 executados/1.313 aprovados/um opcional. Sem suíte ou ZIP novos, merge,
deploy, Gateway, modelo pago, escopos novos ou escrita em oficial/jogador.
Próxima implementação: GPT-6 Astra / Alto; revisão focal Médio.

## Histórico: CARTEIRA e memórias · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`8bb93355cb5d20d75ead1d8ba9a4b6d7c3ad88cc`. Main `ef361cc` e bot main
`de42447` reconferidas sem novidade; nenhum merge necessário.

Perfil CARTEIRA: O13, O27 e O30, conteúdo/notas de fábrica; preserva servidor,
espelhos, identidade, foto e emissão tratados separadamente. O27 é a técnica
declarada consumida por DADOS_AM; sentinela antigo D24 do teste foi corrigido
com prova da montagem completa. Nove contratos de formação anteriores iguais.

Protocolo separado de memórias: quatro caches e 249 marcadores de Classe em
11 grupos fixos de até 24 chaves; recuperações conhecidas por timestamp com
diário individual. Só document properties conhecidas, sem apagar células,
MONTAGENS, configurações, script/user properties ou diários alheios. Recusa
namespace/contrato desconhecido, preserva retomada/concorrência/limites e
invalida cache volátil do editor. A inspeção final deve ser repetida para
identificar recuperações novas; concluir um grupo não certifica o conjunto.

441 cenários de formação/CARTEIRA, 155 de memórias e 101 financeiros passaram
localmente; **1.100** (101/82/78/243/441/155) confirmados no
[CI 40686604745](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40686604745),
aprovado no código `8bb9335` em 28/10 às 09:19:25 Brasília, junto ao pacote
e demais regressões. Run duplicado de push 40686597423 cancelado. Fechamento
produtor `306b22ed008a18d04e40c8d437806cedc5003333` só documental, `[skip ci]`. Quinze entradas/guardas e três notas conferidas em cada
oficial, sem divergência, somente leitura. Sem nova cópia, projeção ou execução
Apps Script nesta rodada. Relatório do produtor:
`r53/inicializacao/CARTEIRA-MEMORIAS-2026-10-28.md`.

Próximo: entidades/cartões/MONTAGENS. Ainda faltam arte, orquestração e
conferência conjunta, ordem das memórias com automações/notas vivas/treinos,
novo responsável, integração executável drive.file e prova nativa completa.
**Criação incondicionalmente bloqueada.** Limpar caches não limpa os cartões
armazenados; não religar automações no meio da limpeza nem apagar diários
para forçar uma nova execução. Não confundir testes isolados com aceite final.

Runtime bot `26ec106`, CI histórico 40496955301 (1.314/1.313/um opcional), PR 84
base PR 83; consumidor só docs, sem suíte/ZIP novo. Protótipos fora do pacote.
Sem merge/deploy/Gateway/modelo pago/escopos novos ou escrita em oficial/jogador.
Próxima implementação GPT-6 Astra / Alto; revisão focal Médio.

## Checkout e Git

Continuação Linux de 27/10: usar explicitamente
`/home/mizuki/.codex/tmp/carteira-etapa7-linux` para o bot e
`/home/mizuki/.codex/tmp/ficha-carteira-inicializacao` para o produtor.
São clones no SSD, reconferidos com o remoto. O checkout antigo em
`/media/mizuki/HD Externo II/Closure Lab/RPG---BOT-b47` está no código da
etapa 6 com alterações locais de versões diferentes da etapa 7. Não foi
resetado, limpo ou sobrescrito. A comparação local identificou versões já
salvas no histórico remoto, sem mudança exclusiva nas 19 fontes alteradas;
isso não autoriza descartar a árvore. Os caminhos Windows abaixo são históricos.

- No Windows recuperado, usar `C:\Users\Mizuki\.codex\tmp\carteira-etapa7-recovery` neste Windows.
- Branch `codex/carteira-viva-etapa-7`, [PR 84 em rascunho](https://github.com/cupcake-mochi/RPG---BOT/pull/84),
  dependente de `codex/carteira-viva-etapa-6` / PR 83.
- Código atual salvo e enviado: `26ec1068131a8b71a9a04688bcf8676771fd736c`.
- CI desse código aprovado: [40496955301](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40496955301),
  1.314 executados, 1.313 aprovados, um opcional pulado, zero falhas; 278,076 s.
  O commit posterior só registra documentação e usa `[skip ci]` para não
  repetir a bateria extensa por esse registro. Conferir o código pelo SHA acima.
- Base exata `c2ca07ef2349ca8be46e2671a51da805bf03e69a`; CI documental 40424104893 verde.
- Pilha anterior 77–83 em rascunho, sem merge. Não mudar a base para main nem usar force-push.
- Main conferida `de424478a7a120ecb43bd0c79eb93774d446fae6`.
- O checkout anterior `E:\Closure Lab\RPG---BOT-b47` teve leituras travadas.
  Windows registrou corrupção NTFS no E: em diretórios fora deste repositório.
  Nenhum reparo executado, nem corrupção específica do código diagnosticada.
  Base e patches foram recuperados no C:. Não sobrescrever ou remover o original.

## O que já funciona no código

Continuação de 27/10: sondagem 2 lê até a última linha física dos três livros
financeiros (máximo de 5.000 linhas; recusa acima disso), entradas e notas de
missão, caixa de lançamento e caixas de correção. Só os sinais são guardados;
versão da sondagem entra na comparação da confirmação. Dez testes novos;
79 direcionados passaram e CI Linux completo aprovado no SHA indicado acima.
Registro do ensaio financeiro anterior (antes do avanço descrito no topo).
Leia também INICIALIZACAO-PRODUTOR.md: o primeiro domínio financeiro está
implementado separadamente na PR 31 do produtor, em rascunho, sem integração
no bot. 99 cenários novos e CI do produtor passaram. A regra confirmada pelo
usuário é preservar configurações extras da mesa e inicializar os dados
pessoais separadamente. Naquele código, o protótipo cobria só financeiro;
textos e nível/base receberam os protótipos descritos no topo. A inicialização
pessoal inteira, inventário, cartões/recuperações e automações seguem pendentes. Prévia nativa financeira em
cópia do Ciclo concluída em 115,013 s; a primeira aplicação atingiu 360,813 s
e retomou em 236,503 s. Código
corrigido `4f3555d`, documentação `352929a`, CI 40505846627 verde; no máximo quatro escritas/chamada,
orçamento e conferência sem duplicação. Na segunda cópia, aplicação 283,416 s
sem timeout; repetição 150,489 s, estado comparado igual. Duas cópias na lixeira,
abas de ensaio/servidor local encerrados. Zero acionadores para o executor;
automação salarial não está atestada. Custo ainda exige otimização e integração
assíncrona permitida. Ver ETAPA-7.md para o alcance das comparações. Não confundir com criação completa
ou OAuth das Guias.

Schema 6, modelos oficiais por padrão, seleção opcional Era/Ciclo/personalizado,
configuração por dono/Administrator e prévia/confirmar via OAuth/Picker existente.
Referência customizada cifrada, revisão local e versão Drive verificadas, perda de
cargo revalidada. Não cria conexão persistente do administrador nem personagem.
Trocar modelo não muda fichas cadastradas, campanha ou análise. Membros veem
somente a escolha genérica; nome/arquivo privado não aparecem na Carteira.

Comandos `/personagem modelos`, `/personagem modelo_configurar`,
`/character templates`, `/character set_template`. Interface PT/EN.
Cadastro existente segue por `/personagem cadastrar` ou `/character register`.
`criar_por_modelo` sempre retorna `modelo_bloqueado`, sem escrita Google ou
atalho de configuração. Nenhum parâmetro de criação está liberado.

## Bloqueio nativo da etapa 7

Três cópias descartáveis pelo Drive conectado (duas oficiais e uma sintética)
herdaram EXTRATO e estado salarial em DADOS_SALARIOS!L2, mesmo com N2 vazia.
No modelo sintético, CONFIGURAÇÃO!F46=5 mudou G46 de 2 para 5, mas o personagem
ficou no nível 2 e XP 0. XP permanece fórmula; regra de campanha não inicializa
nível do personagem. As três cópias estão na lixeira, sem mudança nas fontes.

Isso comprova o bloqueio, não inicialização funcional, Apps Script, acesso de
um novo jogador ou OAuth das Guias. Não presumir gatilhos após cópia/API.
O produtor precisa versionar a limpeza e inicialização idempotente, indicar
ativação manual indispensável e comprovar resultado nas três classes de modelo.
Não limpar células conhecidas de forma avulsa para declarar uma ficha nova limpa.

Produtores conferidos:
- Ficha---RPG-JJK main `57117fbe5c2361e6a09bfa00f037b4bcfaa8437f` (incorporada na PR 31).
- JJK---Project main `353d7728fa4f505f830dc6c0421929a0ab2668c1`.
- Texto R57; contrato mecânico R53/ANALISE 12. Revalidar antes de mudar o produtor.

A configuração privada existente das Guias está no SSD Linux:
`/home/mizuki/.local/share/guias-ciclo/carteira-piloto`. Ela foi localizada nesta continuação Linux; não foi aberta nova conexão
Google das Guias nem reutilizado grant antigo. No Windows anterior ela não estava disponível. Ela só é necessária para a prova pelo
OAuth próprio; não pedir segredos no chat, não recriar clientes/projetos,
não ampliar escopos e não usar credenciais da Arquivista.

## Provas e limites

Limpeza local pendente: a revisão automática bloqueou excluir os arquivos de
`C:\Users\Mizuki\AppData\Local\Temp\carteira-demo-xd9kcr1_`, inclusive
individualmente; sem motivo específico além da política da ferramenta.
Contém somente dados fictícios desta demonstração, cujo serviço já encerrou.
Não contornar a restrição por outra ferramenta. As cópias Google estão na lixeira.

Leia ETAPA-7.md, NATIVO-ETAPA-7.md, CONTRATO.md, BANCO.md, SERVICO.md e TESTES.md.
83 testes direcionados finais passaram. A suíte completa Windows não passou:
1.292 executados, 3 falhas/36 erros/2 pulados; causas e fixture v3 corrigida
constam no relatório. O CI Linux aprovado valida a plataforma de execução.
Navegador PT/EN com provedores fictícios; Drive real por conector.
Não misturar essas provas. Pilotos anteriores continuam encerrados e grants
antigos revogados; não reutilizar cópias da lixeira.

HTTPS persistente, campanha/idioma autoritativos entre bot/serviço,
capacidade/recuperação e bateria nativa combinada seguem pendentes. Ocorrência
anterior de imagem lenta deve ser medida na etapa 9 sem afrouxar os limites.
Serviço/ponte seguem fora do pacote público. Sem modelo pago, merge, deploy,
Gateway duplicado, escrita em oficiais/jogadores ou publicação da Carteira.

## Próximo passo

**Concluir a etapa 7**, continuando os domínios pessoais restantes e a
orquestração/conferência final no produtor, conforme a proposta de
INICIALIZACAO-PRODUTOR.md e depois provando a criação com
OAuth próprio das Guias quando o ambiente privado estiver disponível. Manter
a criação desligada até cumprir o critério do PLANO.md. Depois, etapa 8,
**GPT-6 Astra · Alto**; edições de jogo exigem contrato, prévia, confirmação e
recuperação próprios. Não iniciar a etapa 8 como se a 7 tivesse sido concluída.

Ao continuar: conferir árvore, remoto, PR e CI; usar o checkout SSD deste ambiente,
sem sobrescrever a árvore antiga do disco externo.
Testar proporcionalmente; documentação isolada não exige nova bateria extensa.
Atualizar fila, contrato, relatório e retomada, salvar commit/push na pilha
correta e separar sempre implementação, simulações, ensaio nativo e produção.
