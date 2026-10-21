# Guias de criação e consulta da ficha · 21/10/2026

## Entrega

Publicados na Discloud, app Guias do Ciclo `1773761486581`:

- `GC:guia criar`: **Criar uma ficha**, 14 etapas, da cópia à marcação de
  Emitida na CARTEIRA, depois da revisão com o mestre.
- `GC:guia planilha`: **Conhecer a planilha**, 14 páginas de consulta sobre
  abas, versões, configurações, progressão, emissão, salários e missões.
- `GC:guia ficha` / `/ficha guia`: **Analisar uma ficha**, assunto existente
  mantido separado e agora com um nome que explicita sua função.
- `/guia` oferece os onze assuntos; são 46 páginas no total.

O usuário aprovou a implementação e reiterou a necessidade de várias
revisões de clareza e cobertura. Pediu também títulos intuitivos após ver o
seletor. O polimento posterior trocou termos vagos por tarefas, como
**Como montar e editar uma habilidade**, **Como registrar missões e atualizar
a ficha** e **Por onde começar e como abrir as seções**.

Branch `codex/guias-de-comandos`, [PR 68](https://github.com/cupcake-mochi/RPG---BOT/pull/68)
aberta em rascunho. Runtime final **268d3260898959b4652436ddeeb79be5d8b96739**.
Implementação inicial desta ampliação: `7b7c72383e1ababee43e1afc4680541184265510`.
Não houve merge.

## Fontes e revisão

O bot e o remoto foram conferidos antes de editar. Fontes primárias lidas
sem modificá-las:

- Ficha---RPG-JJK main `fbd6d156602958dc0f9da467a4a80100ad7b913f`, já posterior
  à publicação R53 e com a extensão de emissão/salários de 20/10.
- JJK---Project main `1432c477f812aaaf1e0e8fdff8ed54d1709a663d`, fechamento
  atual R53, capítulo Criar um personagem e demais seções pertinentes.
- Contrato e consumidor vigentes do bot para limites e aprovação exata.

Mapeamento de fontes por assunto e cinco passadas editoriais documentados
em [GUIAS-DE-USO.md](../../../docs/GUIAS-DE-USO.md). Foram conferidos o
conteúdo factual, a sequência de um jogador novo, a cobertura até a emissão,
a apresentação em páginas/menus e, por pedido posterior, os nomes e títulos.

O guia explica a desmarcação automática de Emitida, a data fixa em Brasília,
o efeito de reemissão sobre o ciclo aberto, a ativação salarial por cópia e
a separação entre ienes manuais e créditos de salários. Não confunde essas
ações com envio ao bot ou autorização do mestre.

Os subtítulos que contêm “ · ” são convertidos para “: ” no segmento usado
pelo seletor de páginas. Assim, regras, bônus e cadastros de CONFIGURAÇÃO
conservam nomes distintos. A mudança tem regressão de unicidade dos rótulos.

## Verificação

| Verificação | Resultado |
|---|---|
| Suíte completa local, sem chamadas pagas | 900 executados, 899 aprovados, um online opcional pulado; 284,702 s |
| Guias, após o ajuste final de títulos | 9 aprovados |
| Camada Discord, após o ajuste final de títulos | 65 aprovados; inclui prefixos novos, aliases e ausência de análise/modelo |
| ZIP final extraído | 9 testes dos guias aprovados |
| CI da implementação `7b7c723` | [aprovada](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/39602900647) |
| CI do runtime final `268d326` | [aprovada](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/39604003311) |

A suíte local completa iniciou antes dos últimos ajustes de rótulos; estes
receberam os testes direcionados finais e a CI completa do SHA final. Não
foram alteradas expectativas mecânicas para obter aprovação. A atualização
na expectativa do título acompanha a renomeação pedida pelo usuário.

### Ensaio real no Discord

Servidor autorizado `1357866906341736488`, tópico Testes
`1561410667108368575`, sessão do próprio usuário no navegador do aplicativo.

1. [GC:guia criar](https://discord.com/channels/1357866906341736488/1561410667108368575/1562448712998064140):
   primeira página, todas as 13 transições e chegada à etapa 14, Emitida.
2. [GC:guia planilha](https://discord.com/channels/1357866906341736488/1561410667108368575/1562449010827071509):
   14 páginas percorridas, seletor com títulos completos e salto para regras
   da campanha. A última resposta precisou de nova leitura da interface,
   pois a atualização do Discord ainda estava em trânsito; confirmou página 14.
3. Após o ajuste de nomes e segunda publicação,
   [novo painel](https://discord.com/channels/1357866906341736488/1561410667108368575/1562450342203891839):
   primeira página com título novo, seletor das 14 páginas, salto para
   **Como montar e editar uma habilidade**, menu com os três assuntos
   distintos, troca para Criar reiniciando na página 1 e salto para a etapa 14.

As 28 páginas foram percorridas antes da revisão final de nomes; depois,
foram conferidos os títulos, menus e saltos afetados. Os atalhos novos não
chamam modelos. Privacidade da barra, opções, timeout e cliques encerrados
estão cobertos nos testes; não se repetiu a espera nativa de dez minutos ou
um ensaio com outra pessoa. O `/guia` privado já foi exercitado no fechamento
anterior; os novos assuntos foram ensaiados pelo prefixo e menus.

## Publicação e preservação

Autorização de implantação do trabalho de guias já concedida pelo usuário.
Backup novo antes de publicar, arquivo privado de Downloads com sufixo (14).
Primeiro runtime `7b7c723` online em cinco servidores às **09:52:40**.
Após a orientação adicional sobre títulos, runtime final `268d326` online
em cinco servidores às **09:59:35**, horários de Brasília.

Backups posteriores (15) e (16) foram baixados para comparação, com permissão
local 0600. O (15) também é a cópia anterior à segunda publicação. Não se
usou o console para editar código em produção.

- ZIP final: **78 arquivos**, todos iguais aos fontes e aos bytes instalados.
- SHA-256: `3bf04136ad05f92591df2bd7cef300709cca8a7a9ce928dd9993de4f27de7697`.
- Sem `.env`, bancos ou cadastro real de campanha dentro do pacote.
- Ambiente, cadastro de campanha e núcleo iguais nos backups anterior/posterior.
- Dois bancos íntegros por `PRAGMA quick_check`, também idênticos entre backups.
- Recursos preservados: 700 MB e 0,68 vCPU. Build concluído, bot conectado,
  sem erros de aplicação no trecho observado. Avisos de dependências de voz
  PyNaCl/davey são anteriores e não afetam o guia estático.
- Personalidades, memória, mídia, cálculos e permissões não foram alterados.

Auditoria pública sem conteúdo real em [pacote.json](pacote.json). Capturas,
logs de testes e backups permanecem locais/ignorados; não foram versionados
credenciais, bancos ou dados de campanha. Capturas em
`Closure/src/var/guias-criacao-2026-10-21/`.

## Limites e retomada

A escrita foi revisada várias vezes e a navegação real foi exercitada.
Ainda é útil observar um jogador novo montar um personagem com o roteiro;
este trabalho não fez um estudo de usabilidade nem emitiu uma carteira real.
Nenhuma célula da ficha oficial, Apps Script, salário ou permissão Google
foi alterada. As cópias antigas de testes permanecem no estado da limpeza
anterior; não foram recriadas.

O guia ensina as regras padrão e como conferir exceções com o mestre. Não
substitui o livro, não libera capacidades só pela presença de um cartão,
não converte prosa em bônus e não certifica história de aprendizado, alvos,
Alma, datas de missão ou salários. A comparação do corpus geral R51/R52 com
R53 continua na fila independente; não foi resolvida por este texto estático.

Para retomar: verificar branch, remoto e PR 68; ler este relatório e
GUIAS-DE-USO.md. Runtime publicado `268d326`; commits posteriores apenas de
documentação não exigem novo deploy. Testar `GC:guia criar`, `GC:guia planilha`
e `GC:guia ficha` se houver alteração nova; repetir apenas a cobertura
correspondente. Preservar os nomes das abas e preferir títulos que expliquem
a tarefa. Merge da PR permanece pendente, sem autorização específica nova.
