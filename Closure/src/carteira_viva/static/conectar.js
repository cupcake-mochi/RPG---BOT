"use strict";
(() => {
  const ticket = new URLSearchParams(location.search).get("ticket");
  const $ = id => document.getElementById(id);
  let state, busy = false, pickerReady;
  const en = {
    titulo:"Connect your character sheet", introducao:"Choose the sheet you already use. Registration is for this server and does not approve the character.",
    passo1:"Your Discord account", passo2:"Your Google spreadsheet", passo3:"Review and confirm",
    "entrar-discord":"Sign in with Discord", "entrar-google":"Connect Google", "conta-label":"Or use an existing connection", usar:"Use this connection",
    permissao:"Google authorization grants the app access to selected files. This step only reads the sheet; it does not edit cells.",
    escolher:"Choose my sheet", conferir:"Review your selection", parcial:"The format was identified. Full sheet analysis is a separate step.",
    "nome-label":"Character name", "responsabilidade-label":"I confirm this is my sheet and I may register it in this server. Administrators and authorized reviewers may view its details.",
    "troca-aviso":"Replacing the file keeps the character and card, but requires a new analysis. The previous Google file stays intact.",
    confirmar:"Confirm", pronto:"All set", voltar:"You may close this window and return to Discord.", cancelar:"Cancel request",
    rodape:"Access lasts while Google authorization remains valid. You may disconnect or replace the file later.",
    demo:"Local demonstration — fictional accounts and files."
  };
  const messages = {
    identificar:["Entre com a mesma conta Discord que iniciou esta solicitação.","Sign in with the Discord account that started this request."],
    google:["Agora conecte o Google ou reutilize uma conexão sua.","Connect Google or reuse one of your connections."],
    picker:["Escolha apenas a planilha deste personagem.","Choose this character’s spreadsheet."],
    revisar:["Confira o arquivo e confirme o cadastro ou a reconexão.","Check the file and confirm registration or reconnection."],
    concluido:["Conexão concluída.","Connection complete."],
    cancelado:["Solicitação cancelada. Nenhum arquivo foi alterado.","Request cancelled. No files were changed."],
    falhou:["Não foi possível confirmar a conexão. Abra uma nova solicitação pelo Discord.","The connection could not be confirmed. Start a new request in Discord."]
  };
  const english = () => state?.idioma === "en";
  function showError(code) {
    const specific = {origem:["Abra a conexão no endereço original.","Open the connection at its original address."],
      acesso:["Essa conta ou sessão não pode usar esta solicitação.","This account or session cannot use this request."],
      ocupado:["O serviço está ocupado. Tente novamente em instantes.","The service is busy. Try again shortly."],
      responsabilidade:["Marque a confirmação de responsabilidade para continuar.","Confirm responsibility before continuing."]};
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
    const titles={cadastro:["Cadastrar seu personagem","Register your character"],troca:["Trocar arquivo da ficha","Replace the sheet file"],reconectar:["Reconectar sua ficha","Reconnect your sheet"]};
    $("titulo").textContent=(titles[state.acao] || ["Conectar sua ficha","Connect your sheet"])[english()?1:0];
    for (const id of ["discord","google","picker","revisar","concluido"]) $(id).hidden=true;
    $("demo").hidden=!state.demonstracao;
    const msg=messages[state.fase] || ["Esta etapa está em andamento. Se voltar não resolver, abra uma nova solicitação no Discord.","This step is in progress. If returning does not help, start a new request in Discord."];
    $("mensagem").textContent=msg[english()?1:0];
    if(state.fase === "revisar") {
      const review={cadastro:["Confira o arquivo e o nome do personagem antes de confirmar.","Check the file and character name before confirming."],
        troca:["Confira o novo arquivo. O personagem e o cartão continuam os mesmos.","Check the new file. The character and card stay the same."],
        reconectar:["Confira a ficha vinculada para restabelecer o acesso.","Check the linked sheet to restore access."]};
      $("mensagem").textContent=review[state.acao][english()?1:0];
    }
    if (state.fase === "identificar") $("discord").hidden=false;
    if (state.fase === "google") {
      $("google").hidden=false; $("conta").replaceChildren();
      (state.conexoes || []).forEach((id,i) => { const op=document.createElement("option"); op.value=id;
        op.textContent=(english()?"Connected Google account ":"Conta Google conectada ")+(i+1); $("conta").append(op); });
      $("conectadas").hidden=!(state.conexoes || []).length;
    }
    if (state.fase === "picker" || (state.fase === "revisar" && state.acao !== "reconectar")) $("picker").hidden=false;
    if (state.fase === "revisar") { $("revisar").hidden=false; $("arquivo").textContent=state.previa.nome_arquivo;
      $("nome").value=state.acao === "cadastro" ? state.previa.nome : state.nome_atual; $("nome").disabled=state.acao !== "cadastro";
      $("troca-aviso").hidden=state.acao !== "troca"; }
    if (state.fase === "concluido") { $("concluido").hidden=false;
      $("resultado").textContent=state.resultado.perfil.nome+(english()?" · Registration code: ":" · Código do cadastro: ")+state.resultado.id; }
    $("cancelar").hidden=["concluido","cancelado","falhou"].includes(state.fase);
  }
  async function reload() { state=await api("/api/fluxo"); render(); }
  async function action(work) {
    if(busy) return; busy=true; $("erro").hidden=true;
    document.querySelectorAll("button").forEach(b=>b.disabled=true);
    try { await work(); } catch(e) { showError(e.message); }
    finally { busy=false; document.querySelectorAll("button").forEach(b=>b.disabled=false); }
  }
  for (const provider of ["discord","google"]) $("entrar-"+provider).onclick=()=>action(async()=>{
    const data=await api("/api/login/"+provider,{}); location.assign(data.url);
  });
  $("usar").onclick=()=>action(async()=>{ await api("/api/usar",{conexao:$("conta").value}); await reload(); });
  $("cancelar").onclick=()=>action(async()=>{ await api("/api/cancelar",{}); await reload(); });
  $("confirmar").onclick=()=>action(async()=>{
    const value=await api("/api/confirmar",{nome:$("nome").value,responsabilidade:$("responsabilidade").checked});
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
    // O token só vive na memória desta página e não é escrito em URL ou storage.
  });
  action(reload);
})();
