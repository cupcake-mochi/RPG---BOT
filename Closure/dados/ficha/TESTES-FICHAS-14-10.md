# Fichas de teste no Google (14/10/2026)

**Rodada seguinte, ANALISE 2:** Mizuki informou não ter fichas em uso e autorizou preencher cópias.
Quatro cópias nativas com feitiços/entidades foram calculadas, lidas e conferidas fora do Discord;
originais preservadas. Mizuki confirmou depois as quatro aprovadas no Discord, com capturas de 22h34–22h35.
Domada: vida 34/Defesa 13 e duas notas de Buff; criação: vida 98/Defesa 14. Resultado/limites em
`../../pesquisa/validacao/2026-10-14-analise-v2/relatorio.txt`. A navegação por páginas foi preparada após
essas capturas e também foi confirmada pelo Mizuki às 23h05.

**Reteste concluído pelo Mizuki em 14/10:** fez Commit e Rebuild na Discloud e confirmou que os quatro
testes funcionaram no Discord, com captura dos painéis. A confirmação é do usuário; o agente não acessou
o Discord. As pendências e correções abaixo descrevem o histórico anterior a esse reteste. Isso valida
o envio do comando, a leitura das cópias e os painéis publicados; as quatro cópias continuam sem cartas
de magia preenchidas e não validam essas contas.

Cópias da ficha oficial, preenchidas e testadas pelo Mizuki no servidor com `GC:ficha` e o link.
Inicialmente só tínhamos Testes 1 a 3. Em seguida, Mizuki enviou a Teste 4 — Corpo Amaldiçoado,
e a leitura pública da ANALISE foi conferida junto dos valores da planilha pelo conector.

Correção local de 14/10: Defesa fixa passou a distinguir 0, a fórmula normal e valor adulterado; treino extra
repetido aparece uma vez; sem nome, o título usa Caminho e nível conhecidos. Não foi implantado nesta revisão.

| Ficha | Esperado | O bot deu | Situação |
| ----- | -------- | --------- | -------- |
| Teste 1 - Kaori (Bastião 2, Descendente) | aprovada, vida 23, PE 8, Integridade 26, Defesa 13 | aprovada, com os quatro números | ok |
| Teste 2 - Vanguarda com pendências (nível 10, Encarnado com Duas Vidas, Revestimento 2 + Broquel, Grau 4, 1 ponto sobrando) | reprova pelo Grau, avisa o ponto, treino extra pro mestre | reprovou por "Pede Grau 3", avisou "faltam distribuir 1 de 11" e "Trava Selo de gesto", e o treino extra virou nota | notas repetidas corrigidas localmente; retestar na Discloud |
| Teste 3 - Incursor com erros (nível 14, Restrição corporal com Corpo Debilitado, Besta + escudo Médio, Defesa 19 digitada por cima dos 15 da fórmula) | reprovada | **aprovada**, só com a pendência "Defesa fica 0 por Corpo Debilitado" | corrigido em reprodução local equivalente; retestar a cópia real na Discloud |
| Teste 4 - Corpo Amaldiçoado (Evocador 6, Núcleo Dependente com o PE no Buff) | aprovada | aprovada no servidor e na leitura local | PE 40 correto; acrescentada pendência de Integridade sem barra |

## Fila, na ordem

1. **Corpo Debilitado esconde Defesa adulterada** (`ficha_corretor.conferir_contas`). Com marcante de Defesa 0, a função
   sai antes de refazer a Defesa normal, e qualquer valor diferente de 0 vira a mesma pendência: o jogador honesto (15)
   e o que digitou 19 recebem a mesma resposta. Conserto: refazer a Defesa normal mesmo assim; 0 é conferido, a conta
   normal vira pendência "fica 0", qualquer outro valor é erro de conta. **Concluído localmente**: 0 é conferido,
   15 fica pendente e 19/vazio reprovam na reprodução equivalente ao Teste 3. Inclui Quebradiço e Exaurido,
   Buff e conferência de proteção. Falta retestar a cópia real depois de subir o pacote.
