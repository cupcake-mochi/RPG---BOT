# Nova ficha R53 — proposta de contrato de inicialização 1

28/10/2026. **Proposta para implementação e validação no produtor. Não é uma
rotina geral disponível nem um certificado aceito pela Carteira.** A criação segue
bloqueada. Este documento define o trabalho necessário para sair desse estado,
com inventário ancorado nas fontes atuais e critérios verificáveis.

Repositórios reconferidos nesta continuação:

- Ficha---RPG-JJK main: `ef361ccdf7a0210781176e3c42d318cde147553d`; PR 31, código `2427024`.
- JJK---Project: `353d7728fa4f505f830dc6c0421929a0ab2668c1`.
- Consumidor: PR 84 de RPG---BOT, dependente da etapa 6; sem publicação.

Os fontes abaixo não substituem uma inspeção do código instalado na cópia.
`r53/OFICIAIS.md` registra os incrementos das oficiais; o pacote integral
gerado não foi instalado por esta tarefa e não deve ser promovido por rotina.

## Diagnóstico integrado ao serviço · 28/10 — offline

`Consultas.diagnosticar_grade_copia` usa referência tipada de operação existente,
alvo origem/cópia e domínio fixo. Banco deriva o arquivo e vincula operação,
modelo, iniciador e autorização. Só modelo particular fora das oficiais; cópia
não cadastrada, propriedade/privacidade/marcadores reconferidos antes/depois das
amostras. Acesso atual também é reconferido na espera de cota/fila e na entrega.
Fila/OAuth/cotas compartilhados, duas coletas limitadas, sem escrita ou adoção de
versões. Flags de mudança antes/depois da coleta não são aprovação. Origem também pode
ser lida ainda na intenção preparada, sem fixar versão ou enviar cópia.

122 direcionados distintos aprovados/35 novos; CI completo deste código pendente.
Composição no serviço implementada e testada por HTTP fictício; execução real ainda
não ocorreu. Causa das versões/preparação global/propriedades/prova integral
continuam pendentes, criação bloqueada e sem publicação.
[Execução e limites](DIAGNOSTICO-SERVICO-2026-10-28.md). Sol Alto; revisão Médio.

## Comparação de leituras · 28/10 — só diagnóstico offline

`DiagnosticoGrade` compara duas coletas estritas da mesma fonte/contexto e separa
literais, fórmulas, resultados, notas e formatos numéricos. Guarda HMACs transitórios
por instância, sem dados de células ou hashes no resumo/banco. Informa cobertura
parcial/incompatível e descarta tudo em erro de acesso/transporte ou cancelamento.
Nenhuma guarda de versão mudou; não é preparo de conteúdo ou autorização de escrita.

112 direcionados distintos aprovados, 25 novos. Código `4a36ef9344db432ddec773bdf446de114b7b31de`:
[CI completo 40801082703](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40801082703)
aprovado em 28/10 às 22:37:43 Brasília: 1.558 executados/1.557 aprovados/um
opcional pulado, zero falhas, 263,278 s. Fechamento só documental, sem repetir
suíte/pacote/publicação.
Ainda faltam composição autenticada no piloto e ensaio controlado somente de leitura;
causas das versões, protocolo da fonte/candidata, propriedades e prova integral
continuam pendentes. Sem novo OAuth/Google/Discord, criação ou publicação.
[Roteiro e limites](DIAGNOSTICO-GRADE-2026-10-28.md). Sol Alto; revisão Médio.

## Candidatas e diagnóstico · 28/10 — offline

Novas cópias guardam a primeira observação da candidata antes do recibo. A fonte
é conferida antes da busca e novamente após a candidata; o destino é reobservado
antes da identificação. Nenhuma versão divergente é adotada. Histórico cifrado de
até 12 observações registra etapa/versões/horários, sem renovar a retenção ou
alterar campos de autoridade. Protocolo interno 2 no schema9/ledger2 existentes;
legado compatível e criação bloqueada. Cópia já alterada falha antes de ler células.

100 direcionados distintos aprovados/19 novos; duas reproduções anteriores confirmadas.
Restauração sem versão original agora recusa antes de ler arquivos; os 32
testes de cópia passaram em 6,489 s. Código final `eeb78f98a63f355e16c8b06dde24c80e4108ca80`:
[CI completo 40798497466](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40798497466)
aprovado em 28/10 às 22:13:05 Brasília: 1.533 executados, 1.532 aprovados,
um opcional pulado, zero falhas, 297,175 s. Fechamento só documental, sem repetir
suíte/pacote/publicação. Não houve ensaio nativo novo,
OAuth, pacote publicado ou mudança no produtor. A causa das versões nativas e a
preparação de conteúdo continuam pendentes; não atribuir cache ou repetir cópias.
[Implementação e limites](CANDIDATAS-2026-10-28.md). Sol Alto; revisão Médio.

