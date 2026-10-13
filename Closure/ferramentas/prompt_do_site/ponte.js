// Roda o núcleo da página do site de teste (dados + lógica, sem a tela) e devolve o prompt montado.
//   node ponte.js NUCLEO.js < pedido.json > resultado.json
// pedido: { pers: "kal"|"clo", msg, nome, pronomes, turnos: [{de:"user",nome,texto} | {de:"bot",pers,texto}], hora: {h, m},
//           falas_anteriores: ["texto", ...],    (últimas falas da personagem no canal, de outras conversas; opcional)
//           estado: { bloco: "[Estado agora: ...]", lembretes: ["...", ...] } }   (o estado que o bot calculou; opcional)
// A hora é a de Brasília; sem ela vale a de agora. Cada execução começa do zero: o histórico vem em `turnos`.
const fs = require("fs"), vm = require("vm");
const codigo = fs.readFileSync(process.argv[2], "utf8");
const pedido = JSON.parse(fs.readFileSync(0, "utf8"));
const agora = pedido.hora ? Date.UTC(2026, 9, 13, pedido.hora.h + 3, pedido.hora.m || 0) : Date.now();
class Data extends Date { static now() { return agora; } }
const mundo = { document: { getElementById: () => ({ value: pedido.pronomes || "" }) }, Date: Data, console };
vm.createContext(mundo);
vm.runInContext(codigo + `
;globalThis.__montar = p => {
  pers = p.pers;
  const reais = p.turnos || [];
  // Falas de conversas anteriores: a página só olha a conversa atual pra avisar de repetição. Aqui o mesmo
  // detector dela (repeticoes) roda com as últimas falas da personagem no canal na frente das desta conversa.
  let aviso = null;
  if ((p.falas_anteriores || []).length) {
    turnos = p.falas_anteriores.map(texto => ({ de: "bot", pers: p.pers, texto })).concat(reais);
    aviso = repeticoes();
  }
  turnos = reais;
  // Estado do bot: a página escreve "canal normal; carga 0" fixo. Com o estado calculado, o bloco dele entra no lugar
  // e o lembrete ganha as linhas dele, no máximo duas contando a de fora do plantão (que é da página e tem prioridade).
  if (p.estado) {
    const daPagina = foraDoPlantao;
    linhaEstado = () => p.estado.bloco;
    foraDoPlantao = (...a) => { const f = daPagina(...a); return f + (p.estado.lembretes || []).slice(0, f ? 1 : 2).map(l => "\\n[" + l + "]").join(""); };
  }
  const r = montarPrompt(p.msg, p.nome || "");
  if (aviso !== null) {
    const ultimo = r.input[r.input.length - 1], so_desta = repeticoes();
    if (so_desta && ultimo.content.endsWith(so_desta)) ultimo.content = ultimo.content.slice(0, -so_desta.length);
    ultimo.content += aviso.replace("Você já usou nesta conversa:", "Você já usou nas suas últimas respostas:");
  }
  return r;
};
globalThis.__versoes = D.versoes;`, mundo);
const r = mundo.__montar(pedido);
process.stdout.write(JSON.stringify({ input: r.input, ativadas: r.ativadas, versoes: mundo.__versoes }));
