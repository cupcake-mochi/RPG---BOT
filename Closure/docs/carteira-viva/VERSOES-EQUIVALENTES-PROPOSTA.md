# Proposta: versão nova do Drive sem edição

30/10/2026 · PR 84 · **aprovado pelo mantenedor e implementado offline** (seção final).
[Escrita financeira e recuperação nativas,30/10](NATIVO-ESCRITA-EQUIVALENTE-2026-10-30.md)
aprovadas no caminho observado; sem equivalências extras registradas0/0.
O registro por impressão de uma versão equivalente continua validado offline.

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

## Implementação · 30/10

Aprovado pelo mantenedor. Implementado offline; o fluxo financeiro foi validado nativamente no fechamento acima, sem exercitar o registro de equivalências extras.

- `Provedores.observar_arquivo`: versão e `modifiedTime` na mesma resposta (formato validado).
  `versao_arquivo` continua igual nos outros fluxos. `DestinoCopia.modificado` opcional:
  ausente nunca serve de prova.
- `equivalencia_versao.py`: `Impressao`, `impressao()` (medição financeira em lotes com versão e
  `modifiedTime` iguais do início ao fim), `versoes_aceitas()` e `provar()`.
- **Impressão = novo hash `conteudo` da medição.** Ao testar, o `antes` mostrou-se impróprio: a
  semente inclui o ID do arquivo e o contexto da operação, então mudava entre o fluxo de cópia e o
  financeiro. `conteudo` usa os mesmos dados por página, com semente só do contrato e do layout.
  Regressão própria prova que ele não muda com o contexto e muda com o conteúdo.
- Diário da cópia: `ref_origem` (gravada com `fixar_versao_copia`, antes do POST), `ref_destino`
  (gravada na identificação) e `equivalencias` (até 8 por alvo), fora do hash de contexto como o
  histórico de observações. `registrar_equivalencia_copia` confere de novo contra a referência.
- Cópia: mede a origem antes do POST e a cópia na identificação. **Candidata** com versão nova é
  aceita só se o `modifiedTime` da primeira observação não mudou: a versão da candidata nunca foi
  lida nem usada como conteúdo; a prova de conteúdo começa em `ref_destino`.
- Financeiro: origem e destino provados no início; antes de armar a escrita, versão nova do destino
  só com prova; `preparar_financeiro` exige versão aceita e, se não for a original, `conteudo` igual
  a `ref_destino`; `armar_financeiro` aceita só versões provadas.
- **Diferença do desenho: a leitura (G5) continua estrita.** Subida de versão no meio de uma
  medição recusa como antes. Mais conservador; revisitar se o ensaio nativo mostrar necessidade.
- **Fora do escopo:** a intenção `preparada` ainda compara com a versão configurada do modelo, e
  `validar_modelo` continua recusando metadados diferentes durante a prévia. Operações antigas sem
  referência continuam estritas.
- **Custo:** cada impressão gasta ~38 cotas locais (11 lotes × 3 + observações). Com o limite local
  de 45/min, a cópia passa a esperar cerca de 1 minuto a mais; cabe no prazo de 300 s.

Testes: cópia 37 (4 novos, 3 ajustados para simular edição real com `modifiedTime` novo); financeiro
40 (5 novos). Escrita financeira e recuperação nativas fechadas no relatório de30/10 acima; as demais limitações permanecem.
