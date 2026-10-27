# Carteira viva e personagens

Planejamento de 26/10/2026. **Implementação em andamento; não publicada.**
Este documento reúne as decisões da conversa; não é uma lista de comandos
já disponíveis. Atualização: a [etapa 1](ETAPA-1.md) tem contrato/prova local
e a [etapa 2](ETAPA-2.md) tem banco/cadastro implementados localmente.
A [etapa 3](ETAPA-3.md) implementa o serviço e a conexão localmente.
O [piloto local com OAuth real](NATIVO-ETAPA-3.md) passou nos fluxos de
cadastro, renovação e reconexão. Próxima implementação: etapa 4.
Não há funcionalidade nova em produção.

- [Testes e critérios de entrega](TESTES.md)
- [Estado e instrução para continuar](RETOMADA.md)
- [Contrato definido na etapa 1](CONTRATO.md)
- [Banco e recuperação da etapa 2](BANCO.md)
- [Configuração Google e hospedagem pendentes](ACESSO-GOOGLE.md)
- [Fila geral do bot](../FILA-ATUAL.txt)

## O que vamos entregar

O jogador cadastra uma ficha que já tem, escolhe o arquivo numa tela do Google
aberta pelo bot e confirma o personagem no Discord. Pode cadastrar vários.
O servidor ganha uma galeria com cartões de apresentação. O dono da ficha e
a equipe autorizada têm acesso aos detalhes e à análise, em uma área privada.

A **Carteira viva** é a página do personagem, com apresentação, data da última
leitura e acesso às ações permitidas. A planilha continua sendo a fonte dos
dados de jogo. O bot guarda o cadastro e uma cópia compacta da última leitura,
sem duplicar toda a planilha nem ficar consultando todos os personagens.

Depois dessa primeira entrega, entram a cópia opcional do modelo do servidor
e as edições permitidas pelo Discord. Essas funções precisam comprovar que
preservam as automações da ficha antes de serem liberadas.

## Decisões fechadas

| Assunto | Comportamento combinado |
|---|---|
| Cadastro | Qualquer membro pode cadastrar os próprios personagens. Cadastro não significa aprovação. |
| Vários personagens | Um jogador pode ter vários no mesmo servidor. Cada um tem identificação própria e mostra o jogador responsável. |
| Galeria | `/personagens` abre a própria; `/personagens @jogador` abre a daquele membro, dentro do servidor atual. |
| Conexão | Botão no Discord abre autorização Google e seleção de um arquivo. Não exige que a ficha tenha sido criada pelo bot. |
| Acesso durável | Reutilizar a autorização enquanto for válida. Revogação, perda de acesso ou expiração podem exigir reconexão. |
| Consulta | Atualizar ao abrir o personagem; galeria usa resumos salvos. Navegação seguida pode reutilizar leitura recente. |
| Troca de arquivo | Ação “Trocar arquivo da ficha”, separada de “Atualizar dados”. Preserva o personagem e a apresentação, mas reavalia análise e aprovações afetadas. |
| Público | Apenas cartão básico, com os campos que o dono escolheu exibir dentro das regras do servidor. |
| Privado | Ficha detalhada e análise para dono, administrador/dono do servidor e cargos de revisão explicitamente autorizados. |
| Edição | Permissão separada de leitura e de revisão. Sem edição arbitrária de células ou fórmulas. |
| Personalização | Título, frase, imagem, cor e campos opcionais, com prévia antes de salvar. |
| Modelo do servidor | Padrão oficial; administrador pode selecionar outro compatível e parâmetros iniciais suportados. Nunca altera fichas já cadastradas automaticamente. |
| Link no nome | Abre a Carteira viva. Link direto da planilha fica na área autorizada, respeitando também as permissões do Google. |
| Análise | `/personagem analisar`, privada, com o motor determinístico existente e os limites humanos preservados. |

Não usar varredura periódica de todas as fichas, conta central como dona
obrigatória, nem autorização de edição pedida a cada consulta. Essas foram
alternativas discutidas, substituídas pelas decisões acima.

## Como será o uso

