# Retomada da integração do bot com B47 · 18/10/2026

**Publicação e checagem concluídas · 18/10:** o usuário autorizou aplicar na
Discloud. O código `40d32a7` da PR 65 está instalado no app existente e online
em cinco servidores desde 15:23:32 (Brasília), com 1.000 MB mantidos. Backup
antes/depois: 67 arquivos iguais ao ZIP; variáveis, dois bancos e cadastro de
campanha idênticos, integridade dos bancos ok e quatro aprovações preservadas.
PR 65 permanece aberta, sem novo merge; `main` ainda contém a PR 64.

**Três testes após implantação passaram, com dez páginas conferidas:** ficha
com Vida 999/23 por link, custom aprovada por XLSX e recusa de fórmula sem
cache. Vermelho na página de erro, verde nos valores corretos e amarelo nos
limites; resumo e rodapé conservam o veredito geral. Quatro setas e seletor
funcionaram. Evidência: `pesquisa/validacao/2026-10-18-b47-cores-publicacao/`.
Somadas às rodadas anteriores, são 44 análises reais (13 + 28 + 3), sem
chamadas pagas nestes ensaios. A rodada avançada anterior conferiu 143
páginas de casos técnicos do consumidor, sem novo recálculo nativo; evidências
em `pesquisa/validacao/2026-10-18-b47-avancados/`. A suíte continua **822
executados, 821 aprovados e um opcional pulado**, além de **26/26 no ZIP**;
não foi repetida sem mudança de código. SHA256 do pacote instalado:
`8a210c5aa82bf54a5b8af56486123e0b0199d1d09314b71cf2067b20aab54e40`.

**Fechamento desta etapa:** publicação autorizada e smoke test concluídos.
Para novo trabalho, retomar `origin/codex/integracao-b47` e conferir árvore,
remoto e PR 65 antes de editar; não refazer deploy/baterias por rotina. Ficam
separados revisão/merge no Git, segunda pessoa no painel, recálculos nativos
ampliados e os limites do produtor/mestre. A oficial foi preservada. Os
registros seguintes são históricos; não indicam o runtime atual.

**Bateria nativa preparada em 18/10:** seis cópias sintéticas calculadas no
Sheets, 8.190 chaves por XLSX e resultados locais conferidos. Roteiro em
`../dados/ficha/BATERIA-NATIVA-B47.md`. Inclui aprovação exata, MESTRE VIU sem autorização,
efeito alterado, resultado adulterado e campanha não autorizada. Encontrado
e corrigido no código o falso cadastro de Caminho/Trilha pelos menus default
de cartões vazios; **817 testes: 816 aprovados e um opcional pulado**. Esse
patch ainda não foi implantado. As cópias limpam esses menus não usados para
permitir o teste também no runtime anterior. Com autorização posterior do
Mizuki, seis cópias receberam leitura por link e quatro hashes sintéticos
foram instalados somente no servidor escolhido. Cadastro ativo relido e
conferido; sem mudar regras gerais, reiniciar ou implantar código. Os seis
links anônimos coincidem com os XLSX nas 8.190 chaves.

**Discord executado com autorização em 18/10:** 13 análises reais na versão
já publicada: seis links, seis XLSX e uma reanálise. Os seis pares devolveram
resumos idênticos: casos 01/02 sem divergências nem aprovação pendente; 03 com
quatro aprovações pendentes apesar de MESTRE VIU; 04 reabriu somente o efeito
alterado; 05 reprovou Vida 999/23; 06 reprovou a regra/total não autorizados.
As seis páginas da 02, quatro setas e seletor foram exercitados. Encerramento
após dez minutos e reabertura por nova análise foram observados. Sem chamadas
pagas, reinício, implantação do patch 65 ou alteração da oficial nesta rodada.
Evidências da primeira rodada: `pesquisa/validacao/2026-10-18-b47-discord/`.
A continuação avançada está registrada acima; segunda pessoa e validação
nativa ampliada continuam pendentes. Produtor e mestre limitam a aprovação integral.

