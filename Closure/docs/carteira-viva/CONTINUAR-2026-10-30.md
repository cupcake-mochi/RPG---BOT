# Continuar a Carteira viva · 30/10/2026

Sem credenciais nem dados de jogadores. Substitui o
[prompt de 29/10](CONTINUAR-NO-CLAUDE-2026-10-29.md) como ponto de partida; aquele segue
valendo para limites, caminhos e histórico.

## Onde está

- Repositório: https://github.com/cupcake-mochi/RPG---BOT · branch `codex/carteira-viva-etapa-7`
  · PR84 em rascunho (base `codex/carteira-viva-etapa-6`/PR83). Sem merge nem deploy.
- Cópia local: `/home/mizuki/.codex/tmp/carteira-etapa7-linux`. Testes a partir de `Closure/src`:
  `../.venv/bin/python -m unittest discover -s testes` (~10 min).
- Último código: `583a95b`; CI 41055294614 aprovado: 1.639 executados/1.638 aprovados/um opcional, zero falhas, 293,752 s (30/10 às 09:31:16 Brasília). O fechamento seguinte é só documental.
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

## Marco nativo fechado · 30/10

[Escrita financeira e recuperação](NATIVO-ESCRITA-EQUIVALENTE-2026-10-30.md):
cópia pelo bot e identificação com impressões, um POST Drive200 e um POST Sheets200.
A resposta financeira foi descartada de propósito; processo novo reconciliou por
leitura, sem segundo POST. Células conferidas e recibos intactos. Duas passagens
anteriores de cópia recusaram versão alterada; retomada da mesma operação, sem
outro envio ao Drive e sem mudar G5. Nenhuma equivalência extra registrada 0/0:
este caminho específico continua com prova offline, sem alegação de prova nativa.

Sentinela fictícia preservada na fonte e limpa na cópia, verificada por leitura
independente. Limpeza às 09:55:09 Brasília: ambas na lixeira recuperável, autorização
revogada, recusa sem Drive/Sheets, base vazia/íntegra, porta livre e abas próprias
fechadas. Kit e relatórios privados em `carteira-piloto/etapa7-escrita-equivalente-20261030`;
credenciais fora do Git. Não reutilizar grant ou restaurar descartáveis.

## Próximo passo

Não repetir o ensaio financeiro encerrado por rotina. Fechar a solução/contrato das
cinco propriedades Apps Script e da concorrência com o dono; depois os demais
domínios de inicialização, preservação/automações e prova integral da 7C/7D.
Se exigir produtor, escopos ou ativação manual, explicitar a dependência antes de
implementar. Não ampliar permissões ou liberar criação por suposição.

O kit comprovou registro durável antes dos POSTs de negócio e capacidade consumida
mesmo após reinício. Uma nova hipótese nativa deve usar base/chave/token de serviço,
fonte e autorização novos, só quando houver motivo; login/aviso continuam com a pessoa.

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

Registro nativo das equivalências extras ainda não exercitado; propriedades Apps Script; concorrência com o dono
(sem CAS); preparada × versão configurada e `validar_modelo` com versões equivalentes; demais
domínios, preservação, automações, prova integral; etapas 8–10. Criação de personagem
**bloqueada**; quatro indicadores falsos. Sem merge/deploy, modelo pago, escopo novo, Gateway,
edição de oficial/jogador/produtor. Commits sem coautoria do assistente.