## Ensaio financeiro encerrado · 28/10 — recusas seguras

A primeira cópia passou de versão 9 para 10 durante a leitura financeira;
`alterada`, zero POST Sheets e nenhum diário financeiro. Na segunda candidata,
a leitura completa fechou na versão 9, mas a fonte passou de 12 para 13 antes
da identificação; operação recusada, sem iniciar a segunda escrita. A causa
das mudanças não foi demonstrada. O diagnóstico não comprovou problema de cache.

Fonte/duas cópias na lixeira, grant revogado e recusa sem acessar arquivos;
dados fictícios removidos, bancos íntegros, porta livre/runners encerrados.
Limpeza concluída às 21:36:57 Brasília. **A escrita financeira real continua pendente**;
não houve injeção de resposta HTTP200 nem reconciliação pós-escrita real.

Próximo: investigar versões e definir a fase de candidata antes do primeiro
recibo, sem atualizar versões de cópias já identificadas. Propriedades Apps
Script e demais domínios/prova integral continuam pendentes. Sem código novo,
suíte/ZIP repetidos ou publicação. [Relatório](NATIVO-FINANCEIRO-2026-10-28.md).
Sol Alto; revisão Médio. Registros abaixo históricos.

## Células financeiras · 28/10 — 7C parcial, só offline

O serviço interno agora planeja os resets do contrato, grava o diário antes de
enviar e reconcilia por leitura após erro, cancelamento ou reinício. Só aceita
cópia própria comprovada, privada e ainda não cadastrada. Nenhuma escrita real
foi feita nesta rodada. Schema 9/ledger 2; sem endpoint ou liberação de criação.

**As cinco propriedades do Apps Script continuam pendentes.** Células conferidas
não significam financeiro concluído. A API também não impede edição simultânea
do dono entre a observação da versão e a escrita; essa lacuna bloqueia a criação
pública. Faltam ensaio descartável desta escrita, demais domínios, preservação
global, automações e prova integral. Etapas 8–10 continuam pendentes.

Código `7491d811ee0d3ab7f3455fddc736ee4430d4bb2e`:
[CI completo 40788244056](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40788244056)
aprovado em 28/10 às **20:39:53 Brasília**: **1.514 executados, 1.513 aprovados,
um opcional pulado**, zero falhas, 331,040 s. Fechamento só documental [skip ci],
sem repetir bateria, pacote ou publicação.

[Implementação, testes e próximos passos](FINANCEIRO-REST-2026-10-28.md).
Sol Alto para continuar; Médio para revisão. Registros abaixo são históricos.

## Cópia recuperada no Google · 28/10 — prova da 7B

O método novo enviou um POST real que ficou sem resposta registrada e manteve
`copia_incerta` (23,411 s). Após reiniciar, encontrou e validou a mesma cópia em
21,293 s: três GETs Drive/um OAuth, **zero POST Drive e zero Sheets** na retomada.
Destino próprio/privado e origem inalterada. A injeção de perda planejada não
foi usada: a perda da resposta aconteceu no transporte real.

Concessão revogada, tentativa posterior recusada antes de acessar arquivos,
dados fictícios locais removidos, ambos os bancos íntegros, duas descartáveis
na lixeira e piloto desligado. Nenhuma célula/GS/oficial/jogador alterado.
Próximo bloco **7C**: diário de escrita e reconciliação financeira; depois **7D**,
preservação/automações e ensaio integral. Criação permanece bloqueada.
Código/CI 9cb8a84/1.486 intactos; fechamento apenas documental [skip ci], sem
suíte/ZIP novos, merge/deploy. [Prova real e limites](NATIVO-COPIAS-2026-10-28.md).
Sol Alto para continuar; Médio para revisão.

## Cópia com recuperação · 28/10 — etapa 7B, offline

Backend interno agora guarda o envio antes do POST e, após resposta perdida,
só reconcilia a cópia existente. Schema 8/ledger 2, vínculo ao iniciador/modelo/
concessão, verificação do destino privado, backup sem replay e exclusão tratados.
Sem endpoint, escrita Sheets, cadastro ou liberação de criação. 197 locais distintos aprovados, 29 novos
com HTTP fictício; prova nativa da cópia ainda pendente.

