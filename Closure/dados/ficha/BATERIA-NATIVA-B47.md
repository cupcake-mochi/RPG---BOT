# Bateria nativa B47 · 18/10/2026

A continuação de 28 casos avançados está em
`pesquisa/validacao/2026-10-18-b47-avancados/` (28 análises/143 páginas no
Discord). Ela usa arquivos técnicos do contrato e não é um segundo recálculo
nativo destes Sheets. As seis cópias e suas quatro aprovações continuam
preservadas; a aprovação extra temporária da continuação foi removida.


Seis cópias integrais de uma ficha B47 nativa, com 22 abas. A oficial foi
somente lida. Entradas foram preenchidas pelo Sheets e os XLSX foram
exportados depois do cálculo nativo; não houve importação, LibreOffice ou
execução/publicação de Apps Script. IDs das cópias e arquivos ficam na entrega
local ignorada `src/var/testes-b47/`, fora do pacote do bot.

**Configuração aplicada depois da preparação:** Mizuki informou o servidor de
teste e autorizou leitura pública por link somente nas seis cópias sintéticas.
Todas têm `anyone/reader`, sem descoberta por busca. O arquivo de campanha não
existia em `src/var/` na Discloud. Foi criado com nome temporário, preenchido,
salvo, relido e só então renomeado para `ficha-campanhas.json`. O arquivo ativo
foi relido idêntico ao preparado: um servidor, quatro aprovações, sem regras
gerais ou nome de campanha alterados. Não houve reinício nem implantação de
código. IDs/cadastro e comprovantes privados ficam fora do Git.

Cada link foi lido anonimamente pelo leitor real do bot e comparado com o
respectivo XLSX: 8.190 chaves e zero diferenças de Campo, com os resultados da
tabela. Outro servidor simulado mantém as quatro aprovações pendentes na 02.
Isso valida acesso/contrato e o cadastro relido. A execução real no Discord foi
concluída depois com autorização, conforme seção abaixo. Evidência de acesso em
`pesquisa/validacao/2026-10-18-b47-bateria-nativa/validacao-links-servidor.json`.

## Casos e resultado esperado

| Caso | Conteúdo | Resultado esperado com as quatro aprovações de teste |
| --- | --- | --- |
| 01 Base | Bastião/Muro/Latente, nível 2; atributos 3/2/2/1/1; 9 Perícias, 2 Ofícios, 2 TR; 2 Famílias Livres e 3 Fechadas | Parcial, sem divergência nem aprovação pendente; Vida 23 |
| 02 Custom aprovada | Perícia Runologia Coruja B47/Inteligência; Melhoria Foco Coruja B47 baseada em Precisão; Forma Agulha Coruja B47 baseada em Projétil; efeito Vida máxima +2 | Parcial, sem divergência nem aprovação pendente; Vida 25, perícia +1, feitiço PE 3, dano 2d8, alcance 18 m |
| 03 MESTRE VIU sem autorização | Mesmas estruturas, nomes Pendente e fonte diferente; checkboxes MESTRE VIU marcadas | Quatro pendências de aprovação; sem divergência mecânica |
| 04 Alterada após aprovação | Cópia de 02, mudando apenas o efeito de +2 para +3 | Vida 26 bate; uma pendência de aprovação exata de efeito.1 |
| 05 Divergência intencional | Cópia de 01 com FICHA!J26 substituído por 999 | Reprova Vida 999; esperado 23 |
| 06 Campanha sem autorização | Cópia de 01 com orçamento de criação 10 na CONFIGURAÇÃO e Destreza 3 | Reprova a regra declarada e o total de 10 contra 9 autorizado |

Os casos 01 e 02 não prometem ficha integralmente aprovada: dados ausentes do
contrato e verificações humanas continuam listados. Nenhum resultado deve ser
forçado a verde. Aprovar o conteúdo custom não transforma a descrição em novos
bônus. Na 02, Forma e Melhoria conservam as bases publicadas; o +2 de Vida tem
seu próprio registro estruturado e aprovação.

As aprovações sintéticas cobrem somente os três cadastros e o efeito exato de
02. Nome, base ou conteúdo relevante alterado requer nova decisão. As cópias
03 e 04 não devem ser aprovadas durante esta rodada. Não mudar regras globais
de um servidor real para fazer a 06 passar.

## Execução real no Discord · concluída nesta bateria

