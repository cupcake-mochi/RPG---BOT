# Continuar a Carteira viva · 30/10/2026

Sem credenciais nem dados de jogadores. Substitui o
[prompt de 29/10](CONTINUAR-NO-CLAUDE-2026-10-29.md) como ponto de partida; aquele segue
valendo para limites, caminhos e histórico.

## Onde está

- Repositório: https://github.com/cupcake-mochi/RPG---BOT · branch `codex/carteira-viva-etapa-7`
  · PR84 em rascunho (base `codex/carteira-viva-etapa-6`/PR83). Sem merge nem deploy.
- Cópia local: `/home/mizuki/.codex/tmp/carteira-etapa7-linux`. Testes a partir de `Closure/src`:
  `../.venv/bin/python -m unittest discover -s testes` (~10 min).
- Último código: `583a95b` (CI rodando ao fechar; `5f64c84` e `c2a4b27` passaram).
- Pilotos privados fora do Git em `~/.local/share/guias-ciclo/carteira-piloto/` (pastas 700,
  arquivos 600). Todos encerrados; nenhum grant ativo, porta 8876 livre.

## O que foi feito em 29–30/10

1. Revisão da coleta agrupada; `_json` deixa de vazar `RecursionError` (regressão).
2. Ensaios nativos (fontes descartáveis, limpos e revogados):
   - progressão agrupada: 8/8 duas vezes, zero diferenças, 6 GETs Sheets (antes 18);
   - financeiro individual × agrupado: 25/25, zero diferenças, 11 GETs contra 25.
3. Lotes ligados no serviço: diagnóstico, medição financeira e auditoria.
4. Experimento de versões do Drive: o Google sobe `version` sem mudar `modifiedTime`
   (cópia 8→9 em < 30 s; fonte 13→14 minutos depois) e o `files.copy` passa de 15 s.
   Explica as recusas de 28/10. [Relatório](NATIVO-VERSOES-DRIVE-2026-10-29.md).
5. `files.copy` espera até 120 s; job da cópia com 300 s na fila.
6. **Versões equivalentes** (aprovado pelo mantenedor, implementado offline): versão nova só com
   `modifiedTime` idêntico e impressão de conteúdo igual (hash `conteudo` da medição). Leitura
   segue estrita. [Desenho e implementação](VERSOES-EQUIVALENTES-PROPOSTA.md).

## Próximo passo

Ensaio nativo da **escrita financeira** em cópia descartável, com o código `583a95b` ou posterior:
cópia pelo bot (`copiar_modelo`), identificação com as impressões, `inicializar_financeiro_celulas`
com um único POST Sheets, e, se planejado, perda de resposta com reconciliação sem segundo POST.
Depois: limpar (lixeira recuperável, revogar, base vazia) e registrar.

Antes do ensaio: conferir o CI de `583a95b`; montar o kit a partir de
`carteira-piloto/etapa7-financeiro-agrupado-20261029` (runner com PID/batimento, registro por
chamada, limpeza), **liberando apenas os POSTs necessários** (Drive copy e Sheets batchUpdate só na
cópia criada) e **gravando o marcador antes de qualquer POST** (falha do experimento de 30/10).

## Como os ensaios funcionaram (lições)

- A fonte descartável precisa ser da **mesma conta Google do consentimento** (hoje
  gustavohmoura12, dona da oficial). Copiar pelo "Fazer uma cópia" do Sheets no navegador do app.
- O navegador do app perde login entre sessões: Discord e Google precisam de login da pessoa.
- O aviso "O Google não verificou este app" é **sempre da pessoa**. Autorizar Discord, escolher a
  conta, o Picker e o cadastro fictício podem ser feitos pelo assistente com a permissão já dada.
- Cópia recém-criada pode mudar de versão nos primeiros minutos; recusas por isso são corretas
  quando a operação não tem referência de conteúdo.
- O limite local de cotas (45/min) faz cada impressão esperar; não aumentar cota para acelerar.

## Pendente

Escrita financeira nativa e reconciliação; propriedades Apps Script; concorrência com o dono
(sem CAS); preparada × versão configurada e `validar_modelo` com versões equivalentes; demais
domínios, preservação, automações, prova integral; etapas 8–10. Criação de personagem
**bloqueada**; quatro indicadores falsos. Sem merge/deploy, modelo pago, escopo novo, Gateway,
edição de oficial/jogador/produtor. Commits sem coautoria do assistente.