A etapa 7 foi subdividida para mostrar o avanço: **7A** modelo/leitura/retomada
implementados; **7B** cópia implementada offline; **7C** limpeza/inicialização REST
pendente; **7D** preservação/automações e prova completa pendentes. Etapas 8–10
continuam na fila. Próximo: diário de escrita/reconciliação financeira; não repetir
a leitura nativa anterior como se validasse cópia ou limpeza.
Código `9cb8a84a9afa151c26fd1c5eeed829c6312651db`:
[CI completo 40772021442](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40772021442)
aprovado em 28/10 às **18:32:26 Brasília**: **1.486 executados/1.485 aprovados/um
opcional**, zero falhas, 300,149 s. Fechamento só documental [skip ci], sem nova
suíte, ZIP ou publicação. Piloto de cópia preparado em base própria; consentimento
Google pendente do usuário, sem executar o método novo no Google ainda.

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

## CARTEIRA e memórias · continuação de 28/10

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

## Histórico: inventário e equipamento · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`86410bee3fc70fa81f124a695253e032688c3ebe`. Main `ef361cc` reconferida,
sem alteração desde o checkpoint anterior; bot main `de42447` também igual.

Três perfis novos: equipados (cinco campos), equipáveis guardados (88) e itens
(36). Restauram fórmulas/notas, limpam estoque e valores pessoais, preservando
configurações e catálogos. Quatro notas vivas antigas são limpas sem escrever
nas suas fórmulas protegidas. Soco, mão livre e Traje 1 são defaults da ficha;
não concede dinheiro, estoque ou treino. Fórmulas desconhecidas recusadas.
A variante decimal 0,1 observada nas oficiais é aceita somente nas fórmulas
inteiras conhecidas de Volume; mudança de número/referência continua recusada.
Contratos anteriores e assinatura financeira v1 mantidos.

417 cenários direcionados de formação/inventário e 101 financeiros passaram;
a coleção de inicialização soma 921 (101/82/78/243/417), confirmados pelo
[CI 40683614201](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40683614201),
aprovado em 28/10 às 08:56:07 Brasília no código `86410be`, junto ao pacote,
regressões, catálogo/progressão/Kaori e sintaxe 277 Python/220 JS-GS.
Duplicado 40683604255 cancelado. Fechamento produtor `edea21b` só documental,
`[skip ci]`. Leitura de 161 entradas/
guardas por oficial, zero diferenças e nenhuma escrita.

Projeção Sheets API em cópia privada do Ciclo: 129 campos/notas e quatro notas
isoladas restaurados; 2.678 posições, 10.450 comparações preservadas sem diferença.
Carga 0,3 de 5 igual ao modelo, por causa do Traje 1; nenhum erro nas faixas.
Cópia na lixeira, aba fechada. **Não executou os novos diários Apps Script,
OAuth das Guias ou automações.** Relatório do produtor:
`r53/inicializacao/INVENTARIO-2026-10-28.md`.

Próximo: campos pessoais restantes da CARTEIRA e propriedades de recuperação;
depois entidades/cartões/MONTAGENS. Ainda faltam arte/caches/recuperações,
orquestração/conferência conjunta, automações/notas vivas/treinos iniciais,
novo responsável, integração executável drive.file e prova nativa completa.
**Criação incondicionalmente bloqueada.** Avisos vazios não são aprovação;
notas vivas serão regeneradas na fase final. Não apagar diários para reiniciar.

Bot runtime `26ec106`, CI 40496955301 (1.314/1.313/um opcional), PR 84 base 83.
Consumidor só docs, sem repetir suíte ou gerar ZIP. Protótipos fora do pacote/bot.
Sem merge em main, deploy, Gateway, modelo pago, novos escopos ou escrita em
oficial/jogador. Próxima implementação GPT-6 Astra / Alto; revisão focal Médio.

## Histórico: técnica e Famílias · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`763a78bd5fd3d799dd1273f24b6839a5c118d47a` (domínios em `a92cba8`). Main
`ef361ccdf7a0210781176e3c42d318cde147553d` incorporada pelo merge `a72adc0`
(PRs 41–43). Inclui XP manual/missões congeladas e registro do backup 13 das
oficiais feito por outro trabalho; não reaplicar aquela instalação.

Dois perfis novos: **11 entradas do cabeçalho da técnica e 19 estados de
Famílias**. Nove Famílias do livro voltam a Neutra; dez custom recuperam as
fórmulas originais, sem apagar as definições do servidor. Nome/atributo/CD
derivados são preservados. O nome declarado da técnica na CARTEIRA ainda
precisa de domínio próprio, assim como cartões/amparo e sincronizações.
Os quatro contratos anteriores e a assinatura financeira v1 ficam iguais.

