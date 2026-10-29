# Diagnóstico no serviço

28/10/2026 · PR 84 · integração interna validada offline; ensaio real pendente.

## Entrada e vínculo

`Consultas.diagnosticar_grade_copia(servidor, usuario, referencia, alvo=..., dominio=...)`
recebe uma `ReferenciaCopia` já emitida pelo backend. Não há rota HTTP, comando
Discord, campo de URL/arquivo ou nova intenção de cópia. Os únicos alvos são
`origem`/`copia` e os domínios `financeiro`/`progressao`. As faixas continuam fixas.

O banco deriva o arquivo do diário, exige operação enviada/identificada com versão
original da fonte registrada e modelo particular do servidor. Modelos oficiais
e suas IDs reais, mesmo configuradas como particulares, são recusados neste piloto.
Para cópia pendente, a candidata já precisa estar registrada; não faz busca Drive
ou POST de cópia. Para recibo identificado, usa o destino existente, inclusive em
legado compatível. Cópia cadastrada em qualquer mesa é recusada. A origem pode ser
uma fonte cadastrada, mas continua somente leitura pela própria conexão.

O contexto inclui operação, ator, modelo/revisão, autorização e todos os campos do
diário exceto o histórico técnico de versões. Só o dono da conexão/operação pode
usar o método; admin, dono do servidor ou revisor não herdam a conexão alheia.

## Execução

Usa a mesma fila justa por servidor/usuário, com coalescência por operação/alvo/
domínio/contexto, e o mesmo controle de cota por conta Google. Prazo de execução
de 1.200 s e espera de 1.290 s, definidos no backend. Não há retry de estabilidade,
cache de autorização, Gateway ou aumento de escopo.

Cada revalidação faz GET novo do membro e prova o acesso básico no banco. Não
atribui privilégios administrativos nem precisa consultar definições de cargos
para esse acesso exclusivo do dono. A renovação Google mantém seu caminho comum,
incluindo trava, rotação e recusa de grant antigo/revogado. Mudança enquanto aguarda
fila/cota, perda de participação, conexão, modelo ou cadastro da candidata interrompe.

Antes/depois de cada uma das **duas** amostras, a rede reconfere arquivo próprio,
privado, autorizado ao app, fora da lixeira/Drive compartilhado e com permissão
única de proprietário. Na cópia exige também os marcadores da operação/origem.
A origem não tem obrigação de carregar marcador de cópia. As guardas de privacidade
comuns foram extraídas sem alterar as condições do adaptador de cópia anterior.

São quatro GETs de privacidade adicionais, cada um passando por cota e revalidação;
os GETs da grade mantêm suas checagens estritas de versão. Uma versão atual diferente
do recibo pode ser **lida para diagnóstico**; o diário, candidata e recibo não mudam.
O financeiro continua recusando inicialização pela versão antiga. Não se prepara
ou arma diário financeiro, não se envia escrita Sheets/Drive e não se cadastra
personagem. Apenas a manutenção comum da conexão pode persistir uma rotação OAuth.

## Resumo e descarte

Retorna o [resumo limitado do comparador](DIAGNOSTICO-GRADE-2026-10-28.md), acrescido
de dois pares de booleanos: `versao_mudou_antes_coleta` compara a observação de
privacidade com a abertura do plano; `versao_mudou_apos_coleta` compara a confirmação
da amostra com a observação privada posterior. Não retorna IDs, conteúdo, valores
de versão, hashes ou chaves. Esses sinais não dizem quem alterou o arquivo ou por quê.

Erro de abertura não vira amostra completa. Uma mudança tipificada durante uma
amostra conserva só as páginas aceitas; faz a segunda observação prevista, sem
repetir até estabilizar. Erro de acesso/transporte/estrutura cancela o diagnóstico.
Os buffers são fechados em `finally`, inclusive ao cancelar o último cliente.
Cada cliente coalescido reconfere seu acesso após a fila e recebe cópia independente
do resumo. Nenhum diagnóstico é gravado no banco, backup ou cadastro de personagem.
Os quatro indicadores de liberação continuam falsos.

## Validação offline

121 direcionados distintos aprovados: lote de 118 em 84,932 s e três adicionais
em 2,014 s, sem falhas. São **34 novos testes** com banco/serviço reais e HTTP
fictício, sem importar a classe de testes financeira como novos casos duplicados.

Cobrem origem/cópia, candidata pendente, recibo legado, financeiro/progressão,
isolamento, fonte/ator/servidor/cliente, oficiais e disfarce de oficial, cadastro
em outra mesa antes/durante leitura, privacidade/marcadores, coalescência, mudança
de modelo, cota, membro ausente, revogação/reautorização/expiração, mudança de versão
durante/antes/depois da coleta, 429 sem retry, entrega após revogação e cancelamento.
Conferem diário/dados preservados, ausência de escrita/cadastro e fechamento dos
hashes. CI completo deste código pendente; não atribuir os 1.558 anteriores a ele.

Pacote ignorado regenerado e comparado: 90 arquivos, CRC/fontes iguais, sem
Carteira/env/bancos/campanha; SHA256 `13aea1c6aaeb2ff2d13edd84a05d4699dcf6fc27e1c85dbb08e553441de265f0`.
Não publicado.

## Ensaio real e pendências

Executar primeiro somente leitura numa fonte privada **descartável** e numa cópia
do bot ligada ao mesmo diário, com grant próprio atual. Não reutilizar concessões
revogadas ou restaurar as descartáveis já descartadas do ensaio financeiro anterior.
O piloto precisa obter a referência pela operação real, nunca aceitar IDs do
navegador, logar apenas o resumo sanitizado e encerrar/revogar/descartar seus recursos.

A integração está pronta para esse ensaio; **ainda não há resultado real**. A causa
das versões nativas continua desconhecida. O método não cancela candidatas, não
aprova versões novas e não define preparação global de conteúdo. Propriedades Apps
Script, demais domínios, concorrência, preservação, automações/responsável e prova
integral continuam pendentes. Criação bloqueada, sem merge ou publicação.

Continuação: Sol Alto; revisão Médio.
