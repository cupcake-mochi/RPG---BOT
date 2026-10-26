# Ensaio da leitura completa

26/10/2026 · **preparado, ainda NÃO executado**.
Backend da etapa 4 na PR 81. Resultado offline em [ETAPA-4.md](ETAPA-4.md).

## Preparação concluída

- Nova cópia descartável da oficial Ciclo Maldito, criada pelo conector Drive:
  **QA Carteira — leitura completa — DESCARTÁVEL — 26-10-2026**.
  ID `1MWj-9f21rRnr7pA4vEegGYw0-ec2tQ2kBSWE4Rxjy08`.
  Metadados confirmam `shared=false`; nenhuma permissão foi ampliada.
- Serviço separado em loopback `127.0.0.1:8876`, com as credenciais de app
  já autorizadas, banco privado próprio e arquivo de campanha fictício `{}`.
  O app da Discloud e seu processo não foram alterados.
- Entrada local e identificação Discord com o escopo anterior `identify`
  concluídas. A conta escolhida no Google é a conta de teste do mantenedor.
- Google exibiu o aviso de aplicativo não verificado. A tela foi deixada
  aberta para o usuário passar pelo aviso e confirmar o consentimento.
  Foi pedido selecionar somente essa nova cópia. **Sem resposta, não prosseguir.**

O controle do navegador exige intervenção do usuário em avisos de segurança.
Nenhuma nova credencial, autorização persistente ou leitura completa foi
confirmada neste ensaio até este registro. O grant antigo da etapa 3 continua
revogado. Não confundir criação da cópia ou OAuth Discord com sucesso do Google.

## Continuar

1. Conferir se a tentativa ainda está no prazo de dez minutos. Se expirou,
   criar nova entrada pelo serviço e refazer o login, preservando a cópia.
   Não reutilizar código/estado OAuth antigo.
2. Após confirmação do usuário, conferir escopo e conta; escolher apenas a
   cópia acima no Picker. Confirmar cadastro fictício na própria tela.
3. Usar as rotas internas para atualizar duas vezes, analisar e abrir a análise
   salva. Esperado: segunda atualização usa cache; análise explícita relê;
   resultado salvo coincide; origem/revisão/campanha aparecem corretamente.
4. Comparar a leitura completa com exportação XLSX calculada da MESMA cópia.
   Não abrir ou alterar jogador/oficial para provocar um caso de teste.
5. Registrar contagens, falhas e consumo de chamadas sem expor campos privados,
   IDs de usuário, tokens, URLs OAuth ou parâmetros do iframe Picker.
6. Ao terminar: revogar o grant de teste, remover cadastro fictício, enviar a
   cópia à lixeira, encerrar serviço local e fechar abas temporárias. Excluir
   convites locais antigos. Registrar o que foi de fato confirmado.

Credenciais/configurações ficam no diretório privado indicado em RETOMADA.md,
fora do Git. Arquivos temporários de preparação não são fonte de verdade do
produto nem evidência de sucesso. A configuração de `drive.file` permite ler e
editar arquivos escolhidos, mas este código não escreve em nenhuma célula.

Casos nativos avançados, cargos reais, troca entre duas fontes e celular físico
continuam na matriz de testes. Nada deste ensaio foi publicado no Discord.