**782 cenários locais passaram** (101 financeiro, 82 progressão, 78 identidade,
243 pessoal, 278 formação), 90 a mais que o checkpoint anterior. Duas regressões
usam as novas notas de XP congelado: financeiro remove marcas herdadas;
reinserção depois impede progressão. Mais 87 verificações upstream de XP manual.
O CI 40681047195 passou os 782 cenários, mas faltavam dois commits históricos
para os testes salariais incluídos pela main. O workflow agora busca somente
as duas bases imutáveis, sem pular testes ou mudar expectativas. As 15
verificações de abertura e 2.076 de missões passaram localmente. [CI corrigido 40681468287](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40681468287)
aprovado em 28/10 às 08:39:49 Brasília no código `763a78b`: 782 cenários,
regressões, pacote de nove arquivos, catálogo/progressão/Kaori e sintaxe
277 Python/220 JS-GS. Duplicado 40681461827 cancelado. Fechamento produtor
`5c93e005964360a157a0883857f1951609ce9539` só documental, `[skip ci]`.

Leitura das duas oficiais: 84 entradas/guardas cada, sem divergências ou escrita.
Projeção pela Sheets API em cópia privada descartável da Era: 30 alvos
restaurados, 2.048 posições inspecionadas e 8.132 comparações preservadas sem
diferença. Duas custom (incluindo nome com *) ficaram Neutra; oito vazias.
Fórmulas com vírgulas deram erro de análise na API; a variante exata com ponto
e vírgula observada nas oficiais resolveu. Não altera conta ou referência.
Nenhum erro final nas faixas inspecionadas. Cópia na lixeira, aba fechada.
**Isso não executou o inicializador/diários Apps Script ou o OAuth das Guias.**
O setValues real e a retomada dos novos perfis ainda exigem ensaio nativo.
Relatório: `r53/inicializacao/TECNICA-FAMILIAS-2026-10-28.md` no produtor.

Próximo bloco: inventário/equipamento. Também faltam campos da CARTEIRA,
entidades/cartões/MONTAGENS, fotos/caches/recuperações, orquestração/conferência
conjunta, treinos iniciais/automações, novo responsável, integração executável
com drive.file e prova nativa completa. **Criação incondicionalmente bloqueada**;
protótipos fora do pacote/bot. Não reiniciar fases apagando diários.

Bot runtime `26ec106`, CI 40496955301 (1.314 executados/1.313 aprovados/um
opcional), PR 84 na base da 83. Aqui só docs do consumidor: sem repetir suíte
extensa ou gerar ZIP. Sem merge em main, deploy, Gateway, modelo pago, escopos
novos ou escrita em oficial/jogador. Próxima implementação GPT-6 Astra / Alto;
revisão focal Médio. Não alterar configurações automaticamente.

## Histórico: Grau, Origem e treinos · continuação de 27/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`73dffda`, main `64b84e4cef0b1b0a05c2159c9dc700459a0f2dc9` incorporada por
`3f57c19` (PRs 39/40). A instalação salarial/backup 12 das oficiais foi feita
por outro trabalho e apenas registrada aqui; não reaplicar.

Quatro perfis novos, **268 células**: Grau/Origem (10), Perícias (99),
Ofícios/TR (94), armas (65). Restauram defaults e notas de fábrica;
preservam catálogos, fórmulas protegidas, formatos e validações. Grau 4 de
fábrica, sem inferir pelo nível ou inventar configuração de campanha.
Descrições/Ofícios custom voltam às fórmulas. Bônus custom usam AL, sem
apagar espelhos antigos ou interiores de mesclas. W86 é validado contra a
fórmula final do módulo salarial, não a fórmula antiga de Pessoal.gs.

**692 cenários offline** passaram (101/80/78/243/190); 190 novos cobrem
escritas, concorrência, variantes exatas, notas e matriz parcial. Assinatura
financeira v1 mantida. Limites por perfil: quatro escritas por chamada,
210 s e diário de até 9.000 bytes UTF-8. Estado intermediário desconhecido
é recusado, sem sobrescrita ou rollback automático. Regressões upstream:
2.076 verificações de missões e 95 salariais; não somar à suíte do bot.

CI Linux do produtor `73dffda` aprovado: [40546156146](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40546156146),
27/10 às 14:00:26 Brasília. Os 692 cenários passaram no CI, junto ao pacote,
regressões, catálogo/progressão/Kaori e sintaxe (277 Python/219 JS-GS).
Run duplicado 40546148817 cancelado. Fechamento posterior só documental
com `[skip ci]`; não exige nova suíte do bot nem publicação.

Leitura Google das duas oficiais: **457 conferências por arquivo**, zero
divergências; sem escrita. Não houve nova cópia, projeção por API, executor
Apps Script ou OAuth das Guias nesta rodada. Ensaios anteriores não validam
este executor. Relatório do produtor: `r53/inicializacao/FORMACAO-2026-10-27.md`.