2. **Um treino extra vira três notas.** A ficha mostra "1 a mais" em Perícias, em Ofícios (mesmo com 2 ofícios
   marcados, porque o "a mais" é o mesmo contador) e no resumo. Conserto no bot: juntar numa nota só. Na ficha: o
   "a mais" de Ofícios não devia acender com 2 ofícios (registrado no DIVERGENCIAS-FICHA.md). **Concluído no bot**:
   avisos de Origem com o mesmo excesso viram uma nota, preferindo o resumo; excessos diferentes ou sem
   justificativa não são apagados.
3. **"Ficha de sem nome"** em todas: as cópias não têm o nome preenchido (FICHA!AB2). Não é erro, mas o título podia
   cair no Caminho e no nível ("Ficha de Bastião, nível 2") quando falta nome. **Concluído localmente**:
   só usa Caminho conferido e nível válido; na falta deles, título simples sem inventar dados.
4. **Teste 4 recebida e conferida**: Corpo Amaldiçoado, Evocador 6, Essência 3, Núcleo Dependente com
   Buff de PE 4. PE 40 = 36 do Caminho + 4 da menor: correto, sem pendência de PE. Vida 38, proteção 1
   e Defesa 12 também conferem. **Nova exceção corrigida no bot**: Núcleo Dependente não possui barra
   de Integridade; os 60 mostrados pela ficha não podem constar como conferidos. Fórmula normal vira
   pendência para desconsiderar essa reserva; zero/vazio reconhecem ausência de barra e outro valor reprova.
   A planilha não foi alterada. Retestar o novo aviso depois de atualizar o pacote na Discloud.
5. **A cópia da Teste 3 estava como "Qualquer pessoa com o link, Editor"** e alguém mexeu nela antes do preenchimento.
   **Concluído**: metadados das quatro cópias conferidos. Testes 1, 2 e 4 já eram leitor; Teste 3 mudou de editor
   para leitor e foi verificada pela interface e pelo conector. Colaboradores individuais preservados.
6. **Fichas com customização** (uma aprovada pelo mestre, outra não): esperam a aba CONFIGURAÇÃO na ficha (B47,
   fase 2), as chaves `regra.*`, `efeito.*` e `custom.*` na ANALISE, e no bot o comando do mestre aprovar e a
   conferência por impressão digital. A estrutura do bot já existe (`RegrasDaCampanha`, `Aprovados`).
   Mizuki confirmou que o cadastro fica para essa etapa, junto de CONFIGURAÇÃO; não entrou comando novo de campanha.

## Continuação das contas

As quatro cópias públicas foram relidas depois dos consertos: Teste 1 aprovada; Teste 2 reprovada pelo Grau, com duas
pendências e uma nota de treino; Teste 3 reprovada por Defesa 19 (esperado 0); Teste 4 aprovada com a pendência de
Integridade sem barra e a nota do Buff de PE 4. Nenhuma tem feitiço ou entidade preenchida pelo nome; os números
iniciais das cartas vazias não contam como habilidade. Essas leituras confirmam as regressões, não uma bateria de magia.

O bot passou a conferir parte das montagens independentemente dos avisos, com exemplos numéricos do R51 e alterações
hostis nos testes locais. O que depende de dados ausentes fica declarado como não conferido. A lista para a etapa
CONFIGURAÇÃO/expansão da ANALISE está em `ENTRADAS-FALTANTES-ANALISE.txt`. Falta o reteste na Discloud pelo Mizuki.

Ajuste posterior pedido pelo Mizuki: aprovada com "Falta ou pede atenção" usa amarelo; reprovada mantém vermelho,
mesmo com pendências; aprovada sem pendência usa verde. O aviso genérico "Trava Selo de gesto" foi omitido: a fórmula
da ficha só detecta escudo, sem verificar o Selo escolhido. A Teste 2 passa a ter uma pendência (ponto sobrando),
preservando erro de Grau e nota de treino. A Teste 4 passa a aparecer amarela pela Integridade sem barra.

Observações da outra conversa: o Revestimento 2 com Grau 4 só entrou trocando o Grau pra 3, escolhendo e voltando,
porque o menu da ficha não oferece; a Besta com escudo some o escudo do menu, então foi escolhido antes. O `.venv` do
bot não roda na máquina virtual dela (Python 3.10), por isso ela leu pela aba ANALISE com o conector do Sheets.
