// Adaptador do site: a página foi feita pra rodar no claude.ai (claude.use("sample") e claude.use("db")).
// Aqui as duas coisas viram chamadas pro servidor, que guarda a chave do Gemini e o limite de uso.
(() => {
  if (window.claude) return;
  const SENHA = "closure-senha";
  const lerSenha = () => { try { return localStorage.getItem(SENHA) || ""; } catch { return ""; } };
  const gravarSenha = s => { try { localStorage.setItem(SENHA, s); } catch {} };
  let senha = lerSenha();
  const pedirSenha = msg => { const s = prompt(msg); if (s !== null) { senha = s.trim(); gravarSenha(senha); } return s !== null; };

  async function api(caminho, corpo, signal) {
    for (let tent = 0; tent < 3; tent++) {
      if (!senha && !pedirSenha("Código de acesso do teste (o Mizuki te passa):")) throw { code: "senha", message: "sem código" };
      const r = await fetch(caminho, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...corpo, senha }), signal });
      const d = await r.json().catch(() => ({}));
      if (r.status === 401) { senha = ""; if (!pedirSenha("Código errado. Tenta de novo:")) throw { code: "senha", message: "sem código" }; continue; }
      if (!r.ok) throw { code: d.erro || "http_" + r.status, message: d.detalhe || "" };
      return d;
    }
    throw { code: "senha", message: "código errado" };
  }

  const sample = async (input, opts = {}) => {
    const d = await api("/api/chat", { input, tier: opts.modelTier || "quick" }, opts.signal);
    opts.onText?.({ text: d.text, delta: d.text });
    return { text: d.text, truncated: !!d.truncated };
  };
  const db = { doc: caminho => ({ set: dados => api("/api/conversa", { id: caminho.split("/").pop(), dados }) }) };
  window.claude = { use: async nome => nome === "sample" ? sample : nome === "db" ? db : null };

  // mensagens de erro do servidor, no mesmo lugar onde a página mostra as dela
  window.__ERROS_SITE = {
    senha: "Sem o código de acesso não dá pra conversar. Recarregue a página e digite o código.",
    limite_pessoa: "Você chegou no limite de mensagens por hora. Volta daqui a pouco.",
    limite_dia: "O bot chegou no limite do dia. Amanhã libera de novo.",
    cota_gemini: "A cota do Gemini acabou por agora. Tenta de novo mais tarde.",
    gemini: "O Gemini deu erro nessa resposta. Manda de novo.",
    bloqueado: "O Gemini bloqueou essa resposta. Tenta com outras palavras.",
  };
})();
