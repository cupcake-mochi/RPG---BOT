# Publicação dos Talentos grátis

Concluída em **03/11/2026, às 19:57 (Brasília)**, no app existente das Guias do Ciclo (`1773761486581`). Runtime publicado: **`a50053eface9215b2bd36a3289481cd671dc6851`**. Este registro é só documental: não republicar por causa dele.

## O que foi entregue

- [PR94](https://github.com/cupcake-mochi/RPG---BOT/pull/94), merge do runtime acima: a Closure confere as cartas Talento · Origem e Talento · Extra da FICHA AMALDIÇOADA ([Ficha---RPG-JJK PR50](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/50), já nas duas oficiais). As 15 chaves novas da ANALISE são opcionais; formato 12 e esquema de 18393 chaves sem mudança. Detalhes em [INTEGRACAO-R53](../dados/ficha/INTEGRACAO-R53.md#talentos-grátis--03112026).
- A consulta continua R60/v0.369, 576 trechos.

## Testes

- Suíte completa local: **998 executados, zero falhas, 68 pulados** (main anterior: 990/zero/68). CI da PR94 aprovada.

## Backup, pacote e preservação

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio | 269 | 3411751 | `c85492cef010cf95fc2515ee96ba3354d20942f69da27f69f84b7ecaedb92754` |
| Pacote (`ferramentas/empacotar.py`, da main `a50053e`) | 92 | 1852980 | `587dc80ac2a868cf7496bdc8e5d7fa8d13eca56f322a7edca797d9df9c52e298` |

- O backup antes do envio foi baixado e conferido (zip íntegro, os dois bancos com integridade `ok`); o código instalado antes era o da main `d92cb0b`.
- O pacote tem os mesmos 91 arquivos da publicação de 30/10 mais `recursos/talentos-gratis-campos.tsv`; sem `.env`, bancos, campanha ou dados de jogador.
- Envio pelo Commit no app existente, sem Rebuild separado.
- Backup depois do envio: **92/92 arquivos do pacote instalados iguais**, nenhum ausente ou divergente.
- `.env`, campanha e todas as tabelas dos dois bancos iguais ao backup de antes, exceto a coluna `estado` de `paineis_clima` (rotina normal do painel; servidor, canal, dia e mensagem preservados). Comparação por contagens e hashes, sem expor valores.
- Backups e hashes ficam fora do Git em `/home/mizuki/.local/share/guias-ciclo/publicacao-pr94-20261103`.

## Conferência

- Logs: online em 6 servidores às 19:57:30, zero erros; só os avisos existentes de voz (PyNaCl/davey).
- `GC:ping` no tópico Testes: R60/v0.369, 576 trechos, 51 ms.
- **Não ensaiado no Discord:** `/ficha analisar` com as cartas novas. A cópia de teste é privada (o link não abre sem mudar o compartilhamento) e o envio de anexo não foi possível pelo navegador usado. A conta nova está coberta pelos testes da suíte, não por uma leitura nativa no Discord.

## Pendências reais

- Ensaiar `/ficha analisar` pelo Discord (link aberto ou .xlsx anexo) com as cartas novas; a conferência em si já foi testada na ficha real.
- `MANIFESTO-PACOTE` não foi regenerado nesta publicação.

## Segunda publicação: os alvos da CONFIGURAÇÃO · 03/11/2026, 20:24

Um teste numa ficha real (cópia de teste da oficial: Latente + Manifestação Instintiva, Leitura na carta Talento · Origem, três pagos de CE 1 e Farejador na carta Talento · Extra), com a ANALISE lida pela API e conferida pelo mesmo código do bot, mostrou:

- Carta da Origem certificada ("fora dos espaços e dos cinco pagos", "3 de 3 espaços comuns ocupados"); carta extra fora dos pagos, com nota de fonte do mestre.
- **Bug:** a linha da CONFIGURAÇÃO com o alvo "Talentos grátis" (e, do mesmo jeito, "Feitiços fora dos espaços") era reprovada como alvo desconhecido.

Conserto em [PR96](https://github.com/cupcake-mochi/RPG---BOT/pull/96), runtime **`9173b8e0519f96c53c5904aa6c8f22726b27c82f`**: os dois alvos entram na lista; a linha fica pendente de aprovação do mestre. Suíte completa 999 ok; CI aprovada.

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio | 270 | 3415322 | `49da36a6c7acdee9707e68c217546f1b7580e6c2924529b814be8af9e9beafc8` |
| Pacote (main `9173b8e`) | 92 | 1853063 | `7ca5d6dc24e7d96bea5cffee1a0632ce524f16a70aae2cea77da59044db077a9` |

- Commit no app existente às 20:24, build concluído; online em 6 servidores às 20:24:48, zero erros.
- Backup depois: **92/92 arquivos iguais ao pacote**; `.env`, campanha e bancos iguais, exceto `estado` de `paineis_clima` (rotina normal).
- `GC:ping`: R60/v0.369, 576 trechos, 43 ms.
- Backups e hashes fora do Git em `/home/mizuki/.local/share/guias-ciclo/publicacao-pr96-20261103`.
- `/ficha analisar` pelo Discord segue não ensaiado (cópia privada; anexo indisponível no navegador usado). O teste acima cobre a leitura da ANALISE nativa e a conferência, não o transporte pelo Discord.