Branch: `codex/integracao-b47`, em `cupcake-mochi/RPG---BOT`.
PR de correção: https://github.com/cupcake-mochi/RPG---BOT/pull/65 (aberta; código 40d32a7 implantado, merge pendente).
PR 64: mesclada; publicação autorizada concluída.
Primeiro checkpoint publicado: `cfec482` (contrato/leitor). Continuação do
usuário: completar conferências possíveis e testar tudo ao final. Os checkpoints
seguintes desta branch contêm implementação, regressões e documentação.
Use `git log -5 --oneline` e `git rev-parse HEAD` para identificar a entrega
atual sem depender de outro chat. Não criar worktree, resetar ou usar force-push.

Bases fixadas e escopo completo em
[`../dados/ficha/INTEGRACAO-B47.md`](../dados/ficha/INTEGRACAO-B47.md).
Ficha: `ccbd053c8f7e68f8b4ac223f721b309111d2dcc0`.
Sistema: `e593ba8cf24ce6bbd2f517f5431a73a96610e02b`.
Bot inicial: `7e4dc35209ea840549d5ccf5a0b49834da21d117`.

## Publicação anterior · PR 64 · 18/10

**Publicação autorizada em 18/10:** PR 64 mesclada em
`1997f25fe990eb307204365cda172aeec831969f` e ZIP implantado na Discloud.
Bot online em cinco servidores. Backup antes/depois: 67 arquivos instalados
idênticos ao ZIP; `.env` e dois bancos preservados byte a byte, integridade ok.
Memória de 1.000 MB mantida. Nessa publicação inicial o cadastro B47 de campanha
ainda não existia; posteriormente foram instaladas apenas as aprovações
sintéticas autorizadas. A bateria real por link/XLSX e navegação descrita
acima passou nessa versão; não publica o patch 65. Evidências da implantação em
`pesquisa/validacao/2026-10-18-b47-publicacao/`. A ficha oficial foi preservada.

Retomar de `origin/codex/integracao-b47`, após conferir remotos e árvore local.
`main` contém a publicação da PR 64; a PR 65 acrescenta correção dos cartões
vazios, cores locais por página, responsividade e registro dos testes. Não refazer merge/deploy da PR 64 nem presumir
publicação do patch 65. Próximo passo: revisão da PR 65; merge/implantação
continuam separados desta bateria. Para ampliar o piloto, usar o roteiro externo:
segunda pessoa e os recálculos nativos ainda não executados, sem modelos pagos. Campanha de
jogo e novas aprovações dependem de decisão real do mestre. Retomada exata:
conferir `git status --short --branch`, `git fetch origin` e a PR 65; ler esta
retomada e `dados/ficha/ROTEIRO-EXTERNO-B47.md`. Preservar os seis casos aprovados
como evidência, sem repetir a bateria ou a publicação por rotina.
Backups privados ficam fora do Git; não anexar seus arquivos à PR.

## Checkpoint de código · Máxima e teto de dano · 18/10

Checkpoint de código: `a981416a7d8af1879ed5c95f8d41eb424f2176b0`.
A Máxima confere `maxima.montagem`, dependências aprovadas, identidade das
peças e combinações; montagem inválida não certifica dados dependentes.
Toca a Alma simples confere metade da tabela, conservando permissão humana.
A fórmula fixa conhecida do produtor recebe pendência, nunca aprovação.
Quebra Coisa entra no teto de dano comum/custom/Liberação/entidade, sem
multiplicar dados secundários ou aplicar Remate ao mesmo objeto.

Suíte desse checkpoint: **814 executados, 813 aprovados e um online opcional pulado**,
em 208,229 s. Dezessete regressões novas passaram também no ZIP; contra
`89d56db`, produziram 26 falhas de asserção/subcasos e nenhum erro de execução.
Evidências: `pesquisa/validacao/2026-10-18-b47-maxima/`.
Pacote local: 67 arquivos iguais aos fontes, 1.151.110 bytes, sem credenciais,
banco ou cadastro real. SHA256:
`3d35f83e6ea31f30b4fec9d6487a0fc9e9aa392549c66e72fcc79f6b705d2c75`.

