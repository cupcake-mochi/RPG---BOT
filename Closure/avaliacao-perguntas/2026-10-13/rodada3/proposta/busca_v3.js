// ---------- livro: âncora dos termos acionados + os blocos que mais casam com a mensagem (busca v3) ----------
const PARADA = new Set(("a o e de da do das dos que pra para por com sem um uma uns umas no na nos nas em é eu vc voce você tu se me te meu minha seu sua isso isto esse essa aqui ai aí la lá ja já mais menos muito pouco quando como qual quais quanto quantos onde porque pq tá ta to tô ou mas nao não sim ele ela eles elas ser ter tem tenho foi vai vou pode posso faz fazer " +
  "closure kal kaltsit kal'tsit mizuki livro regra regras dele dela deles delas oque qnt qnts cm").split(" "));
// "nv2", "nvl 2", "lv2" viram "nivel 2"; palavra longa fica com as 6 primeiras letras, pra "estabilizo" achar "estabilizar",
// "habilidades" achar "habilidade" e erro no fim da palavra ("evocadr") não atrapalhar
// "iniciativa" não pode virar "inicia" junto com "inicial"
const RAIZ = w => /^(nivel|classe)\d+$/.test(w) ? w : w.startsWith("iniciativ") ? "inictv" : w.length > 6 ? w.slice(0, 6) : (w.length > 4 && w.endsWith("s") ? w.slice(0, -1) : w);
// "nível 7" também vira a palavra "nivel7", pra pergunta de um nível achar a página que diz "Nível 7."
const nrm = s => STRIP(s.toLowerCase()).replace(/(?<![a-z])(?:nv|nvl|niv|lv|lvl)\.?\s?(\d+)/g, "nivel $1").replace(/(?<![a-z])nivel\s?(\d+)/g, "nivel nivel$1").replace(/(?<![a-z])classe\s?(\d+)/g, "classe classe$1");
// sinônimo de mesa pra palavra que o livro usa
const SINONIMO = { caindo: "queda", cair: "queda", caio: "queda", upar: "nivel", level: "nivel", hp: "vida", shikig: "invoca", voar: "voo", voando: "voo", desmai: "incons",
  // verbo na primeira pessoa que não bate com o radical do livro ("agarro" e "agarrar")
  agarro: "agarra", agarre: "agarra", agarrao: "agarra", escapo: "escapa", ataco: "atacar",
  // custo e preço são a mesma pergunta ("quanto custa", "gasta quanto PE", "preço do traje"); "tank" é o Bastião
  custa: "preco", custo: "preco", custar: "preco", custam: "preco", gasta: "preco", gasto: "preco", gastar: "preco", gastam: "preco",
  tank: "bastia", tanker: "bastia", tanque: "bastia", ataquei: "atacar", corro: "correr", pulo: "pular", esquivo: "esquiv", voa: "voo" };
