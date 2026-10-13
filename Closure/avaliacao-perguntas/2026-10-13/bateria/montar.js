// Roda o JS da página de teste fora do navegador e monta o prompt de cada pergunta.
// uso: node montar.js PAGINA.html PERGUNTAS.json SAIDA.json [kal|clo] [hora]
const fs = require("fs");
const [,, pag, perg, saida, persArg, horaArg] = process.argv;
const html = fs.readFileSync(pag, "utf8");
const js = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
const el = () => new Proxy({ value: "", style: {}, classList: { add() {}, remove() {} } }, { get: (t, k) => k in t ? t[k] : (typeof k === "string" ? (() => el()) : undefined), set: (t, k, v) => (t[k] = v, true) });
global.document = { getElementById: () => el(), createElement: () => el(), body: el() };
global.window = {}; global.navigator = {};
global.setInterval = () => 0;
const hora = horaArg ? +horaArg : 14;
const RealDate = Date;
global.Date = class extends RealDate { constructor(...a) { if (a.length) super(...a); else { const d = new RealDate(); d.setUTCHours(hora + 3, 0, 0, 0); super(d.getTime()); } } static now() { return new Date().getTime(); } };
const fn = new Function(js + `
;return { setPers: p => { pers = p; }, setTurnos: t => { turnos = t; }, montarPrompt, blocosLivro, ativar };`);
const api = fn();
api.setPers(persArg || "kal");
const P = JSON.parse(fs.readFileSync(perg, "utf8"));
const out = [];
for (const q of P) {
  // q: {id, msg, hist?: [[user, bot], ...], nome?}
  const turnos = [];
  for (const [u, b] of q.hist || []) { turnos.push({ de: "user", nome: q.nome || "Rafa", texto: u }); turnos.push({ de: "bot", pers: persArg || "kal", texto: b }); }
  api.setTurnos(turnos);
  const r = api.montarPrompt(q.msg, q.nome || "Rafa");
  out.push({ id: q.id, msg: q.msg, ativadas: r.ativadas, input: r.input });
}
fs.writeFileSync(saida, JSON.stringify(out, null, 1));
for (const o of out) console.log(o.id, "|", o.msg, "\n    ->", o.ativadas.filter(a => !/^(Sempre|Personagem|Mundo: premissa)/.test(a)).join(" ; "));