No checkpoint acima, a PR 64 ainda era rascunho e não havia autorização de
publicação. O usuário autorizou merge/implantação depois; envio de mensagens
no Discord continua separado.
O roteiro externo foi ampliado para esses casos. O produtor permanece
inalterado: quatro defeitos estáticos têm reprodução separada. Seletores,
competências, inventário/carga, TR e estado ativo ausentes continuam sem
certificação; histórico, permissões, narrativa, distribuição e interações de
Alma não automatizadas dependem do mestre. A suíte não encerra essas etapas.

## Checkpoint anterior · 89d56db · 18/10

Remotos conferidos: os três projetos mantêm as bases indicadas acima. Retomada
de `7015c80`, preservando a branch e a PR 64. Checkpoints de código publicados:
`881e6da` (Trilha/troca/especialização) e `2da707f` (CSV/regressão portátil).

- A BASE DO LIVRO da Trilha custom é validada, incluída na assinatura e usada
  no perfil das Famílias e nas escolhas extras da Principal. Preserva o nome
  literal e o Caminho associado; o produtor permite base de outro Caminho.
  Sem aprovação/base válida, não presume o perfil padrão. A herança se limita
  às automações publicadas; prosa não concede novos números. Nenhuma/vazio não herdam.
- Trocar por fixa o resultado mesmo quando a conta-base está incompleta,
  mantendo pendências das entradas e da aprovação. Conflitos/entrada inválida
  continuam bloqueando a caixa. Especialização inválida não certifica bônus
  nem seu orçamento de treinos.
- Leitura real encontrou gviz inferindo milhares de registros como cabeçalho
  (campo maior que 131.072 caracteres). A requisição usa `headers=1`, conforme
  o contrato; limites de tamanho/parser preservados. Regressão com resposta
  simulada e teste online opcional atualizado para a B47 atual.
- Leitura pública real da oficial: CSV e XLSX com 8.190 chaves, zero diferenças
  de Campo e mesmo Resultado. Foi somente GET; nenhuma escrita, alteração de
  acesso, importação ou execução de Apps Script. Não é validação de campanha
  real, casos preenchidos ou das fórmulas defeituosas do produtor.
- Proposta de novos campos/semântica/testes em
  `dados/ficha/PROPOSTA-CONTRATO-B47.md`; roteiro de operador em
  `dados/ficha/ROTEIRO-EXTERNO-B47.md`. Nenhuma ampliação do produtor aplicada.

Evidências desta continuação: `pesquisa/validacao/2026-10-18-b47-cobertura/`.
Suíte final: **797 testes executados, 796 aprovados e um online opcional
pulado**, em 182,286 s. Teste online executado separadamente e aprovado.
Pacote final: 67 arquivos, 1.150.030 bytes, todos iguais aos fontes, sem dados
operacionais; SHA256 `3ff568f2773bc631d2564919628ec7d67deb27c5cba62f6a14d4bbc193312a1d`.
Esse resultado inclui a guarda final das Trilhas publicadas incompatíveis.
Detalhes/reprodução em `relatorio.txt`, `verificacao.json` e `pacote.json`.

## Como continuar exatamente

1. Usar o checkout da branch, sem depender do caminho do computador/nuvem. Conferir `git status
   --short --branch`, `git log -5 --oneline` e alterações remotas antes de editar.
   Preservar trabalho do usuário. Se a branch já existir, retomá-la sem recriar.
2. Ler `INTEGRACAO-B47.md`, `CONTRATO-ABA-BOT.md` e a fila atual. A entrega da
   ficha está concluída: não retomar C/D, não repetir migrações e não usar
   endereços de documentos históricos como contrato.
