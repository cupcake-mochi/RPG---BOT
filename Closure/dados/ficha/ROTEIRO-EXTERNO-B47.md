# Validação externa e publicação B47

Estado em 18/10/2026: PR 64 mesclada e implantação autorizada concluída.
Startup, backups e igualdade dos arquivos instalados foram conferidos.
A bateria nativa de seis fichas passou depois, com autorização do usuário:
13 comandos reais no Discord (seis links, seis XLSX e uma reanálise), seis
pares com resumos idênticos. Cobertos base, custom aprovada, MESTRE VIU sem
permissão, efeito alterado após aprovação, Vida adulterada e campanha divergente.
Setas, seletor, dez minutos de inatividade e reabertura também passaram.
Evidências: `pesquisa/validacao/2026-10-18-b47-discord/` e
[BATERIA-NATIVA-B47.md](BATERIA-NATIVA-B47.md).

**Continuação avançada concluída:** mais 28 análises por XLSX e 143 páginas
conferidas no Discord, com todos os diagnósticos-alvo esperados. Foram casos
sintéticos de uma aba ANALISE, incluindo recusas de leitura, Origem, Trilha,
efeitos, curingas, entidades, Controle, Máxima/Alma e teto de objeto/Liberação.
A aprovação extra de Trilha foi temporária; o cadastro original de quatro
aprovações foi restaurado e relido idêntico. Relatório e casos em
`pesquisa/validacao/2026-10-18-b47-avancados/`.

**Ainda externos:** segunda pessoa no painel e recálculo nativo dos cenários
ampliados por link/XLSX. A troca independente avançada usou CD por zero;
Vida rolada com rolagem ausente permanece no roteiro abaixo. As 28 análises
comprovam o consumidor, não as fórmulas nativas. Cores locais por página e
trabalho fora do loop foram testados no código/ZIP da PR 65, ainda não no
runtime real. A PR 65 continua em rascunho e não foi implantada.
Não repetir publicação. Nova campanha de jogo, aprovações ou mensagens fora
do tópico/bateria autorizados exigem escopo específico; a conta não usa modelo.

## Preparação do operador

1. Rever a PR e o SHA final em `docs/RETOMADA-B47.md`. Fazer backup do estado
   operacional: banco, chave, variáveis e `src/var/ficha-campanhas.json`.
2. Usar a versão já implantada; não criar outra instância. Nenhum modelo é
   necessário para analisar/navegar. A publicação preservou o estado anterior.
3. Usar cópia sintética da B47 no Sheets. Não executar construir/continuar na
   oficial, importar XLSX no Google ou mudar suas permissões. O acesso por link
   precisa já estar autorizado; XLSX pode ser baixado normalmente da cópia.
4. Registrar versão da ficha, SHA do bot e servidor de teste, sem publicar IDs,
   links privados, cadastro real ou mensagens do jogador no Git.

## Casos por link e XLSX

Para cada caso, aguardar o cálculo no Sheets, analisar pelo link e pelo mesmo
arquivo baixado (Arquivo → Fazer download → Microsoft Excel). Comparar campos,
pendências e páginas; diferenças de horário/guia não mudam as contas.