Faltam técnica/Famílias, inventário/equipamento, entidades/cartões/MONTAGENS,
fotos, caches/recuperações, orquestração/conferência conjunta, treinos
iniciais/automações, novo responsável, integração executável drive.file e
prova nativa completa. **Criação permanece incondicionalmente bloqueada**;
protótipos fora do pacote/bot. Não apagar diários para reiniciar fases.

Bot runtime `26ec106`, CI 40496955301 (1.314 executados/1.313 aprovados/um
opcional), PR 84 na base da 83. Consumidor mudou somente docs; sem repetir
suíte extensa ou gerar ZIP. Sem merge em main, deploy, Gateway, modelo pago,
escopos novos ou escrita em oficial/jogador. Próxima implementação:
GPT-6 Astra / Alto; revisão focal Médio. Não alterar configurações automaticamente.

## Cobertura anterior: escolhas, recursos e condições

Produtor `a55517d` (PR 31), além de financeiro/nível-base/textos: três domínios
em `pessoal.gs`, contrato público em `contrato_pessoal.gs`, APIs Previa/Aplicar.

| Domínio | Escopo novo | Limite |
|---|---|---|
| Escolhas básicas | 19 entradas na FICHA: seletores principais, atributos, distribuição de Corpo/marcos e atributos pessoais de ataque/CD | Defaults da fábrica, sem escolher Grau, treinos, capacidades ou completar criação |
| Recursos/bônus | 20 entradas; atuais ligados aos máximos por fórmula; bônus/temporários zero, ± vazio | Máximos reconhecidos e preservados; fórmula pessoal desconhecida recusada |
| Condições/descanso | Nove entradas de condição, Sequelas/extras, Exaustão, resistências/imunidades e descanso | Notas de fábrica restauradas; instruções de cabeçalho preservadas |

CI Linux do produtor `a55517d` aprovado:
[40540295538](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40540295538), 27/10 às 13:24:13 Brasília.
Run duplicado do push também passou antes da tentativa de cancelamento;
registro posterior apenas documental, sem nova suíte do bot ou pacote.

502 cenários offline passaram (101/80/78/243); não somar à suíte do bot.
Diário único de cena excedia tamanho: domínios separados e guarda de 9.000
bytes UTF-8 antes de gravar. Novos tipos internos de escrita de fórmula/nota
conhecida não aceitam planos do navegador. Assinatura financeira v1 mantida.

Leitura nativa: 112 conferências por oficial, zero divergências depois das
variantes exatas de aspas/separador. Projeção de efeitos em cópia privada do
Ciclo: 48 entradas/notas, 11.634 comparações delimitadas preservadas sem
diferença; máximos/atuais acompanharam novas escolhas (23/23, 8/8, 26/26).
Cópia na lixeira, aba fechada. Não executou novos diários Apps Script/OAuth.
[Registro completo](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/a55517deb9b77c43b796c80ac41f1029c0fdebd7/r53/inicializacao/ESCOLHAS-RECURSOS-2026-10-27.md).

Criação continua bloqueada; falta orquestração, conferência conjunta,
Grau/treinos/capacidades de Origem/técnica/Famílias/inventário/entidades/cartões,
fotos/arte, caches/recuperações, latência, automações e novo responsável.
Nenhum pacote instalado ou publicação. Ver ETAPA-7.md para o próximo bloco.

## Histórico: nível/base e textos

PR 31 em rascunho, código `280a7dc`, incorpora a main acima (merge `8cb12ac`).
O executor financeiro foi extraído para perfis fixos sem mudar o diário v1;
a assinatura anterior tem regressão. Não aceita plano enviado pelo navegador.

| Protótipo | Escritas | Preservação e limite |
|---|---|---|
| Nível/base XP | FICHA AH11; DADOS CZ54 | Usa regra inicial e curva da campanha; exige fase financeira da mesma operação e missões vazias. Não altera fórmulas ou distribui atributos/marcos. |
| Textos pessoais | 14 entradas e notas em CARTEIRA/FICHA PESSOAL | Rótulos e espelhos conhecidos; nome volta ao texto de preenchimento. Imagens em célula recusadas; imagens sobrepostas ainda não tratadas. |

Leitor recusa CellImage/objetos em vez de misturar imagens como `{}`. Regra
G46 aceita `,` ou `;` da fórmula conhecida, sem afrouxar outras diferenças.
259 cenários offline (101/80/78) e 20.643 verificações XP passaram. Projeção
nativa dos efeitos via Sheets API, numa cópia nova privada da Era: 14 entradas
limpas, nível 10/base 3.700, missão de 50 levou XP a 3.750 e retirada voltou
a 3.700. 8.998 comparações delimitadas preservadas sem diferença; cópia na
lixeira, aba fechada. [Alvos e prova](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/280a7dcd0b3fb56b0a43dd6e0d88aaadcb08d634/r53/inicializacao/NIVEL-TEXTOS-2026-10-27.md).