3. De `Closure/src/`, executar:
   `../.venv/bin/python -m unittest testes.test_b47_leitor testes.test_b47_integracao testes.test_b47_derivados testes.test_b47_revisao testes.test_b47_cobertura testes.test_b47_maxima testes.test_b47_teto testes.test_ficha_painel testes.test_ficha_analise_v4`.
   Depois de uma mudança relevante, executar
   `../.venv/bin/python -m unittest discover -s testes` e registrar os resultados.
4. Leitor/esquema: `ficha_leitor.py`, `ficha_esquema.py` e manifesto em recursos.
   Orquestração: `ficha_b47.py`; campanha: `ficha_configuracao.py`; custom:
   `ficha_custom.py`, `ficha_forma_custom.py` e motor puro internalizado.
   `ficha_derivados_b47.py` separa contas derivadas completas, contradições e
   seletores ausentes. As contas antigas continuam em `ficha_*.py`.
5. Cadastro por servidor: `Closure/src/var/ficha-campanhas.json`, ignorado pelo
   Git. Use `ferramentas/ficha_campanha.py --help` como operador autorizado.
   Não versionar definições/fichas privadas ou estado real. Aprovar um hash não
   corrige definição inválida; alterar conteúdo/base exige nova aprovação.
6. De `Closure/`, ` .venv/bin/python ferramentas/empacotar.py` produz ZIP local
   sem `.env`. Conferir presença dos contratos/JSON B47. Não enviar à Discloud
   nem reiniciar produção sem autorização específica.
7. Commitar/push em checkpoints, sem reescrever a branch. Preparar/revisar PR
   contra `main`; verificar se já existe antes de criar outra. A API GitHub
   chegou a ser bloqueada pela rede da nuvem; a liberação de `api.github.com`
   foi salva nas configurações, preservando os hosts anteriores. Verificar o
   resultado real de `gh pr list` antes de presumir bloqueio persistente.

## Evidência do checkpoint anterior · 7015c80

Suíte completa registrada naquele checkpoint: **784 testes executados, 783 aprovados
e um online opcional pulado**, em 108,989 s. Comando: de `Closure/src/`,
`../.venv/bin/python -m unittest discover -s testes`. A suíte inclui legado,
leitor, integração, campanha, custom, painel e demais funcionalidades do projeto.
As 12 regressões desta continuação cobrem requisitos de Origem, efeitos que
interrompiam CD/ataques e CSV malformado/excessivo. Os quatro módulos B47
passaram com 139 testes antes dos dois novos casos de leitura; os oito testes
do leitor passaram após essa alteração. Tudo está incluído na suíte completa.
Sem chamadas reais a modelos. PR conferida sem comentários/revisões pendentes.

Primeiro fechamento: 694 testes (693 + um opcional). As revisões anteriores
passaram com 733, 737, 742 e 772 testes; a entrega final acima inclui todas as
mudanças posteriores, sem reutilizar um resultado anterior como validação final.

Pacote local regenerado: `Closure/src/var/closure-lab.zip` (ignorado pelo Git),
67 arquivos, cerca de 1122 KB. Os 59 fontes/recursos Python/JSON/TSV correspondem
exatamente ao checkout final; sem `.env`, banco ou cadastro real da campanha.
SHA256 histórico: `13eefb60a0922d53ae54a4260c15544de9419b018f77a80c585cf7a3f2bcdcf3`.
O pacote dessa continuação foi regenerado; consultar o relatório atual acima.
O operador deve preservar o cadastro de campanha existente ao publicar; ele
não faz parte do ZIP. Não houve envio à Discloud.

## Continuação implementada

- Menores publicadas conferem a marcante exigida (modalidade/clã) pelo catálogo,
  nas duas vagas, Sem Técnica e Origem custom com base. Marcante vazia é
  informação insuficiente; incompatibilidade bloqueia contas da Origem.
