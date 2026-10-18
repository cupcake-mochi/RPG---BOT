# Retomada da integração do bot com B47 · 18/10/2026

Branch: `codex/integracao-b47`, em `cupcake-mochi/RPG---BOT`.
PR para revisão: https://github.com/cupcake-mochi/RPG---BOT/pull/64 (rascunho, sem merge/implantação).
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

## Como continuar exatamente

1. Usar o checkout existente em `/workspace/RPG---BOT`. Conferir `git status
   --short --branch`, `git log -5 --oneline` e alterações remotas antes de editar.
   Preservar trabalho do usuário. Se a branch já existir, retomá-la sem recriar.
2. Ler `INTEGRACAO-B47.md`, `CONTRATO-ABA-BOT.md` e a fila atual. A entrega da
   ficha está concluída: não retomar C/D, não repetir migrações e não usar
   endereços de documentos históricos como contrato.
3. De `Closure/src/`, executar:
   `../.venv/bin/python -m unittest testes.test_b47_leitor testes.test_b47_integracao testes.test_b47_derivados testes.test_b47_revisao`.
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

## Evidência já obtida

Suíte completa final desta revisão: **784 testes executados, 783 aprovados
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
SHA256: `13eefb60a0922d53ae54a4260c15544de9419b018f77a80c585cf7a3f2bcdcf3`.
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

Não houve Google/Discord/LibreOffice nem implantação. O roteiro externo está
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
