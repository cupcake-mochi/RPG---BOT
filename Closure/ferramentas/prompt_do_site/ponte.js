// Roda o núcleo da página do site de teste (dados + lógica, sem a tela) e devolve o prompt montado.
//   node ponte.js NUCLEO.js < pedido.json > resultado.json
// pedido: { pers: "kal"|"clo", msg, nome, pronomes, turnos: [{de:"user",nome,texto} | {de:"bot",pers,texto}], hora: {h, m} }
// A hora é a de Brasília; sem ela vale a de agora. Cada execução começa do zero: o histórico vem em `turnos`.
const fs = require("fs"), vm = require("vm");
const codigo = fs.readFileSync(process.argv[2], "utf8");
const pedido = JSON.parse(fs.readFileSync(0, "utf8"));
const agora = pedido.hora ? Date.UTC(2026, 9, 13, pedido.hora.h + 3, pedido.hora.m || 0) : Date.now();
class Data extends Date { static now() { return agora; } }
const mundo = { document: { getElementById: () => ({ value: pedido.pronomes || "" }) }, Date: Data, console };
vm.createContext(mundo);
vm.runInContext(codigo + `
;globalThis.__montar = p => { pers = p.pers; turnos = p.turnos || []; return montarPrompt(p.msg, p.nome || ""); };
globalThis.__versoes = D.versoes;`, mundo);
const r = mundo.__montar(pedido);
process.stdout.write(JSON.stringify({ input: r.input, ativadas: r.ativadas, versoes: mundo.__versoes }));
