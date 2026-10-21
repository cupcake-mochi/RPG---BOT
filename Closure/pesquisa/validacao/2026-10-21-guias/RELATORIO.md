# Guias de uso, escrita e limpeza · 21/10/2026

## Código e escopo

Branch `codex/guias-de-comandos`, partindo de `main@1e99150` (PR 67 já
mesclada). Código publicado: `f0c9fccdbff8b438dd0d87f3f392256e33e59c36`.
[PR 68](https://github.com/cupcake-mochi/RPG---BOT/pull/68), sem merge.
Não houve reset, force-push, chamada paga ou alteração da ficha oficial.

`/guia`, `/ficha guia`, `GC:guia ficha` e os aliases descritos em
[GUIAS-DE-USO.md](../../../docs/GUIAS-DE-USO.md) oferecem nove assuntos e
18 páginas. A orientação é estática; não executa os comandos ensinados.
Pela barra, é privada; no chat, pública. Os menus continuam acessíveis nos
assuntos de uma página. Os controles expiram após dez minutos sem uso;
um reinício exige abrir outro guia, como nos painéis de ficha.

Foram revistas as saídas fixas de comandos, ajuda, painel de ficha,
paginação, clima, livro e dados pessoais, além das orientações existentes
de mídia/conversa. A revisão não certifica toda fala futura dos modelos.
Cards, prompts, mecânica e permissões administrativas foram preservados.

## Testes e revisão

| Verificação | Resultado |
|---|---|
| Suíte completa no GitHub, código final | **896 executados, 895 aprovados, um online opcional pulado**, 196,050 s. [Execução](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/39596997331) |
| Módulos afetados, cópia temporária dos fontes | 125 executados, 124 aprovados, o mesmo online opcional pulado |
| Guia, Discord e painel no código extraído do ZIP | 91 aprovados |
| Ajuste final do rótulo de página, fontes e ZIP | Cinco testes do guia aprovados em cada execução; incluído na suíte completa acima |
| Auditoria do pacote | 77/77 arquivos idênticos aos fontes; nove arquivos de runtime diferentes da instalação anterior |

A primeira execução local no HD externo foi interrompida pela lentidão.
A cópia temporária tornou a execução viável. Uma rodada completa ainda
falhou na expectativa antiga que exigia somente `analisar` em `/ficha`.
O teste foi atualizado para os dois subcomandos reais, sem modificar
expectativas mecânicas para obter aprovação. Na revisão visual, o seletor
mostrava `1. 1. Prepare…`; o rótulo foi corrigido e reensaiado.

Os testes novos verificam navegação, troca de assunto, limites dos embeds,
acentos/aliases, resposta privada, silêncio da IA, ausência de leitura de
ficha e encerramento dos controles. O aviso padrão da paginação de ficha
continua igual; o guia recebe sua própria orientação de reabertura.

## Discloud e Discord

Publicação autorizada no app **1773761486581**, Guias do Ciclo.
Backup completo privado baixado antes da alteração; não foi versionado.
Primeira publicação iniciou às 09h04; o ajuste de numeração foi publicado
em seguida. Startup final: **09:08:00,439**, online em cinco servidores,
sem erros de aplicação no log observado.

Pacote final: SHA256
`9b32faa18044452cd16733a1cbdfba522d16bdcc140651b3d36d0fd9073e6a84`.
Não contém `.env`, bancos ou cadastro de campanha. O núcleo local de conversa
era mais antigo que o instalado; o pacote preservou os bytes do núcleo de
produção obtido no backup, em vez de substituí-lo pelo cache antigo.

Na hospedagem, uma conferência somente de leitura confirmou os hashes dos
nove fontes novos, do núcleo preservado, do `.env` e do cadastro de campanha.
Os dois bancos (`closure_lab.db` e `src/var/bot.sqlite3`) retornaram `ok`
no `PRAGMA quick_check`. Não houve edição das variáveis ou dos recursos
de hospedagem (700 MB/0,68 vCPU). Detalhes sem segredos em [pacote.json](pacote.json).

No tópico autorizado **1561410667108368575** do servidor
**1357866906341736488**:

- [GC:guia ficha](https://discord.com/channels/1357866906341736488/1561410667108368575/1562436703162208267): envio por link/XLSX e botão Próxima para a explicação das cores.
- [GC:ficha guia, versão final](https://discord.com/channels/1357866906341736488/1561410667108368575/1562437655986438245): seletor sem numeração duplicada, troca para Customizações, página de aprovação exata e troca para Clima. No assunto de uma página, as setas ficam desativadas e o menu de assuntos continua disponível.
- `/guia` foi escolhido entre os comandos das **Guias do Ciclo**, sem confundir com outros apps. Respondeu com o início e o aviso **Só você pode ver esta mensagem**. `/ficha guia` também apareceu no registro real de comandos.

Não foi necessário chamar modelo ou repetir a bateria de contas da ficha
oficial para testar uma orientação estática. Timeout e cliques encerrados
foram testados automaticamente; não houve espera nativa de dez minutos nem
um novo ensaio com segunda pessoa.

## Limpeza das planilhas de teste

Somente depois da publicação e dos ensaios foram removidas **23 cópias**:
seis B47, seis R53, cinco TR nativas, quatro da validação de 14/10 e duas
da Arquivista. Todas foram confirmadas na **lixeira recuperável** pela
interface. A lixeira não foi esvaziada. IDs e títulos: [limpeza.json](limpeza.json).

Quatro cópias antigas compartilhadas — Teste 1/Kaori, Teste 2/Vanguarda,
Teste 3/Incursor e Teste 4/Corpo Amaldiçoado — continuam acessíveis:
o Drive desativa individualmente a opção de lixeira por falta de permissão.
O menu Organizar não ofereceu remoção só da lista. Não foram alteradas
permissões, compartilhamento ou propriedade para contornar esse bloqueio.

As três planilhas indicadas pelo usuário foram conferidas por ID e
preservadas: **Ficha - Era da Revolução**, **Ficha - Ciclo Maldito** e
**Arquivista · Era da Revolução**. Também permaneceram os backups,
Arquivista · Mii and Ki, Aparências - BOT, testes antigos sem relação
com os bots e cópias de QA do produtor, que não integram esta limpeza.

Os links das cópias B47/R53 nos relatórios anteriores agora são históricos.
Uma bateria futura deve preparar novas cópias sintéticas ou restaurar
explicitamente uma cópia necessária; nunca usar a ficha real como fixture.
Manifestos completos e capturas ficam no diretório ignorado
`src/var/guias-2026-10-21/`; não foi versionado um inventário geral do Drive.

## Retomada e limites que permanecem

Conferir remoto e PR 68 antes de editar. Runtime publicado é o SHA acima;
commits posteriores de documentação não significam novo deploy. O guia está
implantado; revisão/merge desta PR continuam separados.

Para verificar o uso, abrir `/guia`, escolher **Ficha** ou **Customizações e
mestre**, ou enviar `GC:guia ficha` no tópico de testes. O bot não escreve
nas planilhas, não aprova prosa como bônus e não aceita MESTRE VIU como
autorização. Aprovações reais e requisitos narrativos continuam com o mestre.

A comparação integral do corpus geral R51/R52 com o livro R53 e os demais
limites descritos na retomada R53 não foram resolvidos por este guia. Não
declarar o projeto inteiro validado por esta rodada. Para remover as quatro
cópias compartilhadas restantes, depende de acesso do proprietário.
