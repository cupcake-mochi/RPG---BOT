# Fichas de teste no Google (14/10/2026)

Três cópias da ficha oficial, preenchidas por outra conversa e testadas pelo Mizuki no servidor com `GC:ficha` e o
link. Mizuki confirmou em 14/10 que só existem as Testes 1 a 3; a Teste 4 ainda não foi criada.

Correção local de 14/10: Defesa fixa passou a distinguir 0, a fórmula normal e valor adulterado; treino extra
repetido aparece uma vez; sem nome, o título usa Caminho e nível conhecidos. Não foi implantado nesta revisão.

| Ficha | Esperado | O bot deu | Situação |
| ----- | -------- | --------- | -------- |
| Teste 1 - Kaori (Bastião 2, Descendente) | aprovada, vida 23, PE 8, Integridade 26, Defesa 13 | aprovada, com os quatro números | ok |
| Teste 2 - Vanguarda com pendências (nível 10, Encarnado com Duas Vidas, Revestimento 2 + Broquel, Grau 4, 1 ponto sobrando) | reprova pelo Grau, avisa o ponto, treino extra pro mestre | reprovou por "Pede Grau 3", avisou "faltam distribuir 1 de 11" e "Trava Selo de gesto", e o treino extra virou nota | notas repetidas corrigidas localmente; retestar na Discloud |
| Teste 3 - Incursor com erros (nível 14, Restrição corporal com Corpo Debilitado, Besta + escudo Médio, Defesa 19 digitada por cima dos 15 da fórmula) | reprovada | **aprovada**, só com a pendência "Defesa fica 0 por Corpo Debilitado" | corrigido em reprodução local equivalente; retestar a cópia real na Discloud |
| Teste 4 - Corpo Amaldiçoado (Evocador 6, Núcleo Dependente com o PE no Buff) | aprovada | não criada | criar antes de testar |

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
4. **Criar a Teste 4**, ainda inexistente: Corpo Amaldiçoado, Evocador 6, Núcleo Dependente com o PE no Buff.
   Depois testar pelo `GC:ficha`. A conferência local do Buff permanece coberta pelos testes unitários existentes.
5. **A cópia da Teste 3 estava como "Qualquer pessoa com o link, Editor"** e alguém mexeu nela antes do preenchimento.
   Trocar as três existentes pra Leitor; a futura Teste 4 também deve ficar só para leitura. Permissões não foram
   alteradas nesta revisão.
6. **Fichas com customização** (uma aprovada pelo mestre, outra não): esperam a aba CONFIGURAÇÃO na ficha (B47,
   fase 2), as chaves `regra.*`, `efeito.*` e `custom.*` na ANALISE, e no bot o comando do mestre aprovar e a
   conferência por impressão digital. A estrutura do bot já existe (`RegrasDaCampanha`, `Aprovados`).

Observações da outra conversa: o Revestimento 2 com Grau 4 só entrou trocando o Grau pra 3, escolhendo e voltando,
porque o menu da ficha não oferece; a Besta com escudo some o escudo do menu, então foi escolhido antes. O `.venv` do
bot não roda na máquina virtual dela (Python 3.10), por isso ela leu pela aba ANALISE com o conector do Sheets.
