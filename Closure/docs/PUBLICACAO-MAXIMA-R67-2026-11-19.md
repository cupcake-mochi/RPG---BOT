# Publicação da análise da Técnica Máxima R67

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **19/11/2026 às
11:47:42**, horário de Brasília. O runtime é o merge
`8fff6ac838082de9c5076eabadac3eb3b2f162c2` da
[PR #108](https://github.com/cupcake-mochi/RPG---BOT/pull/108).

A consulta continua na R68/v0.379. A análise da ficha agora confere a Técnica
Máxima pela R67 nas fichas formato 13, a mesma conta que as oficiais calculam
desde 19/11. Este registro é só documental: não precisa republicar por causa dele.

## Git e testes

- O CI da PR passou no commit `06f40fd`, com 1.031 testes, OK e um pulado. O
  merge saiu com a árvore idêntica a esse commit.
- O que mudou e por quê está em [Análise da Técnica Máxima na R67](ANALISE-MAXIMA-R67-2026-11-19.md).

## Discloud

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (11:43) | 188 | 3443569 | `83e20822f18a602bf97be60d2c01b794e36a4414d506cf5f8d2974d48fb50085` |
| Pacote (`ferramentas/empacotar.py`, commit `06f40fd`) | 93 | 1866031 | `cd0075331fe6c789f962f791d2d80aa6d9d85ec344fe95bf83f1d09c5f08fbf9` |
| Backup depois do envio (11:48) | 188 | 3446109 | `8457476285e9248c660cd5f4693cb240e4f413c1542f262828cf9d997edf2c4b` |

- **Montagem do pacote.** Foi feito num checkout com `core.autocrlf=false`. O
  empacotador regerou `src/var/site/nucleo.js` com CRLF no Windows, e essa
  entrada foi normalizada para LF. Os 93 arquivos são iguais aos fontes e ao
  commit, e nenhum tem CRLF.
- **O que mudou.** Contra o que estava instalado, o pacote trocava só três
  arquivos: `r53/catalogo.json`, `r53/formulas.py` e `r53/modelo.py`.
- **Envio.** Foi pelo Commit do app existente, com o build automático. O ZIP
  foi anexado pela extensão do Claude no Brave do Mizuki.
- **Conferência no backup de depois.** Os 93 arquivos do pacote estão
  instalados iguais. O `.env` e a campanha têm o mesmo hash do backup de antes.
  Os dois bancos deram `integrity_check` `ok`, e as 18 tabelas (2 + 16) têm o
  mesmo dump e as mesmas contagens. A comparação foi feita por contagens e
  hashes, sem expor valores.
- **Guarda.** Os backups e o pacote ficam fora do Git, em armazenamento local
  privado.

## Conferência em produção

- **Logs:** online em **7 servidores** às 11:47:42, com zero erros. Só
  aparecem os avisos de voz já conhecidos (PyNaCl/davey).
- **Discord, 11:49–11:50, tópico Testes.** O `GC:ficha` foi rodado com o link
  de cada oficial (formato 13, `em_dia`, exportadas às 11:23):
  - Ciclo Maldito: painel normal, reprovada, 12 erros, 0 pendências e 0
    observações.
    [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1572987222146158636)
  - Era da Revolução: mesmo resultado.
    [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1572987380699238412)
  - O total é igual ao da publicação do formato 13 (12 erros com a ficha em
    branco). Os erros que aparecem são das invocações ("acerto" informado como
    resultado), e nenhum é da Técnica Máxima.

## Pendências reais

- O cartão da Máxima está vazio nos modelos oficiais. A conta nova só aparece
  quando alguém preencher uma Máxima numa cópia de jogador. Não ensaiei isso no
  Discord.
- Não houve pergunta à Kal'tsit ou à Closure, porque essas chamam o modelo pago.
