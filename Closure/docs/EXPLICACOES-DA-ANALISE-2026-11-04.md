# Explicar avisos na conversa

Implementação em `codex/explicar-avisos-ficha`, sobre main `be84d33`.
Commit, push e abertura de PR autorizados em 04/11/2026. Sem merge ou deploy.
Não publicada. Consulta R63/v0.373, análise R53 e Carteira Viva preservadas.

## Uso

O jogador pode copiar um aviso e perguntar às guias o que significa, ou
responder à página do painel. A conversa recebe uma referência editorial que
separa erro, pendência, observação e parte não conferida, com significado dos
campos esperado/encontrado e orientação para corrigir entradas sem apagar fórmulas.
A personagem e o idioma do servidor são preservados.

Há explicações por família para cadastro/aprovação, nomes custom, Ampliação,
Classe 0, orçamento, talentos/CE, leitura/exportação, progressão/treinos,
equipamento/carga e limites humanos. Avisos desconhecidos recebem a orientação
geral, com pedido de linha completa quando faltar contexto. Não é um catálogo
exaustivo de todas as mensagens específicas emitidas pelo motor.

O texto do jogador apenas seleciona referências; não é interpolado como
instrução de sistema. A citação do painel fica como dado na mensagem do usuário.
Não há leitura automática de links, edição, nova análise ou aprovação.
Nenhuma fórmula da mecânica foi alterada.

## Painel respondido

Somente a página já entregue pelo Discord e com autoria do próprio bot
confirmada é usada. Não busca páginas adicionais, mensagens ou fichas privadas.
Limite de 6.000 caracteres; páginas cortadas devem ser esclarecidas pelo jogador.
O painel é identificado pelo rodapé PT/EN; fica explícito que pode estar antigo.
As verificações existentes de troca de contexto do servidor continuam valendo.

## Validação e limites

Bateria final: 91 testes aprovados, zero falhas (explicações, clareza, conversa e camada Discord).
Testes locais sem modelo pago: categorias de aviso, casos específicos,
instruções em texto copiado, seguimento e mudança de assunto, página PT/EN,
autoria, histórico longo, duas personagens, duas lores e dois idiomas.
A regressão de autoria usa a instância carregada pelo bot: importar o cog
antes da bateria interferia na recarga de extensões e no teste de expiração de
conversa. As expectativas existentes não foram alteradas.

Pacote regenerado: 93 arquivos iguais aos fontes, sem ambiente, bancos ou
cadastro real. O ZIP fica ignorado; não foi enviado à Discloud.
A validação do texto final gerado por modelo e o ensaio real no Discord
continuam separados; esta rodada não fez chamadas pagas nem deploy.
