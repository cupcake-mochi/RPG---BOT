# Conferência parcial por contrato REST

28/10/2026 · etapa 7 parcial, PR84, código `22b65125b283bee7bc37be3d79b8d554b4d19dab`. Criação bloqueada, sem publicação.
Main bot de42447/produtor ef361cc reconferidas antes da implementação.

## Contrato e conferência

Produtor exporta `r53/inicializacao/contrato_rest.json`; cópia idêntica em
`dados/ficha/inicializacao-rest-v1.json`. SHA256 fixado pelo consumidor:
1001e7c3605c754b5bf04c33cfd65542c90ef4b897deffda40167a2bafb30439.
Inclui hashes de seis fontes públicos, operações/guardas financeiras e política
de piso/custos/curva/missões. Não aceita contrato ou intervalos do navegador.
Atualização exige revisão/regen explícita, sem relaxar comparações por heurística.

`conferencia_inicializacao.py` integra `LeitorGradeRest` e validador determinístico.
Cada página deve ser a próxima e pertencer ao mesmo plano privado. A cobertura
exigida pelo contrato é conferida geometricamente antes da leitura; um plano
truncado não pode parecer completo. Não aloca um set das 126 mil posições.

Financeiro: conteúdo/notas a limpar, estado inicial de L2, emissão desmarcada e
13 fórmulas das sete guardas, por equivalências exatas exportadas. Nenhum saldo
ou benefício é inferido de prosa. O histórico inteiro é examinado, incluindo
últimas linhas, sem reter a grade financeira no objeto. Achados limitados aos
16 primeiros, com contagem completa dos demais; não param a varredura.

Progressão: rótulos, regra e entradas do nível; custos escolhidos em E/F da
CONFIGURAÇÃO; fórmulas/resultados em uso; prefixo da curva, zero no piso e
acumulados futuros; nível/base finais, missões vazias e suas fórmulas; XP total.
Espera-se a conta a partir dos custos literais, não de caches AR/Z que seriam
conferidos. Custo necessário ausente/formulado gera pendência, não é deduzido.
Fórmula correta com resultado ausente fica pendente. Conteúdo/erro não é ecoado.

A coleta de progressão ganhou CONFIGURAÇÃO C65:G93: oito páginas/1.894 posições,
27 GETs no transporte ou 28 com a observação final da conferência. Financeiro
permanece 50/126.168/153, ou 154 com observação final. Cota/contexto por GET e
prazo absoluto preservados. Registros antigos de sete páginas são históricos.
Sem nova rota, comando, escrita Google ou alteração do schema 6 do banco.

## Falha de piso encontrada no produtor

As fórmulas da ficha retornam “—” abaixo do nível inicial e XP 0 nele. O protótipo
GS exigia curva inteiramente numérica, recusando pisos acima de 2. A reprodução
falhou antes e passou após a correção. Testes anteriores simulavam uma curva
iniciada em 2 mesmo com piso 10; expectativas 3.700 foram corrigidas por evidência
das fórmulas e do Google, não para produzir verde. O consumidor também recusa
base herdada 3.700 no piso 10. Novo diário de escrita não foi criado/migrado.

Sondagem pelo conector Google Drive em cópia descartável: pisos 2/10/30,
custom 2100 no custo 10→11 e piso 1 sem/com custo explícito zero confirmaram a
semântica. Treze fórmulas financeiras coincidiram com variantes REST exportadas.
Cópia na lixeira, aba temporária fechada. Oficial/jogador intactos. Essa sondagem
não executou Apps Script nem o serviço com OAuth drive.file das Guias. Não é
prova nativa do inicializador ou da conferência Python inteira.

## Recibo de leitura, não diário de escrita

Após receber todas as páginas, o validador pode emitir recibo cifrado com Cifra
existente: contrato, contexto, arquivo, domínio, versão Drive, quantidade de
páginas, cadeia de hashes e resumo de resultado/erros/pendências. Não guarda
valores, notas, fórmulas, tokens ou a grade. Abertura exige o contexto esperado
do backend; recusa adulteração, outra fonte/domínio/versão e flags de liberação.
A cifra suporta reabertura/rotação de chaves, testadas com dados fictícios.

O recibo é histórico e não desbloqueia nada, mesmo sem erros. Não é persistência
transacional de operação, retomada de cursor, diário de limpeza, aprovação do
mestre ou prova de cópia nova. Não adotamos diários PropertiesService como se
estivessem no banco. Sheets REST não os fornece. Nenhum banco real foi aberto
para essa etapa; só envelopes em memória/temporários de teste.

## Limites que permanecem

Criação, conferência conjunta, imagens e consistência temporal permanecem falsas.
Só `conferencia_parcial_concluida` descreve cobertura destes dois domínios, com
erros/pendências e limites explícitos. Zero achados não significa ficha pronta.
Versão igual não congela cálculos externos. Relatórios não expõem valores/IDs.

Ainda faltam: estado persistido/concorrência/recuperação de escritas e vínculo
com cópia recém-criada; propriedades privadas do produtor e demais domínios;
preservação global/arte; autorizações reais e fila no serviço, automações/
treinos/notas e responsável; prova nativa combinada com o OAuth das Guias.
Etapas 8–10 pendentes. Não ampliar escopos, usar credencial da Arquivista,
publicar scripts.run ou tornar criar_por_modelo permissivo para contornar isso.

## Validação e entrega

23 novos testes do consumidor e 95 direcionados existentes passaram nos lotes
desta continuação, incluindo reabertura/rotação do recibo.
[CI completo 40743430137](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40743430137)
aprovado no código 22b6512: **1.385 executados/1.384 aprovados/um opcional**,
zero falhas, 181,422 s. Job concluído em 28/10 às 15:19:00 Brasília. Não foi
repetida a suíte completa local; logs do arquivo da execução conferidos. Produtor: 47 novos de
contrato/piso, 82 progressão, 67 sequência e 43 leitura locais passaram. CI completo produtor 40743272303 aprovado no código
d7adec7: 2.999 cenários/zero falhas, pacote nove arquivos/sintaxe 277 Python/
256 JS-GS e demais regressões, 28/10 às 15:18:33 Brasília. Duplicado
40743263267 cancelado; fechamento só documental [skip ci].

ZIP ignorado regenerado sem env, 90 arquivos; CRC e bytes comparados aos fontes,
sem Carteira, credenciais, bancos ou campanha. SHA256:
2f7d0cd08c22b7d405a127fe8ef9e9f7193b19056f5a551490de09cd88f64720. Nada publicado.
Sem merge/deploy, modelo pago, escopo novo, publicação Apps Script ou escrita em
oficial/jogador. Só células da cópia descartável usada na sondagem foram editadas.
Sol Alto para concluir integração; Médio para revisão focal. Não alterar modelos.