No fechamento, main avançou para `b0dc6aacef08b2c01a7f8a3519bbcc9bff9546ed`
(PR 37 salarial) e foi incorporada no merge `84bcd56` do produtor. Fórmulas
protegidas/alvos dos inicializadores não mudaram. 15 verificações de abertura,
95 salariais e 101 financeiras passaram após o merge. O ensaio nativo descrito
é anterior; não valida execução desse código Apps Script. Nada foi instalado.

CI final do integrado `84bcd566ae74d73bd8fdaf3889aa1ab5d7c68722`
aprovado: [40535287570](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40535287570), 27/10 às 12:53:51 Brasília.
Os 259 cenários, pacote de nove arquivos e regressões passaram; 277 fontes
Python/208 JS-GS com sintaxe válida. Run duplicado cancelado. Registro final
posterior só documental. Prova do OAuth/Apps Script completo continua pendente.

CI anterior, antes da PR 37, aprovado no código `280a7dc`:

[40534237271](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40534237271), 27/10 às 12:47:26 Brasília.
Confirmados os 259 cenários, pacote de nove arquivos sem inicializadores,
sintaxe e regressões. Run duplicado do push cancelado; registro posterior
só documental, sem repetir a bateria do bot.

**Não executou os novos diários Apps Script nem OAuth próprio das Guias.**
Ensaio financeiro antigo `4f3555d` não valida o executor extraído. Todos os
perfis mantêm `criacaoDisponivel=false`; bot não os chama e criação continua
bloqueada. Falta orquestração e conferência conjunta: depois de mudar o nível,
não repetir o financeiro antigo nem apagar diários para reiniciar fases.

Ainda faltam fotos/arte, escolhas, atributos/treinos/marcos/recursos,
inventário, entidades/cartões e recuperações/editor; considerar também os
caches novos `r53_versoes`/`r53_marcas_custom`. Automação, latência, prova do
novo responsável e integração permitida com drive.file continuam exigidas.
Nenhum pacote instalado, merge em main ou deploy nesta continuação.

## Registro anterior: esclarecimento e financeiro

O usuário confirmou: o modelo do servidor é a ficha do sistema com
configurações extras da mesa. Preservar regras e catálogos do servidor;
não herdar identidade, progressão, inventário, missões, cartões ou dinheiro
de personagem anterior. Não solicitar uma lista de escolhas prontas novamente.

O primeiro domínio ganhou implementação **separada no produtor**:
[PR 31, em rascunho](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31),
branch `codex/inicializacao-financeira-carteira`, código
`4f3555d2634c84899e5004733245ae69d0f83c6d`, base `d0836390`;
registro nativo/documentação em `352929a` (sem alteração de código).
`r53/inicializacao/financeiro.gs` faz prévia, aplicação explícita e retomada
financeira. Conteúdo, notas e cada propriedade têm passos distintos para
retomar após interrupção. Não expõe endpoints nem instala eventos/acionadores;
não entra no pacote atual e não é chamado pelo bot.

99 cenários offline novos passaram, incluindo falhas antes/depois de todas
as escritas, edição concorrente, prévia antiga, notas, estado parcial e
preservação. Regressões focais: 95 verificações salariais e 64 cenários/611
verificações de missões. CI Linux do produtor aprovado no mesmo SHA:
[40505846627](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40505846627).
A execução duplicada do push foi cancelada; a execução da PR passou no
mesmo código; não é falha de teste. Não somar esses resultados à suíte do bot.

Leitura nativa pontual das duas oficiais confirmou grade de 1.000 linhas e
as âncoras financeiras esperadas, sem alteração. Prévia do protótipo em uma
cópia descartável do Ciclo concluiu em 115,013 s. Não é latência aceitável de
comando Discord nem prova de inicialização completa; o protótipo é executado
explicitamente no Apps Script. Primeira aplicação atingiu 360,813 s; a mesma
operação retomou e concluiu
em 236,503 s. Foram implementados orçamento de 210 s, limite de quatro passos
por execução e retirada de conferências duplicadas, com retorno incompleto
retomável. O orçamento não cancela chamadas Google nem garante duração.
Ver [registro nativo no produtor](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/codex/inicializacao-financeira-carteira/r53/inicializacao/NATIVO-2026-10-27.md).
Na segunda cópia, a versão corrigida concluiu em 283,416 s; repetição em
150,489 s, estado comparado igual. Regras, fórmulas, formatos e financeiro
conferidos externamente; ambas as cópias estão na lixeira. A lista de
acionadores ficou vazia para a conta conectada. Ainda falta otimizar a
latência e provar automações/identidade/integração, sem tratar esse ensaio
financeiro como uma ficha inteira pronta.

