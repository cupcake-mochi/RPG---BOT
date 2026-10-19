# Integração R53 no bot · 19/10/2026

**Estado:** código na branch `claude/project-thread-zzfh12` (derivada de
`codex/mundo-era-revolucao`, PR 66), em PR rascunho. **Não implantado.** A
oficial `1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro` foi só lida (ANALISE,
poucas linhas: cabeçalho, esquemas, feitiço 1 vazio e `controle_compat`);
nenhuma célula, fórmula, código, permissão ou aparência foi tocada, e nada de
`construir()`/`continuar()`, migração ou importação de Office.

Fonte do contrato: `cupcake-mochi/Ficha---RPG-JJK@4b22da5` (PR 4,
`codex/publicacao-r53`). O manifesto foi derivado dos `.gs` gerados nesse
commit, porque o `docs.google.com` está bloqueado no contêiner.

## O que muda na leitura

| Área | B47 (formato 11) | R53 (formato 12) |
|---|---|---|
| Versão | `variante` → `b47-v11` | `variante` → `r53-v12`; exige `r53.montagem.esquema=2` e os esquemas `r53.entrada.campos`/`r53.versao.campos` |
| Chaves | 8.190 | 18.393 (+ cabeçalho = 18.394): as 8.190 da B47 com a mesma `parte`, +30 `custom.melhoria.N.controle_compat`, +10.173 `r53.*` de 249 cartões (`src/closure_bot/recursos/r53-campos-novos.tsv`) |
| Cartões | montagens B47 (`feitico.N.pecas`, `erros/avisos`) | `r53.<id>.entrada` + `versao.<classe>`/`versao.maxima`, recalculados pelo modelo R53 vendorizado (`src/closure_bot/r53/`, sha conferido nos testes) com `registro_livre=True` |
| Avisos B47 dos cartões | reprovam | ignorados no formato 12 (apontam para células velhas) |
| Melhoria/Restrição custom | base no catálogo B47 | base no catálogo R53 (`Condição · Cego`, `Fraqueza · TR Físico`...) |

Os arrays JSON são lidos pelo esquema exportado; booleanos, inteiros e textos
são conferidos pelo tipo, sem conversão. Esquema ausente ou desconhecido não
certifica nenhum cartão.

## Validação dos cartões

- Recalcula orçamento, saldo, dados, PE, CDs, função e avisos e compara com o
  exportado; diferença numérica ou de aviso é erro de conta.
- `VÁLIDO/REVISAR` aparece como estado mecânico da ficha, nunca como aprovação
  do mestre ou do bot.
- Destinatário, permissão, resolução e TR vazios/padrão não reprovam e não
  contam como autorização narrativa. COMO É fica com o mestre.
- Avisos de cadastro próprio e de migração (`Registro antigo exige revisão`)
  viram pendência de aprovação; Toca a Alma também. Frágil vira nota.
- Peça ou Forma própria: precisa existir no cadastro e estar aprovada. O bot
  não recalcula esses cartões (usa os avisos da ficha e lista em "sem recálculo").

## Troca de classe (assíncrona)

Um cartão está em transição quando o registro ainda mostra `#`/`Loading`, a
Classe ativa ainda não tem versão salva, o cartão visível difere da versão
salva ou os espelhos não alcançaram o JSON. Nesse caso:

- o bot relê o link até 3 vezes (espera de 3 s e 6 s) e fica com a leitura mais
  recente com menos cartões em transição, sem misturar leituras;
- se continuar, o cartão vira pendência informativa com a última versão salva,
  sem aprovar, reprovar ou descartar nada;
- JSON quebrado não é transição: é erro de formato.

O "último registro consistente" é a versão preparada que a própria ficha
guarda. **Decisão a confirmar:** o bot não grava conteúdo de ficha entre
análises, porque a `docs/PRIVACIDADE.md` não cobre esse armazenamento.

## Aprovações e migração

- Hash das aprovações igual ao da B47. `controle_compat` desmarcado não entra
  no hash, então as aprovações já existentes continuam valendo. Marcado, pede
  aprovação nova.
- Melhoria/Restrição custom aprovada na B47 com base que mudou de nome na R53
  muda de hash e pede aprovação nova (as bases antigas saíram do catálogo).
- `ferramentas/ficha_campanha.py` aceita o formato 12 e gera a mesma impressão
  que o bot confere (teste `test_cli_do_mestre_aprova_a_mesma_impressao_que_o_bot_confere`).
- Fichas B47 (formato 11) seguem pelo caminho antigo, sem mudança.

## Painel

Cartões R53 entram na página de feitiços com rótulos legíveis (Feitiço N,
Liberação N, Classe 0 N, Técnica Máxima, Invocação N · básica/especial/
habilidade da Trilha/Liberação/Técnica Máxima). Não há comando de rolagem no
bot, então nada mudou nisso.

## Fora deste trabalho

- Perguntas sobre o livro continuam no índice R51/R52.
- Leitura completa de uma ficha R53 preenchida de verdade pelo bot (o link
  depende do `docs.google.com`, bloqueado aqui) e bateria no Discord.
- Implantação na Discloud: só com pedido do Mizuki.

## Testes

`src/testes/test_r53.py` (33): cópia idêntica do núcleo, 89 casos do autor
(os mesmos verificados no Google), manifesto, cartões, transição, custom,
CLI do mestre, painel e releitura. Suíte completa: ver PR.
