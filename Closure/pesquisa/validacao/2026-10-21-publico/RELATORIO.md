# Publicação de idioma e lore por servidor · 21/10/2026

## Entrega

Guias: runtime `a2baf89f7857aea3a35a3a5928fbf1b3cd036162`, branch `codex/guias-de-comandos`, PR 68 aberta em rascunho. Arquivista: runtime `932df0e`, branch `codex/idioma-ingles`, PR 10 aberta em rascunho. Publicação autorizada: Arquivista conectada às 13:25:33 e Guias às 13:25:45, horário de Brasília. Nenhum merge desta etapa.

`/idioma` e `/language` alteram respostas por servidor. Nomes/opções dos menus nativos seguem o idioma do cliente Discord. Guias e Arquivista têm preferências independentes. A Arquivista 1.1.0 cria arquivos novos na língua escolhida e preserva a língua e os acessos dos existentes.

Nas Guias, `/lnt` escolhe a base original de Arknights ou Nova Terra. Defaults Nova Terra: 1361766037405564988, 1357866906341736488, 1480606366090526893. Outros servidores começam na base original. `/cargo_admin` registra papéis delegados para idioma/lore, sem conceder permissões Discord nem delegação adicional. A Arquivista usa seus cargos de staff atuais. As autorizações não aprovam fichas.

Memória e histórico passaram a respeitar servidor/mundo. Pronomes continuam compartilhados; fatos antigos sem origem ficam no legado privado. A reflexão diária usa pseudônimos separados por contexto na mesma chamada. Foi corrigida uma corrida na troca de mundo enquanto uma resposta estava sendo enviada. Não há promessa de impedir retroativamente uma mensagem já aceita pelo Discord.

Interface, guias, análise e erros conhecidos têm apresentação inglesa; rótulos oficiais, escolhas e texto do jogador permanecem canônicos. A base original é uma referência curada de personagens/regiões, não uma cópia integral de todos os roteiros do jogo. Kal’tsit usa o recorte clássico anterior ao episódio 15. Cartões e regras mecânicas não foram reescritos.

Ajuda sem menções a canais reais; revisão do mestre pede link ou XLSX da ficha atual; livro com PDF normal e escuro. Pedidos reconhecidos de links públicos podem ser respondidos diretamente na voz da personagem, sem modelo, mídia ou extração diária. Isso não executa análises, configurações, aprovações ou envio arbitrário de arquivos.

## Validação

- Guias: 944 testes executados, 943 aprovados e um online opcional pulado. 109 direcionados aprovados; o pacote regenera o núcleo e comprova os dois perfis antes de ser criado.
- Arquivista: 149 testes Python aprovados, 29 JavaScript da ponte e 7 da planilha. O acabamento final alterou apenas textos Python/recursos; os scripts JS foram preservados.
- Google real privado: fórmulas inglesas calculadas, visor/contador/data ISO, expansão 20→40→60 e transferência preservando ID. Arquivo sintético enviado à lixeira. Não foi repetida a concessão real de editor por e-mail; criação/retomada/compartilhamento têm regressões simuladas.
- Migrações em cópias privadas de produção: preservação das linhas preexistentes, integridade antes/depois. Auditoria posterior considera os arquivos WAL dos bancos.
- 88 arquivos instalados das Guias e 27 da Arquivista iguais aos pacotes byte a byte. Sem credenciais ou bancos nos pacotes. Ambiente preservado; banco legado, campanha, fatos antigos e configurações anteriores das Guias preservados. O estado meteorológico do painel mudou de poucas nuvens para parcialmente nublado; destino, dia e mensagem permaneceram iguais.
- Arquivista: cadastros, histórico, confirmações, avisos, arquivos gerenciados, apelidos e configurações anteriores preservados. Nenhuma planilha oficial foi alterada.

## Discord real

Tópico autorizado: https://discord.com/channels/1357866906341736488/1561410667108368575 . Duas contas do usuário, com e sem administração.

Confirmados: `/language` inglês nos dois bots; resposta privada; ajuda inglesa de administrador e membro, com comandos administrativos ausentes na ajuda do membro; guia criar inglês da página 1 à 14/Emitida; análise inglesa por link do modelo oficial e navegação Resumo→Limites; painel antigo mantendo inglês após restaurar o servidor para português; entrega dos dois links do livro por menção à guia; diagnóstico privado Arquivista 1.1.0 em inglês; guia público Arquivista para membro, com cinco páginas; recusa de `/lnt` para membro comum e recusa de `/language` da Arquivista para membro comum; Nova Terra desligada e ligada pela conta autorizada.

Ao fim: os dois bots em pt-BR e Nova Terra ligada no servidor de teste; nenhum cargo delegado criado. Status confirmou a restauração. Auditoria do banco: **zero novas chamadas de modelo** na bateria (686 antes/depois). A primeira tentativa só pelo nome no tópico foi ignorada por estar fora dos canais de escuta; marcar o bot entregou os links, comportamento esperado.

O seletor de arquivo da Discloud no navegador interno falhou antes do envio; a publicação foi concluída na aba Brave autenticada. Alguns cliques de navegação DOM não acionaram botões no navegador interno; cliques na posição visível funcionaram. Não houve defeito do callback demonstrado. Backups posteriores foram baixados e auditados; modal sozinho não foi contado como download.

## Documentação pública

As políticas das Guias foram atualizadas nos gists existentes e relidas. Os três Google Docs da Arquivista receberam bloco de idioma e versão inglesa; leitura posterior comprovou que o texto anterior foi preservado. Links e permissões mantidos.

## O que permanece separado

Não foi avaliada resposta natural de um modelo real, pois esta etapa proíbe chamadas pagas. Isolamento, contexto e montagem dos dois motores foram testados offline. Não é certificação de fidelidade integral à lore original ou de ausência de erro futuro do modelo. Fatos sensíveis continuam sujeitos a falhas do filtro.

O idioma não traduz toda a ficha oficial nem todo o livro. A comparação integral do corpus geral R51/R52 com o livro R53 continua pendente. Ensaios nativos ampliados de alto nível/entidades, campos ausentes e defeitos do produtor permanecem nas retomadas R53/B47. Aprendizado, marcos reais, autorizações, requisitos livres, narrativa, alvos e Alma continuam com o mestre. Não declarar aprovação automática ou verificação integral da ficha.

## Retomada exata

Verificar remoto e árvore antes de editar. Guias: `codex/guias-de-comandos`/PR 68, `Closure/docs/RETOMADA-PUBLICO.md`; Arquivista: `codex/idioma-ingles`/PR 10, `docs/RETOMADA-IDIOMA.md`. Não repetir implantação por mudanças só de documentação. Não fazer merge sem autorização específica para estas PRs. Backups privados e imagens ficam fora do Git. Não reabrir tarefas históricas já fechadas.
