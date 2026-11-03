# Publicação da consulta e da clareza da análise

Concluída em **30/10/2026, às 23:23:20,452 (Brasília)**, no app existente das Guias do Ciclo (`1773761486581`). Runtime publicado: **`229e539416333896a723c21cf3f0e7d2799f6c5d`**. Este registro e a atualização da fila são posteriores e apenas documentais: não republicar por causa deles.

## O que foi entregue

- [PR85](https://github.com/cupcake-mochi/RPG---BOT/pull/85), merge `c635ac2f9f15abb9152799277c6bf80de974f3ae`: categorias CE 1/2/3, explicações de cadastros e cartões e recuperação de fontes para adaptar feitiços. A lore da Era não limita o acesso às regras.
- [PR86](https://github.com/cupcake-mochi/RPG---BOT/pull/86), merge `2ff90a169dc4ca2ebd277fca705e6c1a9f875d23`: consulta R60/v0.369 e revisão geral de mensagens PT/EN. Erro, pendência e observação são explicados separadamente; observação não é chamada de ajuste obrigatório.
- [PR87](https://github.com/cupcake-mochi/RPG---BOT/pull/87), merge do runtime acima: rótulos legíveis e orientação de recálculo sem repetir o parágrafo inteiro em cada item. Resultado ausente informa o valor calculado pelo bot; o resumo orienta preservar fórmulas e obter nova análise/XLSX.

A consulta usa **R60/v0.369**, 576 trechos, importados de JJK---Project `f87f7e21c881babfda60e06be2de374a2904b03a`. O commit posterior `aed0e5636359f6dd9f127f5c3ac54fe4ecb3d385` só registra publicação, sem diferença nas fontes importadas. A análise mecânica continua R53 e no legado comprovado. Não houve afrouxamento de guardas, alteração de aprovação ou incorporação das branches da Carteira viva.

## Testes

- Suíte completa final: **990 executados, 989 aprovados, um online opcional pulado, zero falhas**, 188,902 s. [CI41159413560](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/41159413560), código `d330cd1b87c3cd4ac766439c5ed2f2bed1d13232`, concluído em 30/10 às 23:22:09 Brasília.
- Antes do último acabamento, CI41158622595: 989 executados/988 aprovados/um opcional. A suíte local da sincronização teve 987/986/um opcional, zero falhas; baterias de apresentação finais: 72/71/um opcional e 35/35 no acabamento.
- Núcleo presente, 14/14 comparações QuickJS/Node. Auditoria de fontes: **498/498**, nenhuma regressão; referências mecânicas e catálogos preservados. Isso comprova recuperação das fontes, não respostas finais de modelo.
- Falhas intermediárias e sua investigação estão em [consulta R60](CONSULTA-R60-2026-10-30.md) e [correções iniciais](CORRECAO-ANALISE-E-CONSULTA-2026-10-30.md). Expectativas de redação envelhecidas foram atualizadas mantendo contas e requisitos; escapes indevidos foram corrigidos.

## Backup, pacote e preservação

Dois backups privados foram criados, baixados e validados antes dos respectivos envios. Contêm `.env`, `closure_lab.db`, `src/var/bot.sqlite3` e `src/var/ficha-campanhas.json`; nenhum desses conteúdos foi incluído no Git ou no pacote de atualização.

| Backup | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Antes da atualização inicial, 22:48 | 267 | 3346132 | `17e2cbe6eb16a74f405a084b028c5fd265e8a9cdb863313ff5a93978a4a9038f` |
| Antes do acabamento, 23:18 | 269 | 3390054 | `2db326c57397ecf512b519522712accf7182f6b779afaa443becff559573f148` |

Pacote final gerado por `ferramentas/empacotar.py`, com núcleo preparado: **91 arquivos, 1851359 bytes**, SHA-256 `e6a4ec85fb85a622c5f8d9fa079ce3af2c969be256eaa82f2553d57dd0edd435`. Todos os arquivos do ZIP correspondem aos fontes; **91/91 arquivos instalados correspondem ao ZIP**, nenhum ausente ou divergente. Não contém ambiente, bancos, campanha ou dados de jogador.

Envio pelo Commit no app existente, com build automático da plataforma, sem Rebuild separado. O primeiro envio que ficou parado não foi aplicado; a conexão foi restabelecida e a versão `2ff90a1` entrou às 23:13:48. A conferência visual motivou o acabamento final, publicado às 23:23:20. Logs finais: seis servidores, zero erros; apenas os avisos existentes de bibliotecas de voz não instaladas.

Na primeira publicação, `.env` e campanha ficaram iguais; os bancos íntegros, com diferença apenas no estado do painel climático atualizado pela rotina normal (identificadores, canal, dia e mensagem preservados). **Na publicação final, `.env`, campanha e todas as tabelas dos dois bancos ficaram idênticos ao segundo backup**, com integridade `ok`. A comparação usou contagens e hashes, sem expor os valores. As variáveis da plataforma não foram editadas; não foi feita uma nova comparação independente do ambiente efetivo do processo nesta rodada.

## Conferência no Discord

No tópico Testes autorizado, após a publicação final:

- `GC:ping`: R60/v0.369, 576 trechos, 42 ms; mensagem `1565914076922642503`.
- `GC:ficha` com XLSX inteiramente fictício: **3 erros, 17 pendências e zero observações**, iguais ao ensaio local; mensagem `1565914282334363698`.
- Casos intencionais: espaço no final do nome custom, Origem vinculada inválida e Melhoria Média em Classe 0. O painel explica cada um, preserva os alertas e mostra as orientações gerais de leitura.
- Navegação e rótulos da página Correções e revisão conferidos após o acabamento. Resultado ausente agora usa uma frase curta em vez de repetir toda a instrução de recálculo.

Sem chamada paga a modelo, sem alteração em oficial/jogador e sem novo ensaio nativo de recálculo Google. O XLSX é uma fixture sintética, não uma exportação nativa do Sheets. Não afirmar que as respostas conversacionais do modelo foram novamente certificadas.

## Pendências reais

- **Produtor da ficha:** metadados da coluna C de ANALISE podem apontar à célula antiga após mudança de layout. Exemplo: `passiva.1.categoria` na linha 2809 lê `FICHA AMALDIÇOADA!F392` pela fórmula de B, mas C descreve F379. Afeta a indicação de localização, não o valor lido por chave/B. O encaminhamento está no relatório de correção; não editar manualmente a ficha do jogador.
- **Bot:** respostas finais de modelo não foram ensaiadas nesta rodada. Continuam os limites documentados de cobertura mecânica e dados não exportados; a suíte verde não significa conferência integral da ficha.
- **Mestre:** aprovação real, aprendizado/histórico, requisitos livres, efeitos narrativos, distribuição entre alvos e interações não automatizadas continuam exigindo revisão humana. MESTRE VIU não concede aprovação.
- **Carteira viva:** etapa 7/PR84 e produtor PR31 permanecem separados; esta publicação não os mescla nem os implanta.

Para retomar, conferir remoto e árvore local, ler o topo da fila e este registro. Não repetir publicação, suíte extensa ou chamadas pagas por rotina. Backups e evidências privadas ficam fora do Git em `/home/mizuki/.local/share/guias-ciclo/publicacao-pr85-20261030`.
