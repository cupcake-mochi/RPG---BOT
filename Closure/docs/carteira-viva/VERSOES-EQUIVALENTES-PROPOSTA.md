# Proposta: versão nova do Drive sem edição

30/10/2026 · PR 84 · **desenho para aprovação; nada implementado além do prazo da cópia.**
Base: [experimento nativo](NATIVO-VERSOES-DRIVE-2026-10-29.md) — o Google sobe `version` sem
mudar `modifiedTime` (cópia 8→9 em < 30 s; fonte 13→14 minutos depois).

## Onde as guardas recusariam um fluxo normal

| # | Ponto | Hoje | Efeito observado |
|---|---|---|---|
| G1 | `copias_servico.conferir_origem` (antes/depois da candidata) | versão da origem ≠ fixada ⇒ recusa | fonte sobe minutos depois |
| G2 | `financeiro_servico.origem()` | idem, no início e no fim do financeiro | idem, com mais tempo decorrido |
| G3 | candidata × observação final; `registrar_candidata/destino_copia` | qualquer diferença ⇒ recusa, "não altere sua versão" | cópia sobe em < 30 s |
| G4 | `financeiro_servico`: destino × `versao_destino` antes de preparar | ≠ ⇒ recusa | cópia identificada sobe depois |
| G5 | `LeitorGradeRest._versao` antes/depois de cada GET | ≠ ⇒ `VersaoAlterada` | qualquer subida durante a leitura |
| G6 | armar/fechamento após a escrita | compara com a observação feita ali | esperado mudar com a escrita |

## Regra proposta: equivalência provada, nunca adotada

Uma versão `v2` diferente da referência `v1` do mesmo arquivo só é aceita quando **as duas**
condições valem, conferidas na mesma rodada:

1. `modifiedTime` em `v2` é **idêntico** ao registrado junto com `v1`. Qualquer diferença ⇒ recusa
   como hoje (edição de alguém, inclusive Apps Script).
2. **Impressão de conteúdo** igual: hash SHA-256 das páginas do contrato financeiro (as mesmas
   faixas do `medir`, lidas em lotes, ~11 GETs) em `v2` igual à impressão gravada para `v1`.

Aceita, a equivalência é **gravada à parte** no envelope cifrado (`equivalencias`: até 8 pares
`{versao, modificado, impressao}` por arquivo), sem tocar `versao_origem`/`versao_destino`, que
continuam imutáveis. As guardas passam a aceitar a versão de referência **ou** uma versão já
provada equivalente. A prova nunca é herdada de outro arquivo, operação ou conta.

Por ponto:
- **Origem (G1, G2):** impressão gravada junto com `fixar_versao_copia`, antes do POST.
- **Candidata (G3):** impressão gravada junto com `registrar_candidata_copia`; a identificação
  aceita a versão final equivalente. A cópia nunca foi editada (`modifiedTime == createdTime`).
- **Destino identificado (G4):** mesma impressão da candidata.
- **Leitura (G5):** o leitor passa a observar `version` e `modifiedTime`; subida só de versão
  durante a leitura não aborta, mas a medição só vale se a impressão final das páginas lidas for
  igual à de referência (ela é a própria leitura, sem GET extra).
- **Após a escrita (G6):** sem mudança. A escrita muda `modifiedTime`; a reconciliação continua
  conferindo as células contra o plano cifrado.

## O que não muda

Recusa por `modifiedTime` diferente; recusa por qualquer diferença de conteúdo; recibos e
versões originais imutáveis; nenhum retry de POST; escrita só em cópia própria privada;
criação bloqueada; nenhum campo novo exposto ao cliente.

## Riscos e como a proposta os cobre

- `modifiedTime` atrasar em relação a uma edição real: coberto pela impressão de conteúdo.
- Edição fora das faixas do contrato com `modifiedTime` igual: impossível pela definição do
  campo; se ocorresse, ficaria fora do que o financeiro escreve ou confere.
- Custo: ~11 GETs Sheets por prova, só quando a versão diverge.

## Prazo da cópia (implementado)

`files.copy` espera até 120 s pela resposta (conexão continua 15 s) e o job da cópia tem 300 s
na fila. Sem resposta, segue a recuperação pelo marcador, sem repetir o POST.
