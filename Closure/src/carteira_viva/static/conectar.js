"use strict";
(() => {
  const ticket = new URLSearchParams(location.search).get("ticket");
  const $ = id => document.getElementById(id);
  let state, busy = false, pickerReady, espera;
  const en = {
    titulo:"Connect your character sheet", introducao:"Choose the sheet you already use. Registration is for this server and does not approve the character.",
    passo1:"Your Discord account", passo2:"Your Google spreadsheet", passo3:"Review and confirm",
    "entrar-discord":"Sign in with Discord", "entrar-google":"Connect Google", "conta-label":"Or use an existing connection", usar:"Use this connection",
    permissao:"Google authorization grants the app access to selected files. This step only reads the sheet. The bot only writes to it if you ask, when filling it in on the site.",
    escolher:"Choose my sheet",
    "dica-picker":"If the Google picker asks you to sign in or opens another window, your browser is blocking Google cookies on this page. In Brave, click the lion in the address bar and turn Shields off for this site only, then click Choose my sheet again.",
    conferir:"Review your selection", parcial:"The format was identified. Full sheet analysis is a separate step.",
    "nome-label":"Character name", "responsabilidade-label":"I confirm this is my sheet and I may register it in this server. Administrators and authorized reviewers may view its details.",
    "troca-aviso":"Replacing the file keeps the character and card, but requires a new analysis. The previous Google file stays intact.",
    confirmar:"Confirm", pronto:"All set", voltar:"You may close this window and return to Discord.", cancelar:"Cancel request",
    rodape:"Access lasts while Google authorization remains valid. You may disconnect or replace the file later.",
    "criar-ficha":"I don’t have a sheet yet: create one",
    "copiando-texto":"Google is copying the sheet to your account. It usually takes 20 to 60 seconds. If you close this page, the copy continues and the character appears in /characters.",
    "abrir-ficha":"Open my sheet", "preencher-ficha":"Fill it in on the site", "passos-titulo":"First steps",
    "passo-abrir":"Open the sheet and wait for it to load: the Recursos, Bot and Salários menus appear at the top.",
    "passo-editar":"Before choosing the Path, write the character name in CARTEIRA and wait about 30 seconds. The first edit after opening is slow.",
    "passo-caminho":"Choose the Path (Caminho) in FICHA. If its skills are not marked, choose it again.",
    "passo-guia":"For everything else, use GC:guia criar in Discord. Leave EMITIR for last.",
    demo:"Local demonstration — fictional accounts and files."
  };
  const messages = {
    identificar:["Entre com a mesma conta Discord que iniciou esta solicitação.","Sign in with the Discord account that started this request."],
    google:["Agora conecte o Google ou reutilize uma conexão sua.","Connect Google or reuse one of your connections."],
    picker:["Escolha apenas a planilha deste personagem.","Choose this character’s spreadsheet."],
    revisar:["Confira o arquivo e confirme o cadastro ou a reconexão.","Check the file and confirm registration or reconnection."],
    concluido:["Conexão concluída.","Connection complete."],
    copiando:["Copiando sua ficha…","Copying your sheet…"],
    cancelado:["Solicitação cancelada. Nenhum arquivo foi alterado.","Request cancelled. No files were changed."],
    falhou:["Não foi possível confirmar a conexão. Abra uma nova solicitação pelo Discord.","The connection could not be confirmed. Start a new request in Discord."]
  };
  // Seletor do Google na criação: a pessoa desistiu ou não escolheu o modelo.
  const avisos = {
    cancelado:["Você saiu antes de terminar no Google. Nada foi criado; é só tentar de novo.","You left Google before finishing. Nothing was created; just try again."],
    modelo:["Faltou escolher a ficha modelo na janela do Google. Clique em Continuar, toque na única ficha que aparecer e confirme.","The template was not chosen in the Google window. Click Continue, tap the only sheet shown and confirm."]
  };
  const falhas = {
    copia_incerta:["O Google demorou pra confirmar a cópia. Espere uns três minutos e peça de novo no Discord: se a cópia já existir, ela é aproveitada.","Google took too long to confirm the copy. Wait about three minutes and ask again in Discord: if the copy already exists, it is reused."],
    copia_invalida:["A cópia foi apagada, movida ou compartilhada antes do cadastro. Peça outra no Discord, ou use a sua com /personagem cadastrar.","The copy was deleted, moved or shared before registration. Ask for another in Discord, or register yours with /character register."],
    revogada:["A autorização do Google foi retirada. Abra uma nova solicitação no Discord.","The Google authorization was removed. Start a new request in Discord."],
    modelo_bloqueado:["A criação pelo bot não está liberada neste servidor.","Creation by the bot is not enabled in this server."]
  };
  const english = () => state?.idioma === "en";
  function showError(code) {
    const specific = {origem:["Abra a conexão no endereço original.","Open the connection at its original address."],
      acesso:["Essa conta ou sessão não pode usar esta solicitação.","This account or session cannot use this request."],
      ocupado:["O serviço está ocupado. Tente novamente em instantes.","The service is busy. Try again shortly."],
      responsabilidade:["Marque a confirmação de responsabilidade para continuar.","Confirm responsibility before continuing."]};
    specific.expirada=["Este link venceu: ele vale dez minutos. Peça um novo pelo mesmo comando no Discord.","This link expired: it lasts ten minutes. Request a new one with the same command in Discord."];
    specific.formato=["Essa planilha não está num formato de ficha que a Carteira conhece. Confira se escolheu a ficha certa e abra uma nova solicitação pelo Discord.","This spreadsheet is not in a sheet format the Wallet knows. Check you picked the right sheet and start a new request in Discord."];
    specific.nome=["Escreva o nome do personagem.","Enter the character name."];
    specific.modelo_bloqueado=falhas.modelo_bloqueado; specific.copia_incerta=falhas.copia_incerta;
    specific.limite=["Você já tem solicitações abertas. Termine ou cancele uma delas; depois tente novamente.","You already have open requests. Finish or cancel one, then try again."];
    const text = specific[code] || ["Não foi possível concluir. Confira sua conta ou abra uma nova solicitação pelo Discord.","Could not complete the request. Check your account or start a new request in Discord."];
    $("erro").textContent = text[english() ? 1 : 0]; $("erro").hidden = false;
  }
  async function api(path, data) {
    const r = await fetch(path + (data ? "" : "?" + new URLSearchParams({ticket})), {
      method:data ? "POST":"GET", credentials:"same-origin", cache:"no-store",
      headers:data ? {"Content-Type":"application/json", "X-CSRF-Token":state?.csrf || ""}: {},
      body:data ? JSON.stringify({ticket, ...data}):undefined
    });
    const value = await r.json(); if (!r.ok) throw new Error(value.erro || "solicitacao"); return value;
  }
  function render() {
    if (english()) { document.documentElement.lang="en"; document.title="Connect sheet · Guias do Ciclo";
      for (const [id,text] of Object.entries(en)) $(id).textContent=text; }
    const titles={cadastro:["Cadastrar seu personagem","Register your character"],criar:["Criar sua ficha","Create your sheet"],troca:["Trocar arquivo da ficha","Replace the sheet file"],reconectar:["Reconectar sua ficha","Reconnect your sheet"],modelo:["Modelo do servidor","Server template"]};
    $("titulo").textContent=(titles[state.acao] || ["Conectar sua ficha","Connect your sheet"])[english()?1:0];
    for (const id of ["discord","google","picker","revisar","copiando","concluido"]) $(id).hidden=true;
    $("demo").hidden=!state.demonstracao;
    const msg=messages[state.fase] || ["Esta etapa está em andamento. Se voltar não resolver, abra uma nova solicitação no Discord.","This step is in progress. If returning does not help, start a new request in Discord."];
    $("mensagem").textContent=msg[english()?1:0];
    if(state.fase === "revisar") {
      const review={cadastro:["Confira o arquivo e o nome do personagem antes de confirmar.","Check the file and character name before confirming."],
        troca:["Confira o novo arquivo. O personagem e o cartão continuam os mesmos.","Check the new file. The character and card stay the same."],
        reconectar:["Confira a ficha vinculada para restabelecer o acesso.","Check the linked sheet to restore access."],
        modelo:["Confira o modelo escolhido. Salvar esta escolha ainda não libera a criação de fichas.","Review the selected template. Saving this choice does not enable sheet creation yet."]};
      review.criar=["Dê um nome ao personagem e confirme. A cópia da ficha oficial Ciclo Maldito fica no seu Google Drive.","Name the character and confirm. The copy of the official Ciclo Maldito sheet stays in your Google Drive."];
      $("mensagem").textContent=review[state.acao][english()?1:0];
    }
    if (state.fase === "identificar") $("discord").hidden=false;
    if (state.fase === "google") {
      $("google").hidden=false; $("conta").replaceChildren();
      (state.conexoes || []).forEach((id,i) => { const op=document.createElement("option"); op.value=id;
        op.textContent=(english()?"Connected Google account ":"Conta Google conectada ")+(i+1); $("conta").append(op); });
      $("conectadas").hidden=!(state.conexoes || []).length;
      $("criar-ficha").hidden=!state.pode_criar;
    }
    if (state.fase === "picker" || (state.fase === "revisar" && !["reconectar","criar"].includes(state.acao))) $("picker").hidden=false;
    $("dica-picker").hidden=state.fase !== "picker" || !!state.demonstracao;
    if (state.fase === "revisar") { $("revisar").hidden=false; $("arquivo").textContent=state.previa.nome_arquivo;
      const editavel=["cadastro","criar"].includes(state.acao);
      $("nome").value=state.acao === "criar" ? "" : state.acao === "cadastro" ? state.previa.nome : state.nome_atual; $("nome").disabled=!editavel;
      $("troca-aviso").hidden=state.acao !== "troca"; }
    if (state.fase === "concluido") { $("concluido").hidden=false;
      $("resultado").textContent=state.acao === "modelo" ? (english()?"Server template saved. Existing characters keep their sheets.":"Modelo do servidor salvo. Os personagens cadastrados continuam com suas fichas.") : state.resultado.perfil.nome+(english()?" · Registration code: ":" · Código do cadastro: ")+state.resultado.id; }
    $("aviso").hidden=!avisos[state.aviso];
    if (avisos[state.aviso]) $("aviso").textContent=avisos[state.aviso][english()?1:0];
    if (state.acao === "criar") {
      const copy={introducao:["O bot copia a ficha oficial Ciclo Maldito, vazia, pra sua conta Google e já cadastra o personagem neste servidor. Isso não aprova o personagem.","The bot copies the empty official Ciclo Maldito sheet to your Google account and registers the character in this server. This does not approve the character."],
        permissao:["Na próxima tela, o Google mostra só a ficha modelo: escolha ela e confirme. O app passa a ver o modelo e as cópias que ele mesmo criar, nada mais do seu Drive. Criar não preenche nenhuma célula.","On the next screen Google shows only the template sheet: pick it and confirm. The app can then see the template and the copies it creates, nothing else in your Drive. Creating does not fill in any cell."],
        passo2:["Sua conta Google","Your Google account"],passo3:["Dar nome e criar","Name it and create"],
        "entrar-google":["Continuar no Google","Continue on Google"],conferir:["Criar a ficha","Create the sheet"],
        parcial:["A ficha vem vazia, no nível inicial padrão. O nome escolhido aqui vai no arquivo e no cartão; dentro da ficha, quem decide o que entra é você.","The sheet comes empty, at the default starting level. The name chosen here goes on the file and the card; inside the sheet, you decide what goes in."],
        "responsabilidade-label":["Quero criar esta ficha na minha conta Google e cadastrá-la neste servidor. Administradores e revisores autorizados poderão consultar os detalhes.","I want to create this sheet in my Google account and register it in this server. Administrators and authorized reviewers may view its details."],
        confirmar:["Criar ficha","Create sheet"]};
      for (const [id,values] of Object.entries(copy)) $(id).textContent=values[english()?1:0];
      if (state.fase === "google") $("mensagem").textContent=english()?"Now choose the template on Google.":"Agora escolha o modelo no Google.";
      if (state.fase === "revisar") $("arquivo").textContent=(english()?"Template: ":"Modelo: ")+state.previa.nome_arquivo;
      if (state.fase === "concluido") { $("mensagem").textContent=english()?"Sheet created and registered.":"Ficha criada e cadastrada.";
        $("criada").hidden=false; $("preencher-ficha").hidden=!state.preencher; if(state.preencher) $("preencher-ficha").href=state.preencher+"?idioma="+encodeURIComponent(state.idioma);
        $("abrir-ficha").href="https://docs.google.com/spreadsheets/d/"+encodeURIComponent(state.resultado.arquivo)+"/edit"; }
      if (state.fase === "falhou" && state.erro) $("mensagem").textContent=(falhas[state.erro] || ["A ficha não foi criada agora. Tente de novo pelo Discord; se a cópia já existir no seu Drive, ela é aproveitada.","The sheet was not created. Try again in Discord; if the copy already exists in your Drive, it is reused."])[english()?1:0];
    }
    $("copiando").hidden=state.fase !== "copiando";
    if (state.fase === "copiando") acompanhar();
    if (state.acao === "modelo") {
      const copy={introducao:["Selecione o modelo que sua mesa quer usar. O bot só cria ficha vazia a partir da oficial Ciclo Maldito; criar a partir de um modelo próprio do servidor ainda não está disponível.","Choose the template for your table. The bot only creates empty sheets from the official Ciclo Maldito; creating from a server template is not available yet."],
        escolher:["Escolher modelo do servidor","Choose server template"],conferir:["Confira o modelo","Review template"],
        "responsabilidade-label":["Sou administrador e posso selecionar este modelo para o servidor. Entendo que a criação continua indisponível e que esta escolha não altera personagens cadastrados.","I am an administrator and may select this server template. I understand creation remains unavailable and existing characters are unaffected."],
        rodape:["Esta solicitação salva apenas a referência do modelo. Para cadastrar uma ficha existente, use /personagem cadastrar no Discord.","This request only saves the template reference. To register an existing sheet, use /character register in Discord."],
        parcial:["A conferência do formato é parcial. Nível do personagem, XP e regra de nível inicial da campanha são distintos; nenhum desses parâmetros está liberado para criação automática.","The format check is partial. Character level, XP and the campaign’s starting-level rule are distinct; none is enabled for automatic creation."]};
      for (const [id,values] of Object.entries(copy)) $(id).textContent=values[english()?1:0];
      $("nome").hidden=true; $("nome-label").hidden=true;
      if (state.fase === "picker") $("mensagem").textContent=english()?"Choose a template you may configure for this server.":"Escolha um modelo que você possa configurar para este servidor.";
      if (state.fase === "concluido") $("mensagem").textContent=english()?"Template choice saved. Creation remains unavailable.":"Escolha do modelo salva. A criação continua indisponível.";
      $("modelo-sinais").hidden=!(state.previa?.sinais?.length);
      $("modelo-sinais").textContent=english()?"The check found data or usage markers in this template. Initialization must handle them before creating a new character sheet.":"A conferência encontrou dados ou marcas de uso neste modelo. A inicialização precisa tratá-los antes de criar uma ficha nova.";
    }
    $("cancelar").hidden=["copiando","concluido","cancelado","falhou"].includes(state.fase);
  }
  // A cópia roda no servidor: a página só pergunta de tempos em tempos.
  function acompanhar() {
    clearTimeout(espera);
    espera=setTimeout(async()=>{
      try { state=await api("/api/fluxo"); render(); }
      catch(e) { if (["expirada","acesso"].includes(e.message)) showError(e.message); else acompanhar(); }
    },4000);
  }
  async function reload() { state=await api("/api/fluxo"); render(); }
  async function action(work) {
    if(busy) return; busy=true; $("erro").hidden=true;
    document.querySelectorAll("button").forEach(b=>b.disabled=true);
    try { await work(); } catch(e) {
      showError(e.message);
      // Uma falha pode encerrar a solicitação no servidor: só redesenha se a etapa mudou,
      // para não apagar o que a pessoa digitou na revisão.
      try { const atual=await api("/api/fluxo"); if(atual.fase!==state.fase){ state=atual; render(); } } catch {}
    }
    finally { busy=false; document.querySelectorAll("button").forEach(b=>b.disabled=false); }
  }
  for (const provider of ["discord","google"]) $("entrar-"+provider).onclick=()=>action(async()=>{
    const data=await api("/api/login/"+provider,{}); location.assign(data.url);
  });
  $("criar-ficha").onclick=()=>action(async()=>{ await api("/api/criar",{}); await reload(); });
  $("usar").onclick=()=>action(async()=>{ await api("/api/usar",{conexao:$("conta").value}); await reload(); });
  $("cancelar").onclick=()=>action(async()=>{ await api("/api/cancelar",{}); await reload(); });
  $("confirmar").onclick=()=>action(async()=>{
    const value=await api("/api/confirmar",{nome:$("nome").value,responsabilidade:$("responsabilidade").checked});
    if (state.acao === "criar" && !value.resultado) { await reload(); return; }
    state={...state,fase:"concluido",resultado:value.resultado}; render();
  });
  function loadPicker() {
    if (!pickerReady) pickerReady=new Promise((resolve,reject)=>{
      const s=document.createElement("script"); s.src="https://apis.google.com/js/api.js";
      s.onerror=()=>reject(new Error("provedor")); s.onload=()=>gapi.load("picker",{callback:resolve,onerror:()=>reject(new Error("provedor"))});
      document.head.append(s);
    }); return pickerReady;
  }
  $("escolher").onclick=()=>action(async()=>{
    if(state.demonstracao) { await api("/api/selecionar",{arquivo:"arquivo_ficticio_para_teste_001"}); await reload(); return; }
    const config=await api("/api/picker"); await loadPicker();
    const view=new google.picker.DocsView(google.picker.ViewId.SPREADSHEETS).setIncludeFolders(false);
    new google.picker.PickerBuilder().setAppId(config.app_id).setDeveloperKey(config.developer_key)
      .setOAuthToken(config.access_token).setOrigin(location.origin).addView(view).setCallback(data=>{
        if(data.action===google.picker.Action.PICKED) action(async()=>{
          await api("/api/selecionar",{arquivo:data.docs[0].id}); await reload();
        });
      }).build().setVisible(true);
    // O app não grava o token em storage/URLs próprias. O SDK o passa ao iframe
    // oficial do Google; não registrar ou copiar a URL interna desse iframe.
  });
  action(reload);
})();