| Caso | Preparação na cópia/arquivo de ensaio | Esperado |
| --- | --- | --- |
| Base B47 | Personagem sintético nível 2 completo | Contas reconhecidas conferidas; resumo parcial por lacunas reais, sem aprovação integral. |
| Resultado adulterado | Trocar Vida máxima por 999 no resultado exportado do arquivo de teste | Divergência vermelha em `vida_max`; as outras contas continuam disponíveis. |
| Exportação incompleta | Retirar uma chave da ANALISE somente no arquivo de teste | Pendência de exportação incompleta; ausência não vira zero. |
| Fórmula sem cache | Salvar fórmula sem resultado calculado no arquivo de teste | Erro de leitura claro; não apresentar aprovação. Isso é um caso sintético de arquivo, não exportação nativa do Google. |
| Origem incompatível | Receptáculo/Conflito com Conselho Interior | Requisito de Coexistência apontado; contas dependentes da Origem não certificadas. |
| Trilha herdada | Trilha custom válida, Caminho associado e BASE DO LIVRO Invocação Principal | Sem aprovação: pendência, sem presumir perfil padrão. Após aprovação exata: 5 abertas/2 Livres; Não autônoma acrescenta 1 a ambas. |
| Trilha modificada | Alterar sua base de Principal para Parceria depois da aprovação | Aprovação reaberta; mestre precisa analisar a nova definição. |
| Competência custom | Especialização sem treino ou antes do nível 10 | Divergência e ausência de confirmação do bônus/quantidade dependente. |
| Troca independente | Vida rolada ligada, rolagem ausente e efeito trocar Vida máxima por 0 | Valor fixo 0 conferido; rolagem e aprovação da fonte permanecem pendentes. |
| Efeito inválido | Valor não numérico em efeito de CD/ataque | Diagnóstico da linha; conta dependente não certificada, painel e contas independentes funcionam. |
| Curingas | Perícias `Runa*` e `Runas`, INT 1; efeito +7 só em Runas | Bot espera 1/8. Se o produtor aplicar 7 à primeira, registrar divergência; não relaxar o consumidor. |
| Controle | Caso mínimo de LACUNAS-PRODUTOR-B47.md: ataque +6 e Controle CD 14 | Fórmula conhecida com CD 12 recebe pendência específica; outro número incorreto reprova. Sem alegar que a fórmula foi corrigida. |
| Máxima válida | Nível 17, Projétil, Precisão; Mira Livre | 25 PE, 1 de 8 e 24d8; pontos não compram nem retiram dados. |
| Máxima incompatível | Toque com Longe ou Projétil com Inescapável | Divergência; montagem e dados dependentes não aparecem como conferidos. PE permanece independente. |
| Máxima com Alma | Nível 17, Projétil, Toca a Alma | 3 de 8; 12d8 quando exportados. Fórmula fixa de 24d8 recebe pendência específica; autorização da Regra continua humana. |
| Teto de objeto | Classe 3, Projétil e Quebra Coisa, preços normais | Base 6d8; 7d8 excede o teto quando dobrado. Divergência do produtor não autoriza relaxar o bot. |

## Campanha e aprovação reais

As quatro aprovações sintéticas desta bateria foram instaladas e lidas pelo
runtime; 02/03/04 confirmaram aprovação exata, MESTRE VIU sem poder de autorização
e reabertura do efeito alterado. Não representam aprovação de personagem real.
Outro servidor foi simulado localmente, não exercitado no Discord nesta rodada.

No computador do operador, em `Closure/`, cadastro privado e servidor corretos:

```bash
.venv/bin/python ferramentas/ficha_campanha.py inspecionar --servidor ID --ficha ANALISE.csv
.venv/bin/python ferramentas/ficha_campanha.py aprovar --servidor ID --ficha ANALISE.csv --campo custom.trilha --por 'mestre/registro da decisão'
.venv/bin/python ferramentas/ficha_campanha.py aprovar --servidor ID --ficha ANALISE.csv --campo efeito.1 --por 'mestre/registro da decisão'
```

Também aceita XLSX calculado em `--ficha`. O arquivo deve corresponder à
definição que o mestre examinou. Conferir a mesma ficha antes/depois da
aprovação, alterar um campo e conferir novamente. MESTRE VIU não deve autorizar
nada. Outro servidor não herda aprovação ou regra. As assinaturas de Trilhas
com base agora vinculam também o registro publicado da base; aprovações de
rascunhos anteriores precisam ser refeitas quando o hash mudar.

## Painel e comandos

Executados: ambos os comandos, link/XLSX, as seis páginas da 02, revisões da
03/05, quatro setas, seletor, encerramento e reabertura. A rodada avançada
acrescentou entidades e conferiu as 143 páginas dos 28 ensaios. Houve esperas
expiradas na automação, resolvidas conferindo o estado visível e retargetando
controles; não se comprovou falha de conteúdo por isso. Falta navegação por
uma segunda pessoa no Discord. A nova semântica de cores da PR 65 precisa
ser observada depois de implantação autorizada, sem repetir contas já cobertas.

Exercitar `/ficha analisar` e `GC:ficha`: link e anexo XLSX. Verificar resumo,
revisão, TR/perícias, habilidades, entidades e limites; primeira/anterior/
próxima/última e seletor direto. Outra pessoa no canal deve conseguir folhear.
Depois de dez minutos sem interação, o relatório volta ao resumo e encerra
controles; nova análise abre novos controles. Nenhum clique deve reler a ficha,
invocar modelo ou modificar o cadastro da campanha.

Anotar cada caso como passou/falhou/não executado com campo e esperado/obtido.
Testes locais não encerram esse roteiro nem comprovam autorização real do mestre.