- Efeito inválido/duplicado em CD/ataques não interrompe análise nem permite
  certificar o alvo; contas independentes continuam. CSV truncado/excessivo
  recebe erro de leitura, preservando aspas/quebras de linha válidas.

- Iniciativa, Maestria/Classe/Refino/Classes 0 gratuitas e Sequelas/Morrendo.
- CD/ataques: troca numérica, divergências impossíveis e seletor ausente
  separados. Deslocamento: Exaustão, possibilidades de penalidade e troca final.
- Dois TR pessoais e escolha/atributo físico de TR de cada entidade.
- Efeito de Famílias aplicado antes da autonomia; inteiros e nove vagas.
- Efeito inválido ou literalmente duplicado não certifica o alvo.
- Origem aprovada com base usa seu pacote e rota compatível nas contas; Menor
  respeita a Marcante exigida. Origem sem base não herda capacidades publicadas.
- Formas apenas renomeadas usam a base; Formas estruturadas conferem Liberação,
  Remate, adicionais, totais de Rajada/distribuição e Alma simples, além da
  resolução numérica da entidade. Incompatibilidades impedem certificação.
- Desconto da Forma Livre pessoal corrigido. Ferramenta vincula aprovação à
  base (também item comum), herda Proteção/mãos e aceita Volume zero explícito.
- Reserva Profunda herdada conserva ganho; efeito identificado não duplica esse
  ganho e Buff ambíguo permanece pendente.
- Restrição custom embutida validada, aprovada separadamente e vinculada à
  assinatura da Forma. Mudanças invalidam as aprovações dependentes.
  A Forma também não substitui a aprovação da Família custom que utiliza.
- Condicional preserva frequência herdada mesmo com sufixo de peso; Não
  explícito continua sobrescrevendo. Restrição embutida conta em frequência e
  repetição. Tudo ou Nada considera TR de Melhoria estruturada, sem ler prosa.
- Condições Pesadas obedecem ao limite por modalidade/identidade, inclusive
  aliases. Melhoria de Controle não vira Condição somente pelo seu peso.
- Distribuição incompleta/contraditória da entidade bloqueia contas dependentes,
  sem bloquear a entidade seguinte; Classe inválida bloqueia o motor custom.
- CD exclusiva do Controle confere saldo independente quando disponível,
  preserva Precisão herdada e não concede +2 só por exigir TR ou descartar dano.
  A fórmula entregue sem o +2 obrigatório recebe pendência precisa.

## O que permanece externo ou parcial

No checkpoint histórico acima houve leitura pública CSV/XLSX no Google, sem
escrita, e não houve Discord, LibreOffice ou implantação. As baterias reais
posteriores e a publicação vigente estão descritas no início deste documento. O roteiro externo está
no fim de `INTEGRACAO-B47.md`. B47 não emite as 485 chaves exclusivas TR-v4;
carga integral e vários bônus do livro continuam explicitamente não conferidos.
Seletores pessoais de CD/ataques, ajustes/resultados de TR/perícias do livro,
inventário completo e teto/estado de entidades ativas não foram exportados.
Aprendizado/autorizações, histórico de escolhas, aplicações livres, composição
de Alma com adicionais/distribuição e resoluções sem saldo comprovado ainda
exigem revisão. Essa limitação deve continuar visível, sem aprovação integral.
Lacunas e reproduções estáticas de critério de curinga e CD de Controle estão em
`dados/ficha/LACUNAS-PRODUTOR-B47.md`; somente uma entrega futura do produtor
poderá completar a exportação/corrigir sua fórmula. Não editar a oficial.

Nenhum defeito confirmado da ficha deve ser escondido tornando o bot permissivo.
Se houver nova divergência, registrar chave, entradas sintéticas, resultado
esperado por regra, resultado emitido e reprodução separada, sem editar a oficial.

Para revisão mecânica seguinte, modelo Sol com esforço alto é uma opção adequada
às interações entre contratos e aprovações; isso não altera configuração de modelo.
