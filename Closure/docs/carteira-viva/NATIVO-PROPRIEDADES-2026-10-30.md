# Propriedades financeiras no Google

30/10/2026 · PR84 do bot e PR31 da ficha · ensaio separado, sem publicação.
**Ensaio encerrado às11:26:34 Brasília; propriedades validadas no caminho observado,
ativação e criação continuam bloqueadas.**

## Código e alcance

Produtor `adf36610a8b077377c95d4e9195dad318d0b0b2b`: perfil separado para quatro
propriedades do documento e uma do script, mais inspeção de rotinas somente de
leitura. Não muda o inicializador financeiro anterior nem o contrato REST.
O mantenedor autorizou esta implementação no rascunho PR31 e ensaio em descartável.
46 casos novos,101 financeiros e47 REST passaram localmente. CI41063190512 verde
às10:29:43 Brasília, log completo conferido. Bot67a6b98, CI41061489142 verde:
1.643 executados/1.642 aprovados/um opcional, zero falhas,352,598s.

A nova cópia privada foi feita pelo menu do Sheets, com colaboradores/comentários
desmarcados. Não é uma nova prova de criação pelo bot. Só ela recebeu o arquivo
QA com os dois fontes do produtor e auxiliares sintéticos. Arquivos preexistentes
foram preservados; nenhum bundle oficial foi substituído. Arquivo e projeto
identificados somente no diário privado, fora do Git. A pessoa concluiu o aceite
próprio do Apps Script; não houve novo OAuth das Guias ou ampliação de drive.file.

## Preparação da cópia

- A intenção local e a identificação do alvo foram registradas antes da cópia.
  O auxiliar vincula o arquivo ativo ao destino descartável e registra intenção
  em UserProperties antes da preparação financeira ou da semeadura.
- Primeira preparação financeira:10:38:27–10:44:28,361s, tempo máximo excedido.
  Propriedades ainda não ensaiadas. Não presumir ausência de escrita pelo timeout.
- Às10:51:22 o seletor conservou a função financeira anterior; o agente executou
  a preparação em vez do diagnóstico e cancelou às10:52:55. Erro operacional
  registrado. Nas execuções seguintes, a seleção foi conferida em estado novo
  antes de clicar Executar.
- Diagnóstico somente de leitura10:53:59–10:54:01: diário financeiro presente,
  legível, incompleto,26 passos/três alterações; intenção presente, diário das
  propriedades ausente e zero acionadores visíveis nesta conta.
- Retomada da mesma operação10:55:11–10:59:42: financeiro concluído, sem pedido
  de retomada e criação ainda falsa. Não se apagou o diário para recomeçar.
- Semeadura11:02:55–11:03:02: cinco resíduos fictícios e duas propriedades alheias
  sentinela. Prévia11:03:41–11:05:13: exatamente cinco alterações, criação falsa.

Para não multiplicar as leituras completas pelo próprio teste, semeadura, prévia,
aplicação, conferência e repetição usam chamadas separadas. Os fontes do produto
permanecem idênticos a adf3661; nenhum limite ou guarda foi relaxado. Os auxiliares
iniciais que repetiam a conferência três vezes na semeadura não foram executados.

## Aplicação e encerramento

- Aplicação11:06:33–11:08:58: retornou incompleta/retomar=true, sem indicar
  propriedades preparadas, ativação ou criação. Limite normal de quatro escritas.
- Mesma operação/assinatura/diário em11:09:38–11:12:29: concluída, retomar=false,
  propriedadesPreparadas=true. Ativação, financeiro completo e criação falsos.
- Leitura posterior11:13:58–11:15:30: cinco ausências e duas sentinelas confirmadas;
  hash das células financeiras, fórmulas/configuração e demais propriedades igual
  ao plano inicial. Inclui o diário financeiro anterior, sem apagá-lo/recriá-lo.
  Foi outra chamada pelo mesmo contrato de leitura, não um segundo interpretador
  independente. Não cobre formatos/abas fora desse contrato.
- Inspeção:zero rotinas visíveis, marca ausente e todos os indicadores globais
  falsos, inclusive responsável verificado pelo bot. Nenhum acionador criado.
- Repetição11:16:50–11:19:46: concluída, todas as propriedades de documento e
  script idênticas ao estado anterior. Criação permaneceu falsa.
- Encerramento11:23:15–11:23:17: removidos apenas os cinco marcadores QA de
  UserProperties; zero acionadores visíveis, `ScriptApp.invalidateAuth()` chamado.
  A consulta de status **na mesma execução** retornou autorização não requerida;
  esse retorno sozinho não foi aceito como prova de revogação.
- Uma tentativa posterior do diagnóstico abriu **Autorização obrigatória**.
  Cancelada sem revisar/renovar permissões; registro às11:25:12 informa que o
  projeto precisa de acesso para executar. Nenhuma nova leitura foi autorizada.
- A UI confirmou **Arquivo movido para a lixeira**, com o nome exato da única
  cópia QA. Exclusão recuperável, não esvaziamento da lixeira. Abas da cópia e do
  projeto fechadas; as três abas preexistentes do usuário foram preservadas.
- Fechamento local11:26:34: porta8876 livre e servidor auxiliar já encerrado.
  Este ensaio não criou banco/cadastro do bot, token Google das Guias, personagem
  ou acionador. A autorização invalidada é do projeto vinculado à cópia, não a
  concessão Guias encerrada no ensaio REST anterior.

Fonte QA final relida:36.862 caracteres/37.130 bytes; sufixos de diagnóstico,
encerramento e etapas isoladas idênticos aos preparados. Os auxiliares exatos e
os resultados sanitizados estão fora do Git, com pasta 700/arquivos 600.
Os registros privados ficam em
`~/.local/share/guias-ciclo/carteira-piloto/etapa7-propriedades-20261030/`.
Não publicar IDs privados, valores de propriedades, e-mails pessoais ou credenciais.

## Custo observado

Prévia: 92 s; primeira aplicação: 145 s; retomada: 171 s; conferência: 92 s;
repetição: 176 s,
medidos entre início e fim no registro do Apps Script. Latência de uma única
cópia/conta, sem garantia geral ou otimização demonstrada. O preparador anterior
excedeu 361 s e retomou em 271 s; a causa exata do custo não foi isolada. Não atribuir
isso ao novo perfil nem aumentar limites/retirar validações sem medição focal.
Uma próxima otimização deve reduzir chamadas preservando releituras e recusas;
não aproveitar um snapshot antigo para declarar pós-condição fresca.

## Limites que permanecem

O teste é só uma cópia Ciclo e uma conta; não prova Era, modelo do servidor,
identidade verificável no backend, horário/eventos reais ou ausência de acionadores
de outras contas. A inspeção não instala rotinas nem concede aprovação.
`ativacaoConcluida`, `financeiroConcluido`, `responsavelVerificadoPeloBot` e
`criacaoDisponivel` continuam falsos. Não cadastrar o alvo como personagem.

Não repetir o [ensaio REST já encerrado](NATIVO-ESCRITA-EQUIVALENTE-2026-10-30.md).
Faltam ativação/atestado verificáveis, concorrência/CAS, demais domínios e prova
integrada; etapa7 parcial, etapas8–10 pendentes. Sem oficial/jogador, modelo pago,
merge/deploy, mudança de campanha ou de escopo das Guias.
