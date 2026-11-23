// Motor Node em lote: carrega o núcleo uma vez e monta muitos pedidos (o ponte.js abre um processo por pedido).
//   node lote.js NUCLEO.js perguntas.json saida.json
// perguntas.json: [{id, pers, msg}] -> saida.json: [{id, fontes: [âncoras do livro]}]
// Usado por ferramentas/auditar_consulta_pente.py. A hora fica fixa em 14h de Brasília.
const fs = require("fs"), path = require("path"), vm = require("vm");
const ler = nome => fs.readFileSync(path.join(__dirname, nome), "utf8");
const mundo = { console };
vm.createContext(mundo);
vm.runInContext(ler("antes.js") + fs.readFileSync(process.argv[2], "utf8") + "\n" + ler("depois.js"), mundo);
const agora = Date.UTC(2026, 9, 13, 17, 0);
const saida = JSON.parse(fs.readFileSync(process.argv[3], "utf8")).map(q => {
  const r = mundo.__montar({ pers: q.pers, msg: q.msg, nome: "Alex", pronomes: "", turnos: [], falas_anteriores: [], agora });
  const texto = r.input[r.input.length - 1].content;
  return { id: q.id, fontes: [...texto.matchAll(/\[Livro, âncora ([^\]]+)\]/g)].map(m => m[1]) };
});
fs.writeFileSync(process.argv[4], JSON.stringify(saida));
