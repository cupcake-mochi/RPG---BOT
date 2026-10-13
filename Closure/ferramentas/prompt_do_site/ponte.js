// Motor Node: roda o núcleo da página do site de teste (dados + lógica, sem a tela) e devolve o pedido montado.
//   node ponte.js NUCLEO.js < pedido.json > resultado.json
// O formato do pedido está em depois.js. O bot usa o motor embutido (QuickJS, em site_prompt.py); este serve
// pras ferramentas e pra conferir que os dois dão o mesmo resultado.
const fs = require("fs"), path = require("path"), vm = require("vm");
const ler = nome => fs.readFileSync(path.join(__dirname, nome), "utf8");
const mundo = { console };
vm.createContext(mundo);
vm.runInContext(ler("antes.js") + fs.readFileSync(process.argv[2], "utf8") + "\n" + ler("depois.js"), mundo);
process.stdout.write(mundo.__montarJSON(fs.readFileSync(0, "utf8")));
