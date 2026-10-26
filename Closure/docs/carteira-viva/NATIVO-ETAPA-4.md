# Leitura completa no Google

Concluído em 26/10/2026 15:57:01 (Brasília), na branch `codex/carteira-viva-etapa-4`,
PR 81 dependente da 80. **Piloto local com provedores reais; sem merge ou deploy.**

## Cópia e acesso

Foi usada somente a cópia privada **QA Carteira — leitura completa — DESCARTÁVEL
— 26-10-2026**, ID `1MWj-9f21rRnr7pA4vEegGYw0-ec2tQ2kBSWE4Rxjy08`, criada
pelo conector Drive a partir da oficial Ciclo Maldito. `shared=false` confirmado.
Nenhuma célula da cópia, oficial ou jogador foi editada. Nome fictício foi
configurado só no cadastro local, não na planilha.

Após interrupção e expiração da tentativa anterior, o serviço local foi
reiniciado e uma entrada nova foi criada. A aba original do Discord ainda tinha
sessão válida e permitiu concluir identify. O usuário passou pelo aviso Google
e confirmou a autorização solicitada. Picker selecionou somente essa cópia;
cadastro fictício foi confirmado pela interface. O grant anterior da etapa 3
não foi reutilizado. Serviço separado, banco cifrado próprio e campanha fictícia
local `{}`; nenhuma regra/aprovação real do servidor foi alterada.

## Defeito encontrado e correção

O primeiro pedido completo tentou transportar `userEnteredValue`, incluindo as
fórmulas longas de todas as células. A resposta ultrapassou 16 MiB e foi recusada
com `tamanho`. O limite não foi aumentado. Agora o field mask pede somente
`effectiveValue`, incluindo `errorValue`. Não baixa fórmulas nem outras abas.

Na resposta nativa, 13.371 células vieram sem valor efetivo explícito, incluindo
vazios calculados normais. A API ao vivo não expõe o cache de fórmula do arquivo
XLSX. Esses vazios continuam vazios; não viram zero ou benefício presumido.
A grade enxuta reserializada no diagnóstico ocupou 3.888.453 bytes (não é medição
exata de bytes transferidos). A comparação com o XLSX calculado comprovou
**18.393 chaves iguais, zero diferenças**. Cache XLSX ausente continua sendo
recusado pelo leitor existente, com nova regressão específica. Erros de fórmula
na API, duplicatas, limites e exportação incompleta continuam protegidos.

## Resultados reais

| Ensaio | Resultado |
|---|---|
| Conexão Discord/Google e Picker | Cadastro fictício salvo usando só a cópia selecionada |
| Reinício após cadastro | Conexão persistiu e renovou sem novo consentimento |
| Primeira atualização | Leitura completa salva, `cache=false` |
| Segunda atualização | Mesmo ID de leitura, `cache=true` |
| Análise explícita | Nova leitura; não certificou o cache anterior |
| Abertura da análise salva | Mesmo resultado, com nova verificação de contexto |
| Grade autenticada versus XLSX calculado | 18.393 campos iguais, zero diferenças |
| Motor pela API versus motor sobre XLSX | Achados integralmente iguais |
| Resultado da cópia ainda incompleta | Reprovada: 5 erros, 9 pendências e 12 partes não conferidas, iguais nos dois caminhos |
| Limpeza da concessão | Endpoint Google de revogação respondeu HTTP 200 |
| Cadastro e credenciais de teste | Zero cadastros dessa cópia e zero conexões ativas no banco do piloto |
| Arquivo de teste | Interface Google confirmou “Arquivo movido para a lixeira”; exclusão recuperável |
| Encerramento | Serviço parado, convite local removido, abas temporárias fechadas e tópico Testes restaurado |

O roteiro final fez quatro chamadas à API interna. Houve duas leituras Google
completas estáveis, uma tentativa cada: pelo código, seis GETs Drive/Sheets e
duas renovações OAuth. Cadastro/Picker, investigação da primeira falha, exportação
XLSX e revogação são operações adicionais; não estão incluídas nesse subtotal.
Não é uma auditoria de todas as requisições da conta/projeto. **Zero chamadas de
modelo pagas.** Não foram enviadas mensagens ao Discord.

## Testes e limites

A paridade offline foi ampliada com Ritual e entidade, além dos seis casos
anteriores. Os novos casos passaram; Ritual não ganhou falso alerta de Técnica
Inata e a conferência de Vida da entidade foi preservada. Agora há 50 testes
novos distintos da etapa 4. No lote local, um teste HTTP estourou seu segundo
fixo de prazo durante forte lentidão; os demais 49 passaram. O reteste isolado
repetiu o timeout, com callbacks simples também demorando centenas de ms.
A guarda foi reescrita para **proibir adquirir o semáforo de leituras** na rota
de saúde, em vez de medir o agendamento da máquina. Ela falha se a rota tentar
esperar vaga; não foi só aumentado um timeout. Os quatro testes HTTP passaram
após a mudança, em 15,888 s. Conferir o CI do SHA final para a suíte completa.

O executor local também mostrou demora ao despertar threads. O runner temporário
usou um tick no loop, sem mudar o servidor do produto. Esse runner fica fora do
Git e não transforma o piloto em benchmark. Ainda faltam medições da etapa 9.

Este ensaio valida conexão e leitura/análise básicas nativas. Ritual, entidades
e custom foram ampliados **offline**, não criados/editados no Google desta rodada.
As baterias nativas avançadas, troca entre dois arquivos, cargos reais, galeria,
idiomas e celular físico continuam na matriz das próximas etapas. O painel
Discord ainda não está integrado à Carteira; os resultados privados foram
exercitados pelas rotas internas autenticadas, não por comando instalado.

## Evidência e proteção de dados

Confirmação visual em `/tmp/carteira-etapa4-nativo-cadastro.png`; cópia na lixeira
em `/tmp/carteira-etapa4-copia-na-lixeira.png`. Arquivos fora do Git. Diagnósticos
completos e configuração permanecem no diretório privado do piloto, sem valores
em relatório/PR. Auditoria mínima e registro de revogação seguem a retenção do
banco; não afirmar que esses registros também foram apagados.

Nenhum segredo, banco, cadastro real ou exportação entrou no Git. O manifesto do
bot continua excluindo a Carteira. Próxima etapa: galeria/cartões, com GPT-6.1 Sol
· Alto; hospedagem pública e sincronização confiável de campanhas seguem pendentes.
