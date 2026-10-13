// Mostra por dentro a busca do livro da página: palavras, gatilho e as notas das melhores seções.
// uso: node busca_dbg.js PAGINA.html "pergunta" ["mensagem anterior" ...]
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
let js = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
js = js.replace("const nota = buscar(", "globalThis.__q = qPal; globalThis.__fam = familia; const nota = globalThis.__nota = buscar(");
const el = (v = "") => new Proxy({ value: v, style: {}, classList: { add() {}, remove() {} } }, { get: (t, k) => k in t ? t[k] : (typeof k === "string" ? (() => el()) : undefined), set: (t, k, v) => (t[k] = v, true) });
global.document = { getElementById: () => el(), createElement: () => el(), body: el() };
global.window = {}; global.navigator = {}; global.claude = { use: async () => null }; global.setInterval = () => 0;
const api = new Function(js + `\n;return { blocosLivro, ativar, D, DF };`)();
const [q, ...ant] = process.argv.slice(3);
globalThis.__nota = null;
const out = api.blocosLivro(q, api.ativar(q).termos, ant);
console.log("termos:", api.ativar(q).termos.map(e => e.content.slice(0, 40)));
if (!globalThis.__nota) { console.log("gatilho não disparou; saída:", out.map(b => b.ancora)); process.exit(); }
console.log("palavras:", [...globalThis.__q].map(([w, p]) => `${w}${p < 1 ? "(" + p + ")" : ""}:${api.DF.get(w)}`).join(" "), "| família:", [...globalThis.__fam].join(","));
for (const [s, b] of globalThis.__nota.slice(0, 8)) console.log("  ", s.toFixed(1), b.ancora, "|", b.titulo);
console.log("saída:", out.map(b => b.ancora).join("  "));
