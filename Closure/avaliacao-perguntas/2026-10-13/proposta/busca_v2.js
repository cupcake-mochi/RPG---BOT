// ---------- livro: âncora dos termos acionados + os blocos que mais casam com a mensagem (busca v2) ----------
const PARADA = new Set(("a o e de da do das dos que pra para por com sem um uma uns umas no na nos nas em é eu vc voce você tu se me te meu minha seu sua isso isto esse essa aqui ai aí la lá ja já mais menos muito pouco quando como qual quais quanto quantos onde porque pq tá ta to tô ou mas nao não sim ele ela eles elas ser ter tem tenho foi vai vou pode posso faz fazer " +
  "closure kal kaltsit kal'tsit mizuki livro regra regras dele dela deles delas oque qnt qnts cm").split(" "));
// "nv2", "nvl 2", "lv2" viram "nivel 2"; palavra longa fica com as 6 primeiras letras, pra "estabilizo" achar "estabilizar",
// "habilidades" achar "habilidade" e erro no fim da palavra ("evocadr") não atrapalhar
const RAIZ = w => w.length > 6 ? w.slice(0, 6) : (w.length > 4 && w.endsWith("s") ? w.slice(0, -1) : w);
const nrm = s => STRIP(s.toLowerCase()).replace(/(?<![a-z])(?:nv|nvl|niv|lv|lvl)\.?\s?(\d+)/g, "nivel $1");
// sinônimo de mesa pra palavra que o livro usa
const SINONIMO = { caindo: "queda", cair: "queda", caio: "queda", upar: "nivel", level: "nivel", hp: "vida", shikig: "invoca", voar: "voo", voando: "voo", desmai: "incons" };
const tok = s => (nrm(s).match(/[a-z0-9]{3,}/g) || []).map(RAIZ).map(w => SINONIMO[w] || w);
const DF = new Map(), BTOK = D.livro.map(b => {
  const c = new Map(); for (const w of tok(b.titulo + " " + b.titulo + " " + (b.titulos || []).join(" ") + " " + b.texto)) c.set(w, (c.get(w) || 0) + 1);
  for (const w of c.keys()) DF.set(w, (DF.get(w) || 0) + 1); return c;
});
const NB = D.livro.length;
// erro de digitação no meio da palavra ("funsiona"): troca pela palavra do livro a uma letra de distância, com a mesma inicial
const VOCAB = [...DF.keys()];
function perto(a, b) {
  if (a[0] !== b[0] || Math.abs(a.length - b.length) > 1) return false;
  let i = 0, j = 0, e = 0;
  while (i < a.length && j < b.length) { if (a[i] === b[j]) { i++; j++; continue; } if (++e > 1) return false; if (a.length > b.length) i++; else if (b.length > a.length) j++; else { i++; j++; } }
  return e + (a.length - i) + (b.length - j) <= 1;
}
const corrigir = w => DF.has(w) || w.length < 5 ? w : (VOCAB.filter(v => perto(w, v)).sort((x, y) => DF.get(y) - DF.get(x))[0] || w);
// títulos do livro com duas palavras ou mais ("Olhos Em Mim", "Vida a zero", "Abrir Caminho") contam como frase exata
const TTOK = D.livro.map(b => new Set(tok([b.titulo, ...(b.titulos || [])].filter(t => !/continua/i.test(t)).join(" ")).filter(w => !PARADA.has(w))));
const TITULOS = D.livro.map(b => [...new Set([b.titulo, ...(b.titulos || [])])].filter(t => !/continua/i.test(t)).map(t => " " + nrm(t).replace(/[^a-z0-9]+/g, " ").trim() + " ").filter(t => t.split(" ").filter(Boolean).length >= 2));
// Caminhos do livro: o nome do Caminho, ou o título de uma página dele com uma palavra só ("Executor"), puxa as páginas do Caminho
const CAMINHOS = ["bastiao", "vanguarda", "guia", "emanador", "evocador", "incursor"];
const FAM = D.livro.map(b => b.ancora.split("--")[0]);
const FAMILIA_DE = new Map(CAMINHOS.map(c => [RAIZ(c), c]));
D.livro.forEach((b, i) => { const t = tok(b.titulo); if (CAMINHOS.includes(FAM[i]) && t.length === 1 && !FAMILIA_DE.has(t[0])) FAMILIA_DE.set(t[0], FAM[i]); });
const TABELA = D.livro.map(b => /Progressão d[oa] (Caminho|Trilha)/.test(b.texto));
const REGRA = /(?<![a-z0-9])(d4|d6|d8|d10|d12|d20|rol\w*|dado\w*|teste\w*|dano|ataq\w*|defe\w*|bloque\w*|apar\w*|esquiv\w*|critic\w*|bonus|penalidade|turno\w*|rodada\w*|acao|acoes|reacao|movimento|passos?|alcance|descans\w*|vida|integridade|condic\w*|pericia\w*|atributo\w*|ficha\w*|nivel|niveis|nv\d*|nvl\d*|lv\d*|habilidade\w*|caminho\w*|trilha\w*|origem|origens|legado\w*|classe\w*|feitic\w*|grau|tecnica\w*|expansao|dominio|receptaculo|encarnado|maldic\w*|arma\w*|cobertura|regra\w*|livro|mestre|como funciona|o que e|o que acontece|da pra|pode usar|quanto\w*|combate\w*|escond\w*|estabiliz\w*|caid[oa]s?|cair|queda\w*|personagem|jogar de|sistema|subir|subo|upar|xp|ganh\w*)(?![a-z0-9])/;
// pergunta curta de seguimento ("e no nível 7?", "e o socorrista?", "quanto custa?") herda o assunto da mensagem anterior
const SEGUIMENTO = /^(e|mas|entao|tipo)\b|\b(dele|dela|disso|nisso|essa habilidade|esse)\b/;
// a mensagem anterior só passa o assunto adiante se ela mesma era pergunta de regra
const temCaraDeRegra = s => REGRA.test(nrm(s)) || tok(s).some(w => FAMILIA_DE.has(w));
function buscar(qPal, familia, nivel) {
  return BTOK.map((c, i) => {
    if (familia.size && !familia.has(FAM[i])) return [0, null];
    let s = 0; for (const [w, peso] of qPal) { const f = c.get(w); if (f) s += peso * Math.log(1 + NB / DF.get(w)) * (1 + Math.log(f)); }
    if (familia.size && nivel && TABELA[i]) s += 5;
    // palavra da pergunta no título da seção ("crítico" em "Dano e crítico", "vida" e "zero" em "Vida a zero")
    for (const [w, peso] of qPal) if (peso === 1 && TTOK[i].has(w)) s += 3;
    return [s, D.livro[i], i];
  }).filter(x => x[1]).sort((a, b) => b[0] - a[0]);
}
function blocosLivro(texto, termos, anterior = "") {
  const ancoras = [];
  for (const e of termos) { const m = e.content.match(/âncora ([\w-]+)/); if (m) { const b = D.livro.find(x => x.ancora === m[1]); if (b && !ancoras.includes(b)) ancoras.push(b); } }
  const t = nrm(texto), seg = anterior && temCaraDeRegra(anterior) && (tok(texto).filter(w => !PARADA.has(w)).length <= 3 || SEGUIMENTO.test(t.trim()));
  const qPal = new Map();
  for (const w of tok(texto)) if (!PARADA.has(w)) { const c = corrigir(w); if (DF.has(c)) qPal.set(c, 1); }
  if (seg) for (const w of tok(anterior)) if (!PARADA.has(w) && DF.has(w) && !qPal.has(w)) qPal.set(w, 0.5);
  const frase = " " + t.replace(/[^a-z0-9]+/g, " ") + " ";
  const fraseAnt = seg ? " " + nrm(anterior).replace(/[^a-z0-9]+/g, " ") + " " : "";
  const titulo = new Map(); TITULOS.forEach((ts, i) => { if (ts.some(x => frase.includes(x))) titulo.set(i, 10); else if (fraseAnt && ts.some(x => fraseAnt.includes(x))) titulo.set(i, 6); });
  const familia = new Set([...qPal].filter(([w, p]) => p === 1 && FAMILIA_DE.has(w)).map(([w]) => FAMILIA_DE.get(w)));
  if (!familia.size && seg) for (const w of tok(anterior)) if (FAMILIA_DE.has(w)) familia.add(FAMILIA_DE.get(w));
  const achados = [];
  // palavra rara que é título de seção ("latente", "exaustão") também conta; palavra comum ("tudo") não
  const noTitulo = [...qPal].some(([w, p]) => p === 1 && w.length >= 5 && DF.get(w) <= 40 && TTOK.some(T => T.has(w)));
  if (qPal.size && (termos.length || familia.size || titulo.size || seg || noTitulo || REGRA.test(t))) {
    const nivel = qPal.has("nivel") || qPal.has("habili");
    const nota = buscar(qPal, familia, nivel).map(([s, b, i]) => [s + (titulo.get(i) || 0), b]).sort((a, b) => b[0] - a[0]);
    // o melhor entra se tiver nota mínima; o segundo só se chegar perto do primeiro
    if (nota[0] && nota[0][0] >= 4) { achados.push(nota[0][1]); if (nota[1] && nota[1][0] >= Math.max(6, 0.6 * nota[0][0])) achados.push(nota[1][1]); }
  }
  // até três blocos: o que a busca achou vem antes da âncora genérica do termo ("Caminho", "PE")
  const out = [];
  for (const b of [...achados.slice(0, 1), ...ancoras.slice(0, 1), ...achados.slice(1), ...ancoras.slice(1)]) if (!out.includes(b)) out.push(b);
  return out.slice(0, 3);
}