const tok = s => (nrm(s).match(/[a-z0-9]{3,}|(?<![a-z0-9])(?:xp|pe|pv|cd|tr|rd|ce)(?![a-z0-9])/g) || []).map(RAIZ).map(w => SINONIMO[w] || w);
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
// títulos de uma palavra que também são palavra de papo ("tem tempo?", "no começo") não abrem a busca sozinhos
const TITULO_COMUM = new Set(tok("tempo falha encerrar começo novo livre resposta caminho trilha"));
// título de duas palavras feito só de palavra comum ("De novo", "Uma vez") não conta como citado
const conteudo = t => { const ws = tok(t).filter(w => !PARADA.has(w)); return ws.length >= 2 || ws.some(w => (DF.get(w) || 0) <= 60); };
const TITULOS = D.livro.map(b => [...new Set([b.titulo, ...(b.titulos || [])])].filter(t => !/continua/i.test(t)).map(t => " " + nrm(t).replace(/[^a-z0-9]+/g, " ").trim() + " ").filter(t => t.split(" ").filter(Boolean).length >= 2 && conteudo(t)));
// Caminhos do livro: o nome do Caminho, ou o título de uma página dele com uma palavra só ("Executor"), puxa as páginas do Caminho
const CAMINHOS = ["bastiao", "vanguarda", "guia", "emanador", "evocador", "incursor"];
const FAM = D.livro.map(b => b.ancora.split("--")[0]);
const FAMILIA_DE = new Map(CAMINHOS.map(c => [RAIZ(c), c]));
// termos com endereço: o índice e o glossário do livro ligam cada termo à página que o define ("[Agarrar](#geral--manobras)");
// a linha em negrito de uma tabela ("| **Esquivar** |") e o nome de item de catálogo ("| Katana (espada curva) |", com preço ou dano) também
const POS = new Map(D.livro.map((b, i) => [b.ancora, i]));
const TERMO = new Map();
// palavra solta só vale se for pouco usada no livro (até 40 páginas; 100 quando é o título de uma seção, como "Iniciativa");
// nome de Caminho fica de fora porque já tem a regra de família
const poeTermo = (nome, i, limite = 40) => { const k = tok(nome.replace(/\(.*?\)|\*/g, " ")).filter(w => !PARADA.has(w)).join(" "); if (k && !FAMILIA_DE.has(k) && !TITULO_COMUM.has(k) && (k.includes(" ") || (DF.get(k) || 999) <= limite)) { if (!TERMO.has(k)) TERMO.set(k, new Set()); TERMO.get(k).add(i); } };
D.livro.forEach((b, i) => {
  for (const m of b.texto.matchAll(/\[([^\]]+)\]\(#([\w-]+)\)/g)) if (POS.has(m[2])) poeTermo(m[1], POS.get(m[2]));
  for (const m of b.texto.matchAll(/^\| \*\*([^*|]+)\*\* \|/gm)) poeTermo(m[1], i);
  for (const tab of b.texto.split(/\n(?!\|)/)) if (/^\|[^\n]*(Dano|Preço)/.test(tab.trim())) for (const m of tab.matchAll(/^\| ([^|*]+) \|/gm)) poeTermo(m[1], i);
  // títulos de seção, inteiros e em partes ("Agarrar, derrubar e empurrar" também vale "derrubar")
  if (!/exemplo/i.test(b.titulo)) for (const t of [b.titulo, ...(b.titulos || [])]) if (!/continua|exemplo/i.test(t)) for (const parte of [t, ...t.split(/,| e /)]) poeTermo(parte, i, t === b.titulo ? 100 : 40);
});
const termosNa = t => { const f = " " + tok(t).join(" ") + " ", r = new Map(); for (const [k, is] of TERMO) if (f.includes(" " + k + " ")) for (const i of is) r.set(i, Math.max(r.get(i) || 0, k.split(" ").length)); return r; };
D.livro.forEach((b, i) => { const t = tok(b.titulo); if (CAMINHOS.includes(FAM[i]) && t.length === 1 && !FAMILIA_DE.has(t[0])) FAMILIA_DE.set(t[0], FAM[i]); });
// níveis que a página abre como habilidade ("**Nível 15.**"), que valem mais que um número de nível citado no meio do texto
const NIVCAB = D.livro.map(b => new Set([...b.texto.matchAll(/\*\*N[ií]vel (\d+)\.\*\*/g)].map(m => "nivel" + m[1])));
// coisa definida em linha de tabela ("| Katana (espada curva) | 1 | 1d8 Cortante |...", "| **Esquivar** | ..."): o nome na primeira célula aponta pra seção que traz os números; linha com cinco colunas ou mais é ficha de item e vale o dobro
const LINHA = D.livro.map(b => { const m = new Map(); for (const l of b.texto.split("\n")) { if (!l.startsWith("|") || /^\|\s*:?-/.test(l)) continue; const cel = l.split("|").slice(1, -1); if (cel.length < 2) continue; for (const w of tok(cel[0])) if (!PARADA.has(w)) m.set(w, Math.max(m.get(w) || 0, cel.length >= 5 || /^\s*\*\*/.test(cel[0]) ? 2 : 1)); } return m; });
// título principal da seção, pra pergunta que cobre o título inteiro ("turno" e "Turnos", "voar" e "Voo")
const TPRIN = D.livro.map(b => tok(b.titulo).filter(w => !PARADA.has(w)));
// página de exemplo de mesa conta menos que a regra, a não ser que peçam exemplo
const EXEMPLO = D.livro.map(b => /exemplo/i.test(b.titulo));
const TABELA = D.livro.map(b => /Progressão d[oa] (Caminho|Trilha)/.test(b.texto));
const REGRA = /(?<![a-z0-9])(d4|d6|d8|d10|d12|d20|rol\w*|dado\w*|teste\w*|dano|ataq\w*|defe\w*|bloque\w*|apar\w*|esquiv\w*|critic\w*|bonus|penalidade|turno\w*|rodada\w*|acao|acoes|reacao|movimento|passos?|alcance|descans\w*|vida|integridade|condic\w*|pericia\w*|atributo\w*|ficha\w*|nivel|niveis|nv\d*|nvl\d*|lv\d*|habilidade\w*|caminho\w*|trilha\w*|origem|origens|legado\w*|classe\w*|feitic\w*|grau|tecnica\w*|expansao|dominio|receptaculo|encarnado|maldic\w*|arma\w*|cobertura|regra\w*|livro|mestre|como funciona|o que e|o que acontece|da pra|pode usar|quanto\w*|combate\w*|escond\w*|estabiliz\w*|caid[oa]s?|cair|queda\w*|personagem|jogar de|sistema|subir|subo|upar|xp|ganh\w*|agarr\w*|derrub\w*|empurr\w*|voar|voo|voand\w*|iniciativ\w*)(?![a-z0-9])/;
// pergunta curta de seguimento ("e no nível 7?", "e o socorrista?", "quanto custa?") herda o assunto da mensagem anterior
const t0 = s => STRIP(s.toLowerCase()).trim();
const SEGUIMENTO = /^(e|mas|entao|tipo|como assim)\b|\b(dele|dela|disso|nisso|essa habilidade|esse)\b/;
// palavras de conversa que por acaso estão no livro ("to meio perdido", "última pergunta"): não entram na busca
const CONVERSA = new Set(tok("tudo perdido perdida entendi entender obrigado obrigada ultima ultimo frase mesmo duvida pergunta explica explicar certo valeu beleza"));
// a mensagem anterior só passa o assunto adiante se ela mesma era pergunta de regra
const temCaraDeRegra = s => REGRA.test(nrm(s)) || tok(s).some(w => FAMILIA_DE.has(w));
function buscar(qPal, familia, nivel, numNivel = []) {
  return BTOK.map((c, i) => {
    if (familia.size && !familia.has(FAM[i])) return [0, null];
    let s = 0; for (const [w, peso] of qPal) { const f = c.get(w); if (f) s += peso * Math.log(1 + NB / DF.get(w)) * (1 + Math.log(f)); }
    // pergunta de um nível certo ("nivel7") puxa a página que abre com "Nível 7."; sem número, a tabela de progressão vem na frente
    if (familia.size && nivel && TABELA[i]) s += numNivel.length ? 2 : 5;
    if (familia.size) for (const w of numNivel) if (NIVCAB[i].has(w)) s += 8; else if (c.has(w)) s += 4;
    // palavra da pergunta no título da seção ("crítico" em "Dano e crítico", "vida" e "zero" em "Vida a zero"); palavra que o livro usa em toda parte ("dano", "turno") vale pouco
    for (const [w, peso] of qPal) if (peso === 1 && TTOK[i].has(w)) s += DF.get(w) > 150 ? 1 : 3;
    for (const [w, peso] of qPal) if (peso === 1 && DF.get(w) <= 30 && LINHA[i].has(w)) s += 4 * LINHA[i].get(w);
    if (TPRIN[i].length && TPRIN[i].every(w => qPal.get(w) === 1)) s += 3;
    if (EXEMPLO[i] && !qPal.has("exempl")) s *= 0.6;
    return [s, D.livro[i], i];
  }).filter(x => x[1]).sort((a, b) => b[0] - a[0]);
}
function blocosLivro(texto, termos, anteriores = [], fundo = 0) {
  texto = semIdioma(texto); anteriores = anteriores.map(semIdioma);
  const ancoras = [];
  for (const e of termos) { const m = e.content.match(/âncora ([\w-]+)/); if (m) { const b = D.livro.find(x => x.ancora === m[1]); if (b && !ancoras.includes(b)) ancoras.push(b); } }
  // pergunta com assunto próprio ("como estabilizo um aliado caído?") não herda a anterior; só a curta de verdade ou a que começa com "e", "como assim"...
  const proprias = tok(texto).filter(w => !PARADA.has(w)).length, liga = SEGUIMENTO.test(t0(texto));
  // curta só herda se ainda tiver cara de regra ("quanto custa?", "e de 20?"); "gosta de café?" depois de uma regra não puxa livro
  // a anterior é a última mensagem; a penúltima só entra quando a última também era seguimento ("e no nível 7?" depois de "e o guia nv2?")
  const ult = anteriores[anteriores.length - 1] || "", penult = anteriores.length > 1 ? anteriores[anteriores.length - 2] : "";
  const ultSeg = SEGUIMENTO.test(t0(ult)) || tok(ult).filter(w => !PARADA.has(w)).length <= 2;
  const anterior = ultSeg && penult ? penult + " " + ult : ult;
  const t = nrm(texto).replace(/atac\w*\s+(duas|2)\s+vezes|dois ataques|mais de um ataque/g, "$& ataque extra"), seg = anterior && temCaraDeRegra(anterior) && (liga || (proprias <= 2 && (REGRA.test(t) || /\d/.test(t))));
  const qPal = new Map();
  // a correção de digitação só entra depois que a mensagem já tem cara de regra; antes, "música" virava "munição"
  for (const w of tok(texto)) if (!PARADA.has(w) && !CONVERSA.has(w) && DF.has(w)) qPal.set(w, 1);
  // "e no 15?" depois de uma pergunta de nível: o número é o nível
  if (seg && /(?<![a-z])nivel(?![a-z0-9])/.test(nrm(anterior))) for (const n of t.match(/(?<![a-z0-9])\d{1,2}(?![a-z0-9])/g) || []) if (DF.has("nivel" + n)) qPal.set("nivel" + n, 1);
  // "e o bloquear?" depois de uma pergunta do Guia: palavra que dá nome a poucas seções de fora do Caminho da anterior é assunto novo, e a anterior não passa nada
  const herdada = new Set(seg ? tok(anterior).filter(w => FAMILIA_DE.has(w)).map(w => FAMILIA_DE.get(w)) : []);
  const novo = seg && [...qPal.keys()].some(w => { if (w.length < 5 || CONVERSA.has(w) || /^nivel\d+$/.test(w) || DF.get(w) > 100) return false; const ts = TTOK.map((T, i) => T.has(w) ? i : -1).filter(i => i >= 0); return ts.length && ts.length <= 3 && ts.some(i => !herdada.has(FAM[i])); });
  const herda = seg && !novo, temNivel = [...qPal.keys()].some(w => /^nivel\d+$/.test(w));
  // o nível da pergunta nova substitui o da anterior ("e no 15?" depois de "nível 7")
  if (herda) for (const w of tok(anterior)) if (!PARADA.has(w) && DF.has(w) && !qPal.has(w) && !(temNivel && /^nivel\d+$/.test(w))) qPal.set(w, 0.5);
  const frase = " " + t.replace(/[^a-z0-9]+/g, " ") + " ";
  const fraseAnt = herda ? " " + nrm(anterior).replace(/[^a-z0-9]+/g, " ") + " " : "";
  const titulo = new Map(); TITULOS.forEach((ts, i) => { if (ts.some(x => frase.includes(x))) titulo.set(i, 10); else if (fraseAnt && ts.some(x => fraseAnt.includes(x))) titulo.set(i, 6); });
  const familia = new Set([...qPal].filter(([w, p]) => p === 1 && FAMILIA_DE.has(w)).map(([w]) => FAMILIA_DE.get(w)));
  if (!familia.size && herda && (liga || proprias <= 1)) for (const f of herdada) familia.add(f);
  const achados = [];
  // palavra rara que é título de seção ("latente", "exaustão") também conta; palavra comum ("tudo") não
  // palavra de regra comum ("dano", "vida", "carga", "golpe") só puxa o livro em pergunta; afirmação solta ("que dia cheio") não
  const PERG = /\?|(?<![a-z])(?:como|cm|qual|quais|quanto|quantos|quanta|quantas|qnto|qnta|qntos|qnts|qnt|qto|qtos|pode|posso|podemos|da pra|oq|o que|oque|fun[cs]iona\w*|serve|precis\w*|explic\w*|me diz|me fala|fala d[eoa]|fala sobre|me conta|quero saber|duvida|resume|resumo|regra|lista|mostra|ensina)(?![a-z])/;
  // trecho entre aspas costuma ser a pessoa citando a própria personagem ("não rolo dado"), não pergunta de regra
  const semAspas = t.replace(/"[^"]*"|“[^”]*”/g, " "), pergunta = PERG.test(semAspas);
  // termo do livro só conta na frase que pergunta ("tô sem ideia do que assistir" não abre a busca por "ideia")
  const comTermo = new Map(); for (const f of texto.split(/(?<=[?!.])\s+|\n/)) if (PERG.test(nrm(f))) for (const [i, n] of termosNa(f)) comTermo.set(i, Math.max(comTermo.get(i) || 0, n));
  if (qPal.size && (termos.length || familia.size || titulo.size || seg || comTermo.size || (pergunta && REGRA.test(semAspas)))) {
    for (const w of tok(texto)) if (!PARADA.has(w) && !CONVERSA.has(w) && !DF.has(w)) { const c = corrigir(w); if (DF.has(c) && !CONVERSA.has(c) && !qPal.has(c)) qPal.set(c, 1); }
    const nivel = qPal.has("nivel") || qPal.has("habili");
    const numNivel = [...qPal.keys()].filter(w => /^nivel\d+$/.test(w) && qPal.get(w) === 1);
    const nota = buscar(qPal, familia, nivel, numNivel).map(([s, b, i]) => [s + (titulo.get(i) || 0) + (comTermo.has(i) ? 4 + 4 * comTermo.get(i) : 0), b]).sort((a, b) => b[0] - a[0]);
    // o melhor entra se tiver nota mínima; o segundo só se chegar perto do primeiro
    if (nota[0] && nota[0][0] >= 4) { achados.push(nota[0][1]); if (nota[1] && nota[1][0] >= Math.max(6, 0.6 * nota[0][0])) achados.push(nota[1][1]); }
    // pergunta de um Caminho sem habilidade nem nível nomeado ("o guia gasta quanto PE pra ajudar?"): a página da progressão, que traz a habilidade base, entra junto
    if (achados.length && familia.size === 1 && !titulo.size && !numNivel.length) {
      const tab = nota.find(([s, b]) => /Progressão do Caminho/.test(b.texto));
      if (tab && !achados.includes(tab[1])) achados.splice(1, 0, tab[1]);
    }
    // comparação ("latente e descendente"): palavra da pergunta que dá nome a poucas seções e ficou sem seção nenhuma puxa a melhor delas
    if (achados.length) for (const w of qPal.keys()) {
      if (qPal.get(w) !== 1 || w.length < 5 || CONVERSA.has(w) || /^nivel\d+$/.test(w) || DF.get(w) > 100) continue;
      const comW = TTOK.filter(T => T.has(w)).length;
      if (!comW || comW > 3 || achados.some(b => TTOK[D.livro.indexOf(b)].has(w))) continue;
      const x = nota.find(([s, b]) => tok(b.titulo).includes(w)) || nota.find(([s, b]) => TTOK[D.livro.indexOf(b)].has(w));
      if (x && x[0] >= Math.max(6, 0.4 * nota[0][0])) achados.splice(1, 0, x[1]);
    }
  }
  // "e do 11?", "e de 20?": só muda o número, então a seção da pergunta anterior vem junto (na frente, fora de Caminho)
  if (herda && !fundo && proprias <= 1 && /\d/.test(t)) {
    const antes = blocosLivro(ult, ativar(ult).termos, penult ? [penult] : [], 1).slice(0, familia.size ? 1 : 2).filter(b => !achados.includes(b));
    achados.splice(familia.size ? 1 : 0, 0, ...antes);
  }
  // até três blocos: o que a busca achou vem antes da âncora genérica do termo ("Caminho", "PE")
  const out = [];
  for (const b of [...achados.slice(0, 1), ...ancoras.slice(0, 1), ...achados.slice(1), ...ancoras.slice(1)]) if (!out.includes(b)) out.push(b);
  return out.slice(0, 3);
}