1. **Cadastrar:** `/personagem cadastrar` → “Escolher minha ficha” → Google →
   selecionar arquivo → conferir nome, servidor e prévia → confirmar.
2. **Consultar:** `/personagens @jogador` → escolher personagem → cartão e
   “Abrir carteira”. Detalhes privados exigem identificação e autorização.
3. **Atualizar:** “Atualizar dados” relê o arquivo vinculado. Se falhar,
   informa quando os dados foram lidos e não apresenta o cache como leitura nova.
4. **Substituir:** “Trocar arquivo da ficha” → selecionar novo arquivo →
   verificar acesso e formato → mostrar a troca → confirmar. Nada é apagado
   ou alterado no arquivo anterior.
5. **Revisar:** `/personagem analisar` → leitura atual → resultado privado.
   O mestre continua responsável por história, autorizações e partes não
   conferidas. “MESTRE VIU” continua sendo um lembrete.
6. **Personalizar:** “Editar cartão” → título, frase, imagem, cor e campos
   públicos → prévia → salvar. Isso inicialmente não modifica a planilha.
7. **Desvincular:** retirar o cadastro do bot, com explicação do que será
   excluído. Nunca apagar o arquivo Google junto. Desconectar a conta Google
   é uma ação distinta, pois ela pode atender outros personagens.

Os nomes acima são propostas de interface; confirmar colisões e limites de
comandos antes de registrar. Oferecer equivalentes em inglês e atalhos curtos
sem substituir comandos existentes. Pedidos de dados privados ficam nos
comandos privados, não nos atalhos públicos `GC:`.

## O que o código atual já oferece

Base remota conferida em 26/10: `main a7afebb17fc4ff0297699de13861d56d81825612`.
O commit documental local `de424478a7a120ecb43bd0c79eb93774d446fae6` registra a
publicação dessa main. Ele foi preservado como base deste planejamento.
O [registro de publicação](../PUBLICACAO-R57-2026-10-26.md) é evidência da rodada
anterior; não fizemos nova inspeção da Discloud para montar este plano.

| Reaproveitar | Cuidado necessário |
|---|---|
| `src/closure_bot/ficha_leitor.py` | Leitura por link/XLSX não equivale a acesso Google autenticado. Criar adaptador próprio. |
| `src/closure_bot/cogs/ficha.py` | Reaproveitar a análise e a leitura estável; o painel atual por link é público. A análise do cadastro deve ter saída privada própria. |
| `src/closure_bot/ficha_r53.py` | Preservar tratamento de cartões em transição e formato compatível. |
| `src/closure_bot/ficha_configuracao.py` | Campanha e aprovação exata existentes não podem ser substituídas por um selo genérico de cadastro. |
| `src/closure_bot/servidor.py` | Delegação atual é para idioma/lore. Não herdar acesso a fichas privadas desses cargos. |
| `src/closure_bot/registro.py` | A tabela chamada `fichas` guarda fatos das pessoas; não é o cadastro de personagens desta proposta. |

O contrato mecânico atual contém 18.393 chaves únicas. Ele não representa
automaticamente todos os campos de apresentação, imagens e biografia da
planilha. Mapear o que existe; oferecer perfil próprio para o que faltar,
sem inventar entradas nem extrair imagens por suposição.

## Arquitetura proposta

```text
Discord ── comandos e botões ── serviço de personagens ── banco próprio
                                   │                       │
                                   ├── leitura Google      └── resumo/cache
                                   └── análise existente

Navegador ── Carteira / conexão ── identificação Discord e Google
                                   │
                                   └── mesmo serviço e mesmas permissões
```

O serviço deve ser independente das conversas das personagens. Cadastro,
consulta, atualização e cálculos não chamam modelos de linguagem.

### Google e identidade

Usar OAuth Google com Picker e escopo `drive.file`, limitado aos arquivos
selecionados/criados pelo aplicativo. Esse escopo permite leitura **e escrita**;
não anunciá-lo como permissão Google somente de leitura. A primeira entrega
não terá rotas de escrita na ficha, mesmo com esse escopo.

