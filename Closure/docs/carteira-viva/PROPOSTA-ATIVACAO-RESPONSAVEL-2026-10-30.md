# Próxima ação: ativar a cópia pelo responsável

Proposta de código e ensaio para o rascunho PR31. **Autorizada e implementada em protótipo em 30/10.**
Código do produtor `49e9963`; 29 cenários offline aprovados. Ensaio nativo e CI
ainda têm fechamento separado. A autorização anterior cobre cinco propriedades e inspeção,
sem instalar acionadores. A extensão foi explicitamente autorizada pelo mantenedor.

## Entrega proposta

Uma ação separada do produtor, executada pelo responsável no Google, depois do
perfil de propriedades. Atua somente na cópia ativa, privada, descartável e
vinculada à mesma operação/projeto/execução. Não repete resets financeiros.

1. Conferir contexto, diário terminal das propriedades, células limpas e
   preservação antes de qualquer efeito. Recusar oficial, modelo, arquivo
   cadastrado, outro projeto/execução e contexto importado do navegador.
2. Instalar somente `salarioDiario` (diário, 3h, America/Sao_Paulo),
   `salarioRegistrarEdicao` (edição da cópia) e `salarioAposAbrir` (abertura da
   cópia), com diário próprio e retomada após cada criação. Conferir os tipos e
   a fonte antes de reutilizar uma rotina; não apagar acionadores desconhecidos.
3. Coordenar `salario_edicao` com o projeto e o acionador de edição. A marca
   nunca pode declarar uma instalação que não terminou. Não alterar outras
   propriedades ou refazer o financeiro para recuperar uma interrupção.
4. Manter a inspeção e todos os indicadores do backend separados. O resultado
   local pode relatar rotinas instaladas pela conta da execução, mas continua
   com `responsavelVerificadoPeloBot=false` e `criacaoDisponivel=false`.
5. Ensaiar em uma descartável: instalação única, repetição, interrupção entre
   criações, evento real de edição/abertura, missão/gasto/correção sem duplicar
   lançamentos e limpeza de somente os recursos do ensaio. Login e avisos são
   feitos pelo mantenedor. Nenhuma oficial ou ficha de jogador é alterada.

## O que isso não resolve

A conta só enxerga os próprios acionadores. O backend com `drive.file` não tem
uma API que certifique os acionadores do projeto. Identificação Google do dono
não é prova de que um JSON sobre automações é verdadeiro; um desafio devolvido
pelo navegador também não é essa prova. Não aceitar checkbox, JSON colado,
chave temporária ou relatório local como liberação automática.

Essa entrega comprova a ativação local no caminho observado. O vínculo
verificável com o backend exige desenho separado antes de qualquer novo escopo,
endpoint ou implantação Apps Script. Até lá, criação continua bloqueada.
Não há proposta de ampliar OAuth das Guias, criar endpoint público, fazer merge,
publicar o produtor ou implantar a Carteira nesta autorização.

## Aceite

Testes offline precisam cobrir falha antes/depois de cada criação, marca sem
rotina, rotina errada/duplicada, contexto trocado, preservação e retomada sem
instalação duplicada. Prova nativa só depois dos testes; nenhuma repetição dos
ensaios REST anteriores é necessária para essa entrega.

Implementação: wrappers próprios só delegam aos três handlers listados após concluir o diário e a marca. Uma criação sem confirmação de UID é incerta e recusa repetição; não há adoção automática de CLOCK por inspeção. Detalhes no produtor: `r53/inicializacao/ATIVACAO-2026-10-30.md`.