O retorno financeiro mantém `criacaoDisponivel=false`. L2 sem emissão é
`{"versao":1,"graus":[]}` somente no modo salarial por fórmula; o leitor real
o aceita e as fórmulas condicionam o ciclo a N2 numérica. Isso não libera o
modo legado nem cria dinheiro inicial. Nível/XP e regras da mesa são
preservados neste domínio, não inicializados como personagem novo.

Os flags do contexto são pré-condições de um futuro criador confiável,
**não autenticação ou prova vinda do navegador**. Ainda faltam inventário
pessoal completo, propriedades de recuperação, automações, responsabilidade
e execução compatível com drive.file. O consumidor permanece bloqueado,
mesmo com o domínio financeiro concluído. Não declarar a etapa 7 pronta.

## Inventário financeiro anterior e domínios ainda exigidos

Referências fixadas no commit do produtor:
[Salarios.gs](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/d0836390f90b435b4796313e898eaaa1a4a4da8b/apps-script/Salarios.gs),
[SalarioLote](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/d0836390f90b435b4796313e898eaaa1a4a4da8b/r53/diagnostico-android/salario_lote.gs) e
[EditorR53](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/d0836390f90b435b4796313e898eaaa1a4a4da8b/apps-script/EditorR53.gs).

| Área | Estado que exige tratamento de nova ficha | Preservação/decisão necessária |
|---|---|---|
| EXTRATO A2:C até o fim físico | Lançamentos e saldo de personagem anterior | Preservar cabeçalhos, formatos e proteção; não criar saldo anterior a partir de O86 |
| SALÁRIOS A2:L até o fim físico | Créditos/fechamentos anteriores | Preservar estrutura; total inicial não pode somar crédito herdado |
| DADOS_SALARIOS A2:G até o fim físico | Registro de identidade, nome, tipo, data e vínculo de missão | Deve concordar com as missões novas; só apagar o livro não elimina essas identidades |
| DADOS_SALARIOS H2:J até o fim físico | Histórico de mudanças de Grau/regras/emissão | Não herdar regras históricas de um personagem; conservar regras atuais da campanha na CONFIGURAÇÃO |
| DADOS_SALARIOS L2 | JSON do módulo legado: início, graus, última emissão e possível agenda | Produtor precisa definir o estado inicial válido para as versões instaladas; apagar L2 ou gravar `{}` sem essa prova não basta |
| DADOS_SALARIOS N2 | Data efetiva da emissão | Nova ficha sem emissão; preservar o cabeçalho N1 e as fórmulas que exibem N2 |
| FICHA PESSOAL AW:AX, BC:BD, BI:BJ, BO:BP, linhas 15–87 | Nome/tipo de missão e nota com `[Salário: ...]` | A identidade viaja na nota. Remover texto visual não remove a identidade; definir as demais entradas de cada missão sem apagar XP calculado |
| FICHA PESSOAL O86 | Caixa de lançamento, inclusive fórmula customizada | Não converter conteúdo herdado em saldo inicial; valor inicial permitido precisa ser definido pelo produtor |
| FICHA PESSOAL BI11 e BO11 | Caixas/resultado de correção de data de missão | Não preservar correção do personagem anterior |
| Fórmulas financeiras | Q2:Q8, P11 e AA2 de DADOS_SALARIOS; W86 da FICHA PESSOAL; painel da CONFIGURAÇÃO | Preservar âncoras e seus derramamentos; não limpar a aba inteira nem sobrescrever totais com zero |
| Emissão na interface | CONFIGURAÇÃO O38/O39 e CARTEIRA AH3/AT3 | Preservar fórmulas de apresentação e desarmar a ação de emitir; copiar não equivale a emitir |
| Nível e XP | FICHA AH11 e AN11/DADOS CZ47 | Nível atual é entrada própria. XP é calculado. Regra inicial F46/G46 da CONFIGURAÇÃO é separada e deve ser preservada |

As quatro entradas por missão foram inventariadas no protótipo financeiro.
Os dados do editor de cartões ainda precisam de inventário completo do produtor.
Essa tabela é um
escopo mínimo financeiro e não declara que todos os dados de personagem foram
enumerados. Nenhuma dessas linhas é uma lista de comandos de limpeza pronta.

## Estado fora das células