O consentimento ocorre no Google, possivelmente no navegador externo do
celular. Não prometer que será concluído inteiramente dentro do Discord.
Vincular cada tentativa ao usuário Discord, servidor e ação, com expiração,
uso único, proteção contra troca de sessão e identificação Discord na página.
Autenticar o retorno; não confiar num ID de usuário ou arquivo enviado pelo cliente.

Guardar credenciais cifradas no servidor, com chave fora do banco e do Git.
Refresh tokens nunca vão ao Discord, aos logs, à URL ou ao frontend. Se o
Picker exigir access token no navegador, limitar sua duração e exposição;
não persistir em armazenamento do navegador nem incluir em telemetria.
Prever rotação da chave, reconexão, revogação e exclusão dos vínculos.

Não reutilizar credenciais da Arquivista. Aproveitar apenas padrões de código
que passem por revisão. Verificar consentimento público, domínio, política de
privacidade e requisitos do projeto Google; um teste que funciona para o
desenvolvedor não comprova funcionamento durável para qualquer jogador.
Conferir também o modo de publicação do consentimento: uma credencial de
teste com validade limitada não comprova renovação contínua em produção.

### Permissões e privacidade

| Ação | Dono do personagem | Outro jogador | Equipe de revisão | Administrador/dono do servidor |
|---|---|---|---|---|
| Ver cartão permitido | Sim | Sim, no servidor | Sim | Sim |
| Ver ficha e análise privada | Sim | Não | Sim, com cargo específico | Sim |
| Personalizar e trocar arquivo | Sim | Não | Não por ser revisor | Não assumir posse; usar fluxo administrativo auditado |
| Editar dados de jogo | Só operações liberadas e consentidas | Não | Só com capacidade de edição separada | Só fluxo de edição explicitamente autorizado |
| Configurar modelo/cargos | Não, salvo outra permissão | Não | Não por ser revisor | Sim |

Para estas novas capacidades, reconhecer dono e `Administrator`. A função
atual também aceita `Manage Guild`; não reutilizá-la sem distinguir gestão
de configuração, leitura privada e edição. Não alterar as permissões dos
comandos antigos por consequência desta mudança.

Revalidar permissões no servidor em toda ação, inclusive botões antigos e
sessões web. ID difícil de adivinhar não substitui autorização. A API pública
retorna apenas campos públicos; esconder elementos no navegador não protege
dados já enviados. Por padrão, a galeria exige participação no servidor;
“público” aqui significa visível aos outros membros, não indexado na internet.
Compartilhamento externo anônimo fica fora desta primeira entrega.

Acesso Google a um arquivo não prova autoria do personagem. Bloquear tomada
de cadastro existente; definir declaração de responsabilidade e transferência
com confirmação/auditoria. Mesmo arquivo em outro servidor exige novo vínculo,
consentimento e configuração, sem herdar campanha, análise ou aprovação.

Ao sair do servidor ou perder cargo, perder acesso privado imediatamente nas
novas requisições. Retenção e remoção do cadastro precisam ser documentadas,
com prazo definido na etapa 1. Não guardar ficha privada em memória de conversa
das guias nem permitir que uma conversa contorne a autorização do comando.
Revogação Google conhecida bloqueia novas leituras e o acesso ao snapshot
privado até resolver a autorização. Falha temporária de rede é diferente:
pode oferecer a última leitura ao usuário ainda autorizado, identificada
como antiga. Sem consulta contínua, não prometer detecção instantânea de
uma revogação externa que o serviço ainda não observou.

### Banco, leitura e desempenho

Começar com SQLite próprio, migrações e um serviço responsável pela escrita.
Não colocar SQLite em sistema de arquivos de rede nem dar a várias máquinas
acesso direto ao mesmo arquivo. Se bot e site rodarem separados, o site usa
a API autenticada do serviço; escolher hospedagem e persistência na etapa 1.

Guardar separadamente:

- configurações do servidor e capacidades dos cargos;
- personagem, servidor, responsável e identificador estável;
- conexão Google cifrada e vínculo com arquivo/revisão da fonte;
- campos públicos e personalização do cartão;
- última leitura compacta, versão do formato, horário e resultado da leitura;
- análise e referência das aprovações à fonte/conteúdo correspondente;
- operações pendentes, confirmações e auditoria mínima com retenção definida.

