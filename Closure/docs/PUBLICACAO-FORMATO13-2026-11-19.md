# Publicação da ANALISE estática (formato 13)

Concluída em **19/11/2026, às 09:09:30 (Brasília)**, no app existente das Guias do Ciclo (`1773761486581`). Runtime publicado: **`66dc59f`** (merge da [PR104](https://github.com/cupcake-mochi/RPG---BOT/pull/104)). Este registro é só documental: não republicar por causa dele.

## Por que agora

As duas oficiais (Ciclo Maldito e Era da Revolução) viraram formato 13 em 18/11/2026, às 14:07, com `analise.estado = em_dia` ([Ficha---RPG-JJK PR132](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/132)). O runtime anterior (`0251baa`, PR102, de 04/11) respondia "formato desconhecido" para qualquer ficha 13.

## O que foi entregue

- O 13 é conferido como o 12 quando `analise.estado` é `em_dia`. Fora disso (`desatualizada`, `exportando`, sem estado) o bot não confere dado velho e pede pra exportar (menu Bot > Exportar para o bot no PC, caixa Bot da CARTEIRA no celular) e chamar de novo. O 12 vivo continua aceito. Detalhes em [CONTRATO-ABA-BOT](../dados/ficha/CONTRATO-ABA-BOT.md).
- Consulta, guias, clima e o resto do bot sem mudança.

## Pente fino antes do envio

- Do runtime publicado (`0251baa`) até `66dc59f` mudaram só a PR104 e três documentos (PR97). A árvore de `66dc59f` é idêntica à cabeça da PR104, aprovada na CI.
- **Carteira Viva:** só existe nos ramos `codex/carteira-viva-*` e PR93, não mesclados. Não está no `main`, não entra no pacote e não estava instalada na Discloud (backup de antes sem nenhum arquivo dela).
- O histórico da Discloud mostra dois Commits e a RAM alterada para 512 MB em 05/11, sem registro no repo. O backup de antes mostrou que o código instalado era o de `0251baa` (84 dos 93 arquivos iguais ao pacote novo, os outros 9 eram os 8 da PR104 e o `nucleo.js`, igual a menos de quebra de linha).
- Testes da ficha num checkout limpo de `66dc59f` (LF): 290 + 47 OK; nos 176 da B47, só o erro conhecido do Windows (`test_cli_preserva_outros_servidores_e_aprova_hash`, que chama um executável), aprovado na CI Linux.
- Conferência na ficha real antes do envio: o corretor de `66dc59f` lê as duas oficiais 13 `em_dia` (18.501 linhas) com o mesmo resultado do 12.

## Backup, pacote e preservação

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (09:06) | 188 | 3437033 | `f19dbffdf5e68a0fbd6670a7ddba19c1664e09af4c58ca00e6098281422d2898` |
| Pacote (`ferramentas/empacotar.py`, main `66dc59f`) | 93 | 1861331 | `dc02fad3a63285c8f886ef691e6350d162a76af983c1a99f68878a5b94dc7511` |
| Backup depois do envio (09:11) | 188 | 3440506 | `71c2b7e3eac6daec2f2b24eb8c6cc7936bcd399fa5e8884189934a94da9d03a5` |

- Pacote montado no Windows a partir de um checkout com `core.autocrlf=false`. O empacotador regera `src/var/site/nucleo.js` com CRLF no Windows; essa entrada foi normalizada para LF e ficou byte a byte igual à instalada. Nenhum arquivo do pacote com CRLF; sem `.env`, bancos, campanha ou dados de jogador.
- Comparado ao instalado antes, o pacote mudava só os 8 arquivos da PR104.
- Envio pelo Commit no app existente, sem Rebuild separado.
- Backup depois: **93/93 arquivos do pacote instalados iguais**, nenhum ausente ou divergente.
- `.env` e campanha iguais ao backup de antes (hash). Os dois bancos com `integrity_check` `ok`, as 18 tabelas com as mesmas contagens e o mesmo conteúdo antes e depois. Comparação por contagens e hashes, sem expor valores.
- Backups ficam fora do Git, na pasta de downloads do computador do Mizuki.

## Conferência

- Logs: online em **7 servidores** às 09:09:30, zero erros; só os avisos existentes de voz (PyNaCl/davey). Um único reinício.
- **Não ensaiado no Discord:** o navegador usado não tinha sessão do Discord. A leitura e a conferência das oficiais 13 foram testadas com o mesmo código, fora do Discord.

## Pendências reais

- Ensaiar `/ficha analisar` no Discord com o link de uma oficial (tem que sair o painel) e com uma ficha 13 editada depois da exportação (tem que sair o pedido de exportação).
- `.xlsx` de ficha 13 não testado com arquivo real.
- Registrar o que foram os dois Commits e a mudança de RAM de 05/11.
