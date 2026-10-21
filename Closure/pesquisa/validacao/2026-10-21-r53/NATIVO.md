# Ficha nativa atual · 21/10/2026

Cópia nova da oficial, preservada sem importação Office. Edições e salvamento
dos cartões ocorreram no Sheets. O bot só leu link e exportação XLSX nativa.
Arquivo de QA: `1rK5qHDSfj5RYze2BUKvmMfYJKYEuxMQ9pd_qeELVUYE`.

| Estado preparado | Resultado independente esperado | Observado |
| --- | --- | --- |
| Classe 1, Projétil, Dano 3 | 3 pontos, 3d8, 3 PE | Cartão VÁLIDO; bot confirma 3d8/3 PE/saldo 3. |
| Classe 1, Dano 6 + Cura 4 | Orçamento 3 − base 1 = saldo 2; distribuir 10 excede o saldo | REVISAR; o bot registra “Distribuição excede o saldo” como problema mecânico. Mostrar os dados limitados não aprova a distribuição. |
| Classe 5, Dano 6 + Cura 4 | 15 − base Média 5 = saldo 10; 6d8 + 4d8; 15 PE | Cartão VÁLIDO; bot confirma as duas parcelas e o saldo, sem avisos do cartão. |

Cada estado foi lido por link e por seu XLSX exportado, com **18.393 chaves**,
paridade de todos os valores e do Resultado completo. `ensaios-nativos.json`
contém os resumos e tamanhos dos três arquivos. Exportações integrais ficam em
`src/var/testes-publico-21out/`, fora do Git.

A ficha foi mantida incompleta de propósito: sem nome, atributos, treinos,
capacidades de Origem e demais escolhas de criação. As cinco/seis falhas gerais
e nove pendências não são falsos erros dos cartões nem foram retiradas para
obter verde. Estes ensaios não aprovam um personagem ou uma campanha.

Na troca de Classe, a proteção preservou edições que ainda estavam sendo
salvas e pediu nova seleção. A bateria só avançou após confirmar o estado
salvo. O nível sintético foi elevado para exercitar Classe 5; nenhuma regra
de campanha ou aprovação real foi cadastrada. Não há garantia de salvamento
instantâneo, nem se transforma um estado transitório em aprovação.

Uma conta sem administração enviou o link no tópico Testes e conseguiu abrir
o painel. A navegação foi exercitada; o reensaio na publicação confere o mesmo
painel com a conta administrativa. Não é uma nova bateria de permissões do
cadastro de campanhas. Regras custom, MESTRE VIU, autorização por definição
exata e limites humanos conservam as regressões/evidências anteriores.

Esta rodada amplia a cobertura externa; não substitui todo o conjunto de
casos avançados nativos de 19/20 de outubro nem demonstra toda combinação
possível de montagem, concorrência ou rede.