Não guardar XLSX completo, fórmulas, formatação, catálogo repetido por personagem
ou histórico ilimitado de snapshots. Distinguir zero, vazio e campo ausente.
Imagens ficam fora do SQL, com tamanho/quantidade limitados e política de
remoção. Não depender de URLs temporárias de anexos do Discord como arquivo
permanente. Validar imagens e impedir acesso do servidor a endereços internos.

Consultas próximas ao mesmo personagem compartilham uma leitura em andamento.
Cache e operações incluem servidor, personagem e revisão do vínculo, para uma
resposta antiga não sobrescrever uma troca de arquivo. Galeria paginada não
relê a planilha de cada card. Fila com limites por usuário, servidor e projeto,
tempo máximo e espera progressiva quando o Google limitar requisições.

A meta de ensaio é **100, 500 e 1.000 personagens cadastrados**. Isso não é
capacidade comprovada. Medir tamanho real, memória máxima, tempo de resposta,
concorrência e impacto no bot. O `RAM=256` do pacote não comprova a memória
contratada; o registro de 25/10 informa 700 MB. Conferir a alocação efetiva
antes do ensaio. Contagem de personagens não determina sozinha a necessidade
de banco pago, e trocar o banco não aumenta as cotas do Google.

### Trocar arquivo sem perder o personagem

Validar o novo arquivo antes de confirmar a troca. Gravar o novo vínculo e sua
revisão numa única transação; falha antes disso mantém o anterior. Uma leitura
antiga ou operação pendente não pode gravar sobre a nova revisão. Manter a
análise anterior identificada como antiga, sem transferir aprovação de uma
ficha diferente. Remover cache privado obsoleto conforme a retenção definida.

### Modelos e edição: duas verificações obrigatórias

1. **Copiar não basta:** comprovar acesso ao modelo com `drive.file`, destino
   e propriedade da cópia, fórmulas, scripts vinculados e ativação necessária.
   Limpar somente dados de exemplo conforme contrato explícito. Nunca levar
   emissão, salário, histórico ou aprovação de outro personagem para a cópia.
2. **Escrever não basta:** alterações pela API não disparam automaticamente
   `onEdit`, inclusive gatilhos instaláveis. Cada operação precisa declarar
   entradas, cálculos, efeitos secundários, confirmação e leitura de retorno.
   Evitar duplicação de salário, XP, emissão e trocas de Classe após repetição
   de pedido ou reconexão. Uma trava do bot não impede edição simultânea pelo
   jogador no Google; detectar conflito de conteúdo e nunca sobrescrever
   silenciosamente. Operação que não puder garantir isso fica indisponível.

Se uma integração exigir alteração no produtor, preparar contrato e PR no
repositório da ficha, com teste em cópia descartável. Nenhuma execução deste
plano autoriza editar uma oficial ou uma ficha real para experimentar.

## Etapas e modelo recomendado