O fonte usa DocumentProperties `salario_extrato`, `salario_trocas`,
`salario_correcao_nome` e `salario_proximo` como contadores/cache, e
ScriptProperties `salario_edicao` para distinguir a rotina instalável.
`L2.agenda`, quando presente, referencia o projeto da agenda.

Os comentários do produtor indicam que contadores de propriedades não vêm
numa cópia; isso não foi convertido em garantia nativa desta tarefa. É preciso
inspecionar a cópia e rederivar o estado de acordo com seu próprio projeto.
Não copiar IDs de agenda, não cadastrar gatilho em nome do antigo responsável
e não usar `deleteAllProperties()` para resolver o problema: propriedades de
montagem, paleta e editor têm outros papéis e exigem tratamento explícito.

O EditorR53 também mantém Classe visível, amparo e recuperações de edições.
Restaurar uma recuperação antiga depois de limpar as células pode recolocar
dados do personagem anterior. O contrato do produtor deve cobrir esse estado
antes de declarar uma nova ficha pronta.

## Por que os preparadores atuais não inicializam uma nova ficha

- `salarioPrepararCarteira_` retorna sem limpar quando EXTRATO já existe.
- `salarioPrepararEmissao_` retorna se N1 já tem conteúdo; o cabeçalho copiado
  não prova que o estado financeiro da nova ficha foi zerado.
- `prepararSalarioLote` prepara fórmulas/painel e invalida cache, sem limpar
  livro ou missões, conforme seu próprio comentário.
- Reemitir/corrigir emissão preserva/congela pagamentos vencidos. Essas
  operações são de continuidade de personagem, não de criação de outro.

Não chamar essas rotinas em sequência e anunciar “inicialização concluída”.
Também não simular `onEdit` para tentar obter indiretamente seus efeitos.

## Protocolo exigido antes de implementar escrita

1. **Alvo:** vincular operação a uma cópia nova, distinta do modelo e de todos
   os arquivos registrados; recusar as oficiais e qualquer ficha preenchida.
   Identidade do novo responsável e acesso à cópia são provas independentes
   da autorização usada pelo administrador para escolher o modelo.
2. **Versões e prévia:** fixar versões do contrato, produtor instalado, modelo
   e cópia; listar os domínios tratados e o que será preservado. Alteração
   durante a espera invalida a prévia. Nenhum “pronto” vindo do navegador é prova.
3. **Responsabilidade:** produtor enumera todas as entradas, notas, propriedades,
   caches e recuperações envolvidas, inclusive os domínios ainda não cobertos.
   Parâmetros aceitos e estado salarial inicial recebem regras explícitas.
4. **Recuperação:** definir uma operação idempotente com ID estável, diário
   e resultado verificável. Interrupção parcial fica incompleta e não é
   cadastrada. Retentativa não relança dinheiro, emite carteira ou paga salário.
5. **Execução explícita:** decidir o que roda pela API e o que requer uma ação
   do responsável no Apps Script. Não ampliar o OAuth drive.file das Guias.
   Se a arquitetura exigir outro escopo, essa solução permanece indisponível
   dentro dos limites atuais; não contornar pelo conector de outra aplicação.
6. **Pós-condições:** conferir saldo/créditos/participação/emissão sem herança,
   notas e propriedades coerentes, fórmulas e proteções preservadas, parâmetros
   aplicados no lugar correto e editor sem recuperação de personagem anterior.
7. **Ativação:** provar com a conta do responsável as automações efetivamente
   necessárias, inclusive limitações no Android. Instruções manuais só aparecem
   no produto quando houver um procedimento existente e validado.
8. **Aceite:** repetir criação, falha, retomada e segunda execução em cópias
   descartáveis de Era, Ciclo e servidor sintético. Conferir independência do
   modelo, preservação dos personagens cadastrados e duas identidades Google.

## Papel da sondagem 2 do consumidor

A PR 84 passou a conferir a grade antes dos dados e ler o fim físico dos
livros EXTRATO, SALÁRIOS e DADOS_SALARIOS A:J. Limite de 5.000 linhas por
livro; uma grade maior é recusada, sem truncar para uma amostra aparentemente
vazia. A resposta Google continua limitada a 512 KiB e o timeout HTTP
configurado continua em 15 s.
Lê somente os campos necessários de CellData, inclusive as notas das missões.
Não guarda nomes de missão, valores de lançamentos ou texto de notas na prévia:
só sinais constantes de presença.

Referências anteriores continuam identificadas como sondagem 1; as novas,
como 2. A confirmação não mistura essas versões. Isso melhora o diagnóstico,
mas **não é inicialização**: propriedades, gatilhos, código instalado, editor
e todos os demais dados ainda não são certificados. Ausência de sinais nunca
habilita criar_por_modelo; a barreira continua incondicional.