Na versão já publicada, passaram 13 análises: seis por link, seis por XLSX e
uma reanálise após encerramento dos controles. Foram dois comandos slash (link
e arquivo da 02) e onze `GC:ficha`. Os seis pares tiveram resumo idêntico.

| Caso | Erros observados | Aprovações pendentes observadas |
| --- | ---: | ---: |
| 01 | 0 | 0 |
| 02 | 0 | 0 |
| 03 | 0 | 4 |
| 04 | 0 | 1 (somente efeito.1) |
| 05 | 1 (Vida 999; correto 23) | 0 |
| 06 | 3 (regra e orçamento não autorizados) | 0 |

Na 02, as seis páginas foram abertas; perícia +1 e feitiço PE 3/2d8/18 m
corresponderam ao esperado. As quatro setas e o seletor funcionaram. O painel
voltou ao resumo e desabilitou os quatro botões após dez minutos; uma nova
análise reabriu controles, e o callback Próxima abriu a página 2.
**Não exercitado:** segunda pessoa no painel. Os demais casos ampliados do
roteiro externo também não fazem parte desta bateria. Sem modelos pagos,
reinício, implantação da PR 65 ou alteração da oficial durante esses testes.
Evidências agregadas: `pesquisa/validacao/2026-10-18-b47-discord/`.

## Reprodução no Discord

1. As quatro aprovações de teste já estão instaladas no servidor escolhido.
   Para reproduzir em outro ambiente, instalar somente os quatro hashes,
   preservando outras campanhas e aprovações.
   `ferramentas/ficha_campanha.py inspecionar/aprovar` aceita os XLSX nativos.
   Nunca publicar esse cadastro operacional no Git.
2. Rodar `/ficha analisar` com cada link legível pelo bot e repetir com o XLSX
   correspondente. `GC:ficha` é alternativa. Sem necessidade de chamar IA.
3. Comparar resumo e páginas de revisão, atributos/treinos, habilidades,
   conferidos e limites. Nos seis casos, link e XLSX devem concordar.
4. Na 02, verificar a ausência das quatro pendências específicas e os números
   da tabela. Na 03, confirmar que MESTRE VIU não as remove. Na 04, confirmar
   que mudar o efeito reabre somente sua aprovação.
5. Folhear seletor e setas, com outra pessoa no canal; após dez minutos sem
   interação, fazer uma nova análise para reabrir os controles.

Links privados abrem para o proprietário, mas não para o GET anônimo do bot.
As seis cópias sintéticas desta rodada já receberam essa leitura com autorização;
a oficial não teve permissões alteradas. O XLSX continua disponível.

## Defeito encontrado durante a preparação

O molde nativo tem defaults em cartões custom vazios:
`custom.caminho.campo.troca_pericias_por_arma=Não`,
`custom.caminho.campo.treino_de_arma=Todas` e
`custom.trilha.campo.base_do_livro=Nenhuma`.
O bot publicado tratava esses menus, mesmo sem nome, como dois cadastros
inválidos e pedia aprovação de definições inexistentes.

O bot agora ignora somente esses defaults no teste de ativação de seus
respectivos cartões. Nome, valor numérico explícito zero, conteúdo diferente
ou MESTRE VIU continuam ativando o cartão. Os defaults permanecem nos dados e
na assinatura de qualquer definição ativa. Três regressões cobrem ausência,
ativação e invalidação da aprovação após mudança de base.

Para que as fichas também funcionem com o runtime já publicado, esses três
menus não utilizados foram limpos nas cópias de teste. Isso não altera a
oficial, não concede benefícios e não apaga campos de um cadastro ativo.
A correção de código tem publicação separada; não se presume que esteja
instalada por causa da criação das cópias.

## Validação desta rodada

- Seis exportações nativas lidas: 8.190 chaves em cada uma, sem erro de cache,
  fórmula ou contrato incompleto. Resultados locais correspondem à tabela.
- Caso 02 conferido sem aprovação: quatro pendências. Com aprovação sintética
  exata: nenhuma pendência de aprovação e nenhuma divergência.
- Suíte: 817 executados em 206,224 s; 816 passaram, um online opcional pulado.
  Módulo de cobertura: 15 testes aprovados, em 6,700 s.
- Sem chamadas pagas, mensagens ao Discord, alteração da oficial ou
  implantação do patch durante a preparação. Configuração e leitura anônima
  posteriores foram verificadas conforme registro acima. A execução posterior
  de 13 análises reais e do painel tem evidência separada, sem repetir a suíte
  ou regenerar o ZIP: esta rodada final mudou somente documentação.