Recomendações para o **Codex durante o desenvolvimento**, não para trocar o
modelo usado pelas guias. São escolhas de engenharia para este projeto,
apoiadas na [orientação da OpenAI sobre modelos](https://developers.openai.com/api/docs/guides/model-selection).
Sol será o padrão de implementação; Astra entra nos pontos com decisões
interligadas e na revisão final. Não é necessário usar esforço máximo em tudo.
Não haverá troca automática de modelo nem chamada paga de teste.

| Etapa | Entrega | Modelo e esforço |
|---|---|---|
| 1 | Contratos, permissões e prova do acesso Google | GPT-6 Astra · Alto (`high`) |
| 2 | Banco e cadastro isolado por servidor | GPT-6.1 Sol · Alto |
| 3 | Conectar Google, escolher e trocar arquivo | GPT-6.1 Sol · Alto |
| 4 | Leitura sob demanda e análise privada | GPT-6.1 Sol · Alto |
| 5 | Galeria e personalização no Discord | GPT-6.1 Sol · Alto |
| 6 | Carteira no navegador | GPT-6.1 Sol · Alto |
| 7 | Modelo do servidor e criação opcional | GPT-6 Astra · Alto para contrato; Sol · Alto para implementação |
| 8 | Edições autorizadas da ficha | GPT-6 Astra · Alto para contrato; Sol · Alto para implementação |
| 9 | Revisão integrada, carga e testes reais | GPT-6 Astra · Alto; Sol · Médio nos roteiros repetíveis |
| 10 | Clareza, documentação e publicação autorizada | GPT-6.1 Sol · Médio; Alto se houver correção de código |

As etapas são sequenciais; cada uma deve caber numa PR revisável. Dividir uma
etapa em PRs menores se necessário, mantendo funções incompletas desligadas.
Não abrir dez PRs vazias nem tratar aprovação do plano como autorização de deploy.

### 1. Fechar os contratos e provar o acesso

Mapear fontes atuais, campos públicos/privados, ações, retenção, vínculo de
contas e revisão da fonte. Definir hospedagem HTTPS da conexão/carteira e
responsável único pelo banco; o app atual é `TYPE=bot`, não uma hospedagem web
comprovada. Apresentar custo/recursos adicionais antes de contratar qualquer coisa.

Construir uma prova pequena em ambiente de teste: iniciar no Discord,
autenticar o mesmo usuário na página, selecionar uma planilha descartável,
ler uma faixa e reutilizar a conexão depois de reiniciar. Tratar cancelamento,
conta errada, arquivo sem permissão e revogação. Validar o caminho no celular
sem exigir senha/código no chat. Se OAuth público/domínio ainda faltar,
documentar exatamente essa dependência e concluir os contratos offline.

**Concluída quando:** contrato de dados/permissões aprovado tecnicamente,
fluxo viável demonstrado ou bloqueio externo delimitado sem falsa validação;
hospedagem, retenção e campos editáveis iniciais explicitamente definidos.
Não implementar edições nesta etapa.

**Ao terminar:** salvar decisões e evidência; indicar **etapa 2, Sol · Alto**.
Retomada: “Implemente a etapa 2 da Carteira viva a partir do contrato validado;
preserve os bloqueios externos registrados e não publique.”

### 2. Criar o cadastro e as permissões

Banco próprio, migrações, personagem estável, vários personagens por jogador,
permissões por servidor e separação entre consulta, revisão, gestão e edição.
Tratar duplicação, transferência, exclusão, desconexão e saída do servidor.
Criar auditoria mínima sem dados secretos, backup consistente e restauração.

**Concluída quando:** testes de isolamento e migração/restore passam; usuário
sem cargo não acessa ficha privada nem toma cadastro de outro. Nada do banco
de conversas é reaproveitado indevidamente ou perdido.

**Ao terminar:** salvar schema e resultados; indicar **etapa 3, Sol · Alto**.
Retomada: “Implemente a conexão Google da etapa 3 sobre o cadastro existente,
incluindo reconexão e troca de arquivo; teste somente com cópias fictícias.”

### 3. Conectar e trocar a ficha

Transformar a prova em fluxo completo: OAuth/Picker, vínculo Discord,
credenciais cifradas, renovação, erros claros e reconexão. Implementar troca
atômica de fonte, desconexão e proteção contra retornos antigos ou repetidos.

**Concluída quando:** selecionar, cancelar, reconectar e substituir funcionam;
perder permissão não derruba o bot; token/URL de outro usuário não transfere
cadastro; falha na troca conserva a fonte anterior. Teste de reinício concluído.

**Ao terminar:** registrar permissões Google realmente usadas; indicar
**etapa 4, Sol · Alto**. Retomada: “Implemente leitura sob demanda e análise
privada da etapa 4, reutilizando o leitor e o motor atuais.”

### 4. Ler sob demanda e analisar

Ler `ANALISE` por acesso autenticado, normalizar pelo contrato existente e
reaproveitar a leitura estável. Cache curto, fila, deduplicação de chamadas,
limite de tamanho e cancelamento. Separar resumo público de snapshot privado.
Análise sempre identifica arquivo/revisão, horário e campanha usada.

**Concluída quando:** mesmos dados produzem os mesmos achados pela nova leitura
e pelo caminho já validado; erros, fórmulas em transição, campos ausentes e
revogação não viram aprovação. Consulta repetida não vira várias leituras
simultâneas. Resultado e botão privado verificam permissões atuais.

**Ao terminar:** registrar comparação e consumo de chamadas; indicar
**etapa 5, Sol · Alto**. Retomada: “Implemente a galeria e os cartões da etapa 5,
sem tornar público o conteúdo reservado da análise.”

### 5. Montar a galeria no Discord

Implementar comandos, paginação, seleção, jogador responsável, prévia do
cartão e personalização. Texto e ações PT/EN, nomes intuitivos, limites de
caracteres e prevenção de menções involuntárias. Definir hospedagem/validade
das imagens e retenção. Mostrar horário da leitura, estado desatualizado e
botão para atualizar; não prometer edição eterna de mensagens antigas.

**Concluída quando:** duas contas exercitam galeria e análise com permissões
diferentes; vários personagens e listas vazias/grandes são legíveis; títulos,
cores e imagens não escondem erros nem dados de acesso restrito.

**Ao terminar:** salvar capturas sem dados reais; indicar **etapa 6, Sol · Alto**.
Retomada: “Implemente a Carteira no navegador da etapa 6 usando o mesmo serviço
e as mesmas permissões da galeria.”

### 6. Abrir a Carteira no navegador

Página responsiva com identificação Discord, cartão básico e área privada.
Bot e web usam a mesma autorização no servidor. Não expor URL Google privada,
tokens ou snapshot completo no HTML/JSON público. Exibir atualização e erros
de forma igual ao Discord. Revisar navegação no celular, contraste e teclado.

**Concluída quando:** alterar URL/ID, sair do servidor ou perder cargo não dá
acesso indevido; apresentação funciona em tela pequena; dados privados não
ficam em caches compartilhados. Encerrar sessão invalida a sessão da carteira.

**Ao terminar:** primeira entrega funcional de leitura pronta para ensaio,
**ainda não publicada**. Indicar **etapa 7, Astra · Alto**.
Retomada: “Valide o contrato de modelos da etapa 7 e depois implemente a cópia
opcional, sem modificar nenhum modelo oficial.”

### 7. Escolher o modelo do servidor

**26/10/2026: parcialmente implementada.** Escolha/configuração no Git,
criação bloqueada após herança de histórico e estado salarial nas três
cópias nativas. O critério abaixo continua pendente; não marcar concluída
nem iniciar escrita de jogo. Ver ETAPA-7.md e NATIVO-ETAPA-7.md.

Configuração administrativa com modelos oficiais como padrão e outro modelo
compatível como opção. Definir parâmetros suportados, distinguindo nível do
personagem, XP e regra de nível inicial da campanha. Confirmar cópia funcional,
acesso do jogador e automações exigidas; não copiar histórico, emissão ou
salário como se pertencessem ao novo personagem. Cadastro de ficha existente
continua independente desse fluxo.

**Concluída quando:** cópias descartáveis dos dois modelos oficiais e de um
modelo sintético do servidor preservam fórmulas/automação; incompatibilidade
é explicada; troca do modelo não altera personagens antigos. Se ativação
Google manual for indispensável, o passo deve aparecer claramente na interface.

**Ao terminar:** registrar requisitos do produtor; indicar **etapa 8, Astra · Alto**.
Retomada: “Defina e valide o contrato de edições da etapa 8 antes de implementar
escrita; não simule gatilhos da planilha por suposição.”

### 8. Editar operações permitidas

Escolher uma primeira lista pequena de operações comprováveis, com campos
identificados por contrato e versão, prévia, confirmação e registro do autor.
Uma boa candidata é um recurso atual sem efeitos adicionais, se o produtor
confirmar essa condição. Campos que alteram Classe, salário, XP, emissão ou
aprovação exigem contratos próprios, não entram por extensão automática.

Para cada operação: comparar estado esperado, validar permissão atual,
executar uma vez, verificar efeitos e reler. Tratar resultado incerto após
timeout sem repetir lançamento. Recuperação não pode desfazer uma edição
legítima que o jogador fez no Google no intervalo. Se precisar de produtor,
abrir PR separado e manter a função desligada até o ensaio nativo completo.

**Concluída quando:** cada operação liberada tem paridade com o comportamento
da ficha, teste de repetição/conflito/reinício e recuperação segura. Listar
operações não suportadas; nunca chamar isso de edição irrestrita da ficha.

**Ao terminar:** indicar **etapa 9, Astra · Alto**, passando implementação
para revisão crítica. Retomada: “Audite a entrega da Carteira viva, execute a
matriz de testes e registre problemas reais antes de preparar publicação.”

### 9. Revisar e testar o conjunto

Executar [a matriz](TESTES.md), revisar autorização em todas as rotas, medir
carga, perda de conexão e migração/restore. Exercitar no navegador lateral
o tópico de testes, verificando antes conta/servidor. Usar conta secundária
sem cargos e arquivos fictícios. Não expor dados reais para testar permissões.

**Concluída quando:** nenhum vazamento ou escrita incorreta conhecido; testes
obrigatórios passaram com evidência; limites de carga e bloqueios externos
estão documentados. Cenário não executado continua pendente, não aprovado.

**Ao terminar:** indicar **etapa 10, Sol · Médio**.
Retomada: “Revise textos, guias e entrega da etapa 10 usando os resultados
reais; prepare a publicação, mas não implante sem autorização específica.”

### 10. Revisar textos e preparar a publicação

Revisar nomes e mensagens PT/EN, ajuda/atalhos, privacidade, termos e roteiro
para o mestre. Informar consentimento, dados guardados, exclusão, leitura
antiga, limites do bot e quem pode ver/editar. Atualizar o conhecimento
operacional das guias sem inserir fichas privadas no contexto da conversa.

Preparar pacote, plano de migração/volta e backup restaurável, com credenciais
fora de commits e ZIP. Publicar só com autorização específica, sem reusar o
ok de rodadas anteriores. Validar fontes instalados, dados preservados e
comandos nativos depois da publicação. Commit documental não pede outro deploy.

**Concluída quando:** revisão, testes e publicação autorizada têm evidências
separadas. Sem autorização, a entrega fica “pronta para publicar”, não
“publicada”. Etapas 7/8 bloqueadas impedem declarar o escopo inteiro concluído;
uma primeira entrega só de leitura pode ser proposta explicitamente.

**Ao terminar:** registrar versão/commit/PR e pendências reais. Não trocar de
modelo nem começar outra ideia automaticamente. Sala de treino continua na fila.

## Fontes técnicas

- [Escopos Google Drive](https://developers.google.com/workspace/drive/api/guides/api-specific-auth): acesso por arquivo com `drive.file`.
- [Google Picker](https://developers.google.com/workspace/drive/picker/guides/overview): seleção de arquivo pelo usuário.
- [OAuth para aplicações web](https://developers.google.com/identity/protocols/oauth2/web-server): autorização e renovação.
- [Políticas OAuth](https://developers.google.com/identity/protocols/oauth2/policies): requisitos de autenticação e publicação.
- [Gatilhos simples](https://developers.google.com/apps-script/guides/triggers) e [instaláveis](https://developers.google.com/apps-script/guides/triggers/installable): escrita por API não dispara os gatilhos de edição.
- [Cópia de arquivo](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/copy): validar a cópia e sua inicialização.
- [Cotas Sheets](https://developers.google.com/workspace/sheets/api/limits): fila, limites e espera após `429`.
- [Quando usar SQLite](https://www.sqlite.org/whentouse.html): banco local e concorrência.
- [Escolha de modelos OpenAI](https://developers.openai.com/api/docs/guides/model-selection): base das recomendações de desenvolvimento.

Revalidar essas referências e as bases Git na etapa 1. Modelos, cotas e
configurações de hospedagem podem mudar; decisões locais não são medições.
