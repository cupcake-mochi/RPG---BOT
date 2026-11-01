# Encerramento da fila durante a limpeza

## Falha reproduzida e correção

Um cliente pode cancelar a última consulta enquanto seu trabalho ainda está
limpando recursos. Outro pedido com a mesma chave espera essa limpeza para
não iniciar uma operação concorrente. Essa espera acontecia depois da primeira
verificação de fila aberta.

Se o serviço encerrasse durante essa espera, o segundo pedido podia acordar e
admitir trabalho novo com `fechada=True`. O teste reproduziu a falha no código
anterior: o substituto devolveu o resultado fictício em vez de recusar com
`Ocupado`. Não foi observado incidente em produção ou acesso a dados reais.

Agora a admissão reconfere o encerramento após a limpeza. O escalonador também
não inicia trabalhos quando a fila está fechada. Nenhum prazo, limite de cota,
regra mecânica, esquema de banco ou permissão mudou.

Dois testes novos exercitam a corrida e seu controle: encerramento durante a
limpeza recusa o substituto sem chamar sua função; mantendo a fila aberta, o
substituto aguarda a limpeza e executa uma vez. Os15 testes da fila passaram.
O primeiro teste foi executado antes da correção e falhou pela ausência da
recusa esperada; não se alteraram as expectativas existentes.

## Trabalho local que continua possível

O Google indisponível limita os ensaios reais; não bloqueia toda a etapa7.

| Frente | Próximo trabalho | Dependência |
| --- | --- | --- |
| Integração dos domínios | Contrato REST atual cobre financeiro/progressão; mapear a leitura e integração dos demais perfis já existentes no produtor | Código e contratos, pode começar offline |
| Ativação verificável | Definir como o backend comprovará responsável/instalação sem confiar em JSON ou checkbox do navegador | Desenho de contrato antes de qualquer nova API/escopo |
| Concorrência | Revisar a fronteira entre observar e escrever no Google; a fila local não é compare-and-swap contra edição do jogador | Desenho e testes locais; prova final nativa |
| Falhas e recuperação | Continuar revisão dirigida de cancelamento, reinício, revogação e estado incerto | Pode avançar offline com reprodução independente |
| Eventos reais | Medir preparo/instalação e observar abertura, edição, missão, gasto/correção | Sessão Google autorizada e nova descartável |

A correção deste documento trata apenas o encerramento da fila. Não encerra
as outras frentes, não libera criação e não comprova os eventos Google.
Etapa7 parcial e8–10 pendentes. Código da Carteira separado da produção.

Para reproduzir, com o núcleo e as dependências preparados, em `Closure/src/`:

```sh
../.venv/bin/python -m unittest testes.test_carteira_fila
../.venv/bin/python -m unittest discover -s testes
```

Modelo recomendado: Sol/High para implementação/testes; Astra/High para
contrato de ativação e concorrência; Medium para conferência documental.
