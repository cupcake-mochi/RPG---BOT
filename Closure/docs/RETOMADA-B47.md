# Retomada da integração do bot com B47 · 18/10/2026

Branch: `codex/integracao-b47`, em `cupcake-mochi/RPG---BOT`.
PR para revisão: https://github.com/cupcake-mochi/RPG---BOT/pull/64 (rascunho, sem merge/implantação).
Primeiro checkpoint publicado: `cfec482` (contrato/leitor). Os checkpoints
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
   `../.venv/bin/python -m unittest testes.test_b47_leitor testes.test_b47_integracao`.
   Depois de uma mudança relevante, executar
   `../.venv/bin/python -m unittest discover -s testes` e registrar os resultados.
4. Leitor/esquema: `ficha_leitor.py`, `ficha_esquema.py` e manifesto em recursos.
   Orquestração: `ficha_b47.py`; campanha: `ficha_configuracao.py`; custom:
   `ficha_custom.py`, `ficha_forma_custom.py` e motor puro internalizado.
   As contas antigas continuam em `ficha_*.py`.
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

Suíte completa: 694 testes, 693 aprovados e um online opcional pulado.
Regressões focais da revisão final: 68 aprovados. O pacote local foi inspecionado:
contratos/módulos B47 presentes; sem `.env` ou banco.

## O que permanece externo ou parcial

Não houve Google/Discord/LibreOffice nem implantação. O roteiro externo está
no fim de `INTEGRACAO-B47.md`. B47 não emite as 485 chaves exclusivas TR-v4;
carga integral e vários bônus do livro continuam explicitamente não conferidos.
Aprendizado/autorizações, histórico de escolhas, aplicações livres, efeitos de
alvos sem automação e interações especiais de Formas próprias não podem ser
certificados por descrições ou resultados exportados. Essa limitação deve
continuar visível, sem painel verde ou aprovação integral.

Nenhum defeito confirmado da ficha deve ser escondido tornando o bot permissivo.
Se houver nova divergência, registrar chave, entradas sintéticas, resultado
esperado por regra, resultado emitido e reprodução separada, sem editar a oficial.

Para revisão mecânica seguinte, modelo Sol com esforço alto é uma opção adequada
às interações entre contratos e aprovações; isso não altera configuração de modelo.
