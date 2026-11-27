# Versão rápida da ficha · o que muda na Closure (26/11/2026)

A ficha (`Ficha---RPG-JJK`, PRs 155, 156 e 157, main `85a596b`) ficou mais leve em três etapas. A ANALISE
continua com as mesmas 18.500 chaves, nas mesmas linhas e com a mesma parte. **11.202 delas agora vão em branco:**

| Etapa | Chaves em branco |
|---|---|
| 3 e 4 · cartões de preencher | `r53.<cartão>.*` (os 251 cartões). Os três cabeçalhos (`r53.montagem.esquema`, `r53.entrada.campos`, `r53.versao.campos`) continuam com valor |
| 5 · CONFIGURAÇÃO | `custom.melhoria.*`, `custom.restricao.*`, `custom.forma.*`, `aviso.custom.(melhoria\|restricao\|forma\|tipo_entidade\|talento_entidade).*`, `custom.tipo_entidade.N.(base\|mestre_viu\|definicao)`, `custom.talento_entidade.N.(base\|mestre_viu\|requisitos)` |

A lista foi tirada comparando a ANALISE gerada antes da etapa 3 (`a4a5a20^1`) com a da main. A regra do
`testes/test_versao_rapida.py` pega exatamente essas 11.202.

## O que a Closure faz agora

- **Cartões:** quando todas as chaves `r53.<cartão>.*` vêm em branco, é a versão rápida. A Closure não recalcula
  nada dos cartões, não acusa erro nem aviso, e escreve uma linha em "não conferido" se algum cartão tiver nome
  (as contas, peças e avisos dos cartões ficam com o mestre). A oficial antiga manda os menus padrão até no cartão
  vazio (Projétil, Classe 1), então continua no caminho de sempre.
- **Tipo e talento de entidade:** a caixa MESTRE VIU saiu. A chave em branco não é mais defeito nesses dois
  cadastros; nos outros (Família, Perícia, Origem…) continua sendo. A aprovação do mestre continua igual.
- **Melhorias, Restrições e Formas custom:** a linha toda vem em branco, então não vira cadastro. Nada mudou no
  código para isso.

## O que não mudou

- Fichas oficiais antigas: mesmas conferências de antes.
- PR 143 (preencher pelo site): as faixas que ela lê e escreve (CARTEIRA, FICHA, FICHA PESSOAL, DADOS_PROGRESSAO,
  DADOS_CONFIG, DADOS_CUSTOM CP:CS, ANALISE A1:B8, DADOS DL:DM) estão iguais nas duas versões. A INVOCAÇÕES (que
  ganhou 11 linhas por fileira) e a CONFIGURAÇÃO custom não são tocadas por ela.
- Os endereços que a Carteira lê na CONFIGURAÇÃO (C38:P46, K81:P90) também não andaram.
