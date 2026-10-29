# Comparar leituras da grade

28/10/2026 · PR 84 · ferramenta interna, validada offline; não publicada.

## Para que serve

O ensaio financeiro anterior viu mudanças na versão Drive da fonte e da cópia,
mas não identificou as causas. O bot agora tem `DiagnosticoGrade`, para comparar
duas leituras estritas da mesma fonte e do mesmo domínio/contexto. Ainda precisa
ser composto no piloto autenticado antes de um novo ensaio real. Não é comando,
endpoint, preparação da ficha ou autorização para continuar uma cópia recusada.

O [Google Sheets distingue entrada, resultado, nota e formato](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/cells).
A comparação mantém cinco categorias separadas:

- **Literais:** valores preenchidos, preservando texto, número e booleano.
- **Fórmulas:** texto exato da fórmula; não usa o resultado para inferi-la.
- **Resultados:** valores calculados ou literais retornados pela API.
- **Notas:** somente as notas das células, não comentários do Drive.
- **Formatos numéricos:** tipo e padrão solicitados pelo leitor existente.

Trocar uma fórmula por um literal com o mesmo resultado altera as duas primeiras
categorias. Mover conteúdo dentro da página também altera sua assinatura. Números
equivalentes como 1/1.0 e 0/-0.0 não simulam diferença; texto, vazio, ausência e
booleanos continuam distintos. Fórmulas, notas e textos não são normalizados.

## Cobertura e significado do resultado

A ferramenta usa **as faixas fixas e a paginação atuais de `LeitorGradeRest`**,
com os mesmos GETs, autorização, cotas, prazo e guardas de versão. Não cria outro
transporte nem acrescenta chamadas. Ela só registra páginas que o leitor aceitou.
Se a versão mudar ao ler uma página, aquela página fica fora da comparação.

O resumo informa páginas previstas/lidas em cada amostra, fechamento completo ou
interrupção por versão, versões iniciais iguais/diferentes e a quantidade de
**páginas** com diferença em cada categoria. Não são contagens de células.

Somente páginas comuns são comparadas. Zero diferenças significa igualdade
nessas páginas e nesses cinco campos. Sem páginas comuns, as contagens são
`null`, nunca zero. Se dimensões, IDs/títulos de abas ou faixas do plano diferirem,
a cobertura fica incompatível e nenhuma página é comparada. Uma amostra com todas
as páginas lidas, mas mudança na confirmação final, continua incompleta.

Ficam fora: células/abas não lidas, demais formatos, imagens, mesclas, validações,
proteções, comentários, nomes definidos, configurações gerais da planilha,
metadados Drive e propriedades/código Apps Script. A igualdade da projeção
**não prova estabilidade global, preservação integral, recálculo ou problema de
cache**. Os quatro indicadores de liberação permanecem falsos no resumo.

## Dados e limites

Cada instância aceita duas amostras, até 128 páginas por amostra e 4.096 células
por página. Usa HMAC com chave aleatória própria, guardando apenas os resumos em
memória, com limite de volume por página. Chaves/resumos nunca entram no retorno,
banco, backup, logs ou relatório. Hashes de outra instância não são comparáveis.
Não há hash público que permita adivinhar valores curtos por tentativa.

O vínculo privado inclui arquivo, domínio, contexto e geometria. Fonte e cópia
são arquivos diferentes e não podem ser comparados entre si por esta ferramenta.
Planos pertencem ao leitor original. Uma referência fraca ao plano impede repetir
o mesmo objeto sem manter sua grade ou identificadores em memória pelo diagnóstico.

O prazo total é de 30 minutos, sem renovação. Ao usar uma instância expirada,
ela descarta chave e amostras. Erro de acesso, transporte, formato ou cancelamento
também descarta tudo; apenas a mudança tipificada de versão preserva uma amostra
parcial. O piloto deve chamar `fechar()` em `finally`; não há temporizador que
limpe uma instância abandonada. Não serializar ou registrar seus atributos privados.

## Próximo ensaio, sem escrita

1. Compor o piloto com uma fonte privada **descartável**, selecionada por novo
   consentimento quando necessário; não restaurar o grant revogado do ensaio antigo.
2. Vincular o contexto à operação, ao iniciador, à conexão e ao arquivo derivados
   do banco. Revalidar identidade/cargos atuais e reservar cota em cada chamada,
   usando os callbacks existentes. Não receber IDs/faixas livres do navegador.
3. Abrir um plano estrito, observar uma vez, abrir explicitamente outro plano
   da mesma fonte/contexto e observar outra vez. Cada plano mantém sua versão;
   não alterar versão configurada, candidata ou recibo de cópia identificado.
4. Comparar só o resumo sanitizado, registrando cobertura e interrupções. Se faltar
   cobertura, informar essa falta. Não aguardar/repetir até aparecer uma igualdade.
5. Não enviar POST Drive/Sheets, não inicializar financeiro ou Apps Script e não
   cadastrar personagem como consequência. Fechar a instância e encerrar o piloto.

Essa composição autenticada e o ensaio real **ainda não foram executados**. A
ferramenta não oferece protocolo de cancelamento/encerramento da candidata nem
contrato de preparação global de conteúdo. Essas decisões, as cinco propriedades
Apps Script, demais domínios, concorrência, preservação e prova integral continuam
pendentes. Criação bloqueada, sem mudar o produtor ou a produção.

## Validação

Testes HTTP simulados de categorias, troca de fórmula por literal, posições,
tipos, números equivalentes, páginas parciais, mudança no fechamento, grade
incompatível, contexto/fonte distintos, autorização, cancelamento, prazo,
concorrência, limites e privacidade. Não houve chamada Google/Discord real.
112 testes direcionados distintos aprovados: 87 existentes da grade/cópia/financeiro
passaram no lote de 110 em 58,943 s; os 25 novos passaram no lote final em 6,967 s.
O único erro inicial foi da fixture descrita abaixo. CI completo ainda pendente;
não atribuir a este código os 1.533 da revisão anterior.

Pacote ignorado regenerado e comparado: 90 arquivos, CRC e bytes dos fontes
iguais, sem Carteira/env/bancos/campanha. SHA256 `bfd7b4afc7aa6509c38e9cb20ebee562ee6198d3967f42e71c8a2e510ee12fce`.
Não publicado.

Um erro inicial foi da fixture: aplicava duas células também em faixas de uma
coluna. O leitor recusou corretamente; o teste passou a fornecer os dados somente
na faixa de seis colunas prevista. Não foi relaxada a validação do leitor.

Não houve modelo pago, escopo novo, edição de oficial/jogador, merge ou deploy.
Continuação: Sol Alto; revisão Médio.
