// Monta um turno com o JS da própria página de teste, pra conversa simulada receber exatamente o que a página manda.
// uso: node pagina_turno.js PAGINA.html < entrada.json   (entrada: {pers, hora:"HH:MM", nome, pron, msg, hist:[{de, texto}]})
// imprime JSON: {ultimo, ativadas}
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const E = JSON.parse(fs.readFileSync(0, "utf8"));
const js = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
const el = (v = "") => new Proxy({ value: v, style: {}, classList: { add() {}, remove() {} } }, { get: (t, k) => k in t ? t[k] : (typeof k === "string" ? (() => el()) : undefined), set: (t, k, v) => (t[k] = v, true) });
const pron = el(E.pron || "");
global.document = { getElementById: id => id === "pron" ? pron : el(), createElement: () => el(), body: el() };
global.window = {}; global.navigator = {}; global.claude = { use: async () => null };
global.setInterval = () => 0;
const [hh, mm] = E.hora.split(":").map(Number);
const agora = Date.UTC(2026, 9, 13, hh + 3, mm);
const RealDate = Date;
global.Date = class extends RealDate { constructor(...a) { if (a.length) super(...a); else super(agora); } static now() { return agora; } };
const api = new Function(js + `\n;return { setPers: p => { pers = p; }, setTurnos: t => { turnos = t; }, montarPrompt };`)();
api.setPers(E.pers);
api.setTurnos(E.hist.map(t => t.de === "user" ? { de: "user", nome: E.nome, texto: t.texto } : { de: "bot", pers: E.pers, texto: t.texto }));
const r = api.montarPrompt(E.msg, E.nome);
process.stdout.write(JSON.stringify({ ultimo: r.input[r.input.length - 1].content, ativadas: r.ativadas }));
