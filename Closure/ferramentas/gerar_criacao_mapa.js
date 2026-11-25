'use strict';
// Gera src/carteira_viva/criacao_mapa.json e o esperado dos testes a partir do repositório da ficha.
// Uso: node ferramentas/gerar_criacao_mapa.js <pasta do repositório Ficha---RPG-JJK>
// As regras não são reescritas aqui: as funções vêm do Codigo.gs e rodam como estão.
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const raiz = path.resolve(process.argv[2] || '.'), aqui = path.resolve(__dirname, '..');
const ctx = {};
vm.createContext(ctx);
vm.runInContext(require(path.join(raiz, 'medidas/carregar-ficha.js')).fontes(), ctx);
vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script/Habilidades.gs'), 'utf8') +
  '\nglobalThis.LIVRO=HABILIDADES_DO_LIVRO_;globalThis.MEDIDA=MEDIDA_DAS_CARTAS_;', ctx);
const codigo = fs.readFileSync(path.join(raiz, 'apps-script/Codigo.gs'), 'utf8');
const corpo = n => {
  const s = codigo.indexOf('function ' + n + '('), e = codigo.indexOf('\n}', s);
  if (s < 0 || e < 0) throw Error('Função ausente: ' + n);
  return codigo.slice(s, e + 2);
};
const FUNCOES = ['tabelaDaDados_', 'periciasDoCaminho_', 'trilhaQueFica_', 'habilidadeQueFica_', 'notaDaCarta_',
  'cartasDaFicha_', 'linhasDoTexto_', 'alturaDaCaixa_', 'alturasQueEsticam_', 'negritosDoTexto_', 'caixasDeTreino_', 'treinoDoCaminho_'];
const categorias = /var TRILHAS_COM_CATEGORIA_ = [^\n]+/.exec(codigo)[0];
const js = {};
vm.createContext(js);
vm.runInContext(FUNCOES.map(corpo).join('\n') + '\n' + categorias + '\nglobalThis.CATEGORIAS=TRILHAS_COM_CATEGORIA_;', js);

const letras = c => { let s = ''; for (; c; c = Math.floor((c - 1) / 26)) s = String.fromCharCode(65 + (c - 1) % 26) + s; return s; };
const coluna = t => [...t].reduce((n, x) => n * 26 + x.charCodeAt(0) - 64, 0);
const exige = (cond, o) => { if (!cond) throw Error(o); };
const aba = n => { const a = ctx.ABAS.find(x => x.nome === n); exige(a, 'Aba ausente: ' + n); return a; };
const indices = {};
const valor = (n, a1) => {
  const m = /^([A-Z]+)(\d+)$/.exec(a1);
  const i = indices[n] || (indices[n] = new Map(aba(n).vals.map(t => [t[0] + ',' + t[1], t[2]])));
  const v = i.get(+m[2] + ',' + coluna(m[1]));
  return v === undefined ? '' : v;
};
const endereco = f => {
  const m = /ROW\((?:'[^']+'|[A-Z_]+)!\$?([A-Z]+)\$?(\d+)\)/.exec(f);
  exige(m, 'Endereço não reconhecido: ' + f);
  return m[1] + m[2];
};
// A grade da DADOS com os endereços resolvidos, como o script a lê.
const dados = Array.from({ length: aba('DADOS').rows }, () => Array(aba('DADOS').cols).fill(''));
for (const [r, c, v] of aba('DADOS').vals)
  dados[r - 1][c - 1] = typeof v === 'string' && v.startsWith('=') ? (v.startsWith('=ADDRESS(') && /ROW\(/.test(v) ? endereco(v) : '') : v;
const indice = {};
for (let r = 1; r <= aba('DADOS').rows; r++) {
  const k = valor('DADOS', 'BA' + r), v = valor('DADOS', 'BB' + r);
  if (k && typeof v === 'string' && v.startsWith('=ADDRESS(')) indice[k] = endereco(v);
}

// ---------- células de entrada, com o rótulo que confirma o lugar e o valor de fábrica
const campo = (chave, a, celula, rotulo, texto) => {
  exige(valor(a, rotulo) === texto, `Rótulo mudou em ${a}!${rotulo}: ${valor(a, rotulo)}`);
  const fabrica = valor(a, celula);
  exige(!(typeof fabrica === 'string' && fabrica.startsWith('=')), `${a}!${celula} virou fórmula`);
  return { chave, aba: a, celula, rotulo, texto_rotulo: texto, fabrica };
};
const P = 'FICHA PESSOAL';
const identidade = [
  campo('nome', 'CARTEIRA', 'O9', 'O8', 'PORTADOR'),
  campo('jogador', 'CARTEIRA', 'AK22', 'AK21', 'REGISTRADO POR'),
  campo('idade', P, 'AI11', 'AI10', 'IDADE'), campo('altura', P, 'AO11', 'AO10', 'ALTURA'),
  campo('olhos', P, 'Q15', 'Q14', 'OLHOS'), campo('cabelo', P, 'Y15', 'Y14', 'CABELO'),
  campo('pele', P, 'AG15', 'AG14', 'PELE'), campo('genero', P, 'AO15', 'AO14', 'GÊNERO'),
  campo('aparencia', P, 'Q19', 'Q18', 'APARÊNCIA'), campo('cicatrizes', P, 'AI19', 'AI18', 'CICATRIZES'),
  campo('traco', P, 'Q23', 'Q22', 'TRAÇO · UMA FRASE DA SUA HISTÓRIA'),
  campo('historia', P, 'Q27', 'Q26', 'HISTÓRIA'), campo('personalidade', P, 'D31', 'D30', 'PERSONALIDADE'),
  campo('lacos', P, 'Q35', 'Q34', 'LAÇOS E ANOTAÇÕES')];
const atributos = ['Força', 'Destreza', 'Constituição', 'Inteligência', 'Essência'].map(n => {
  const c = indice['atr_base_' + n], m = /^([A-Z]+)(\d+)$/.exec(c), rotulo = m[1] + (+m[2] + 1);
  exige(valor('FICHA', rotulo) === n, 'Atributo fora do lugar: ' + n);
  return { nome: n, celula: c, rotulo };
});
const escolhas = [
  campo('caminho', 'FICHA', indice.caminho, 'D10', 'CAMINHO'), campo('trilha', 'FICHA', indice.trilha, 'N10', 'TRILHA'),
  campo('origem', 'FICHA', indice.origem, 'X10', 'ORIGEM'), campo('marcante', P, 'D44', 'D43', 'MARCANTE'),
  campo('menor1', P, 'R44', 'R43', 'MENOR 1'), campo('menor2', P, 'AH44', 'AH43', 'MENOR 2')];
exige(valor('FICHA', indice['trocou por arma']) === 'Não trocou', 'Troca por arma mudou');

// ---------- perícias, ofícios e testes: nome e caixa de treino
const marcas = (l1, l2, nomeCol, caixaCol) => {
  const out = [];
  for (let r = l1; r <= l2; r++) {
    const nome = String(valor('FICHA', nomeCol + r)).trim();
    if (!nome) continue;
    exige(valor('FICHA', caixaCol + r) === false, `Caixa ausente: FICHA!${caixaCol}${r}`);
    out.push({ nome, caixa: caixaCol + r, rotulo: nomeCol + r });
  }
  return out;
};
const pericias = [...marcas(80, 90, 'F', 'D'), ...marcas(79, 90, 'V', 'T')];
const oficios = [...marcas(108, 113, 'F', 'D'), ...marcas(108, 112, 'S', 'Q')];
const testes = marcas(108, 111, 'AG', 'AF');
exige(pericias.length === 23 && oficios.length === 11 && testes.length === 4, 'Contagem de treinos mudou');

// ---------- cartas da seção 7
const cartas = [];
for (let r = 2; valor('DADOS_AM', letras(256) + r) !== ''; r++) {
  const texto = endereco(valor('DADOS_AM', letras(260) + r));
  cartas.push({ fonte: valor('DADOS_AM', letras(256) + r).split(' ')[0], nivel: Number(valor('DADOS_AM', letras(257) + r)),
    nome: endereco(valor('DADOS_AM', letras(259) + r)), texto, linha: Number(texto.replace(/^[A-Z]+/, '')) });
}
exige(cartas.length === 9, 'Cartas mudaram');
const livro = ctx.LIVRO.map(l => ({ dono: l.dono, fonte: l.fonte, nivel: l.nivel, nome: l.nome, texto: l.texto,
  negritos: js.negritosDoTexto_(l.texto, l.titulos), altura: js.alturaDaCaixa_(l.texto, ctx.MEDIDA) }));

// ---------- caixas que esticam com o texto (dossiê e capacidades da Origem)
const estica = (gatilho, n) => {
  const g = aba(P).esticam.find(x => x.gatilhos.some(a => a.split(':')[0] === gatilho));
  exige(g && g.aba === P && g.textos.length === n && g.minima === undefined, 'Caixas que esticam mudaram: ' + gatilho);
  return g.textos.map(x => ({ largura: x[0], celulas: x[1], linha: x[2], linhas: x[3], folga: x[4] || 0 }));
};
const esticam = { identidade: estica('D31', 6), capacidades: estica('D44', 3) };
const metrica = { larguras: ctx.MEDIDA.larguras, media: ctx.MEDIDA.media, linha: ctx.MEDIDA.linha,
  respiro: ctx.MEDIDA.respiro, minima: ctx.MEDIDA.minima };

// ---------- treino em armas, pelas funções do script
const t = js.caixasDeTreino_(dados);
const todas = js.tabelaDaDados_(dados, 'Caminho que treina todas as armas').map(l => String(l['Caminho que treina todas as armas']));
const nomes = js.tabelaDaDados_(dados, 'Caminho').map(l => String(l['Caminho']));
const tabela = [];
for (let r = 2; r <= 7; r++) tabela.push({ caminho: valor('DADOS_PROGRESSAO', 'M' + r),
  pericias: [valor('DADOS_PROGRESSAO', 'R' + r), valor('DADOS_PROGRESSAO', 'S' + r)] });
exige(JSON.stringify(tabela.map(l => l.caminho)) === JSON.stringify(nomes), 'Caminhos divergem');
const trilhas = [];
for (let r = 2; r <= 21; r++) trilhas.push({ trilha: valor('DADOS_PROGRESSAO', 'AA' + r), caminho: valor('DADOS_PROGRESSAO', 'AB' + r) });
const caixas = [...t.armas, ...t.grupos].map(x => ({ caixa: x.caixa, categoria: x.categoria }));

const commit = execFileSync('git', ['-C', raiz, 'rev-parse', 'HEAD']).toString().trim();
const mapa = { protocolo: 1, ficha: commit, identidade, atributos, escolhas,
  troca_arma: { celula: indice['trocou por arma'], fabrica: 'Não trocou' }, categoria_trilha: indice['grupo de arma da trilha'],
  trilhas_categoria: js.CATEGORIAS, tr_fisico: 'AK108', pericias, oficios, testes, treino: { caixas, conjurador: t.conjurador },
  cartas, linhas_da_carta: ctx.MEDIDA.caixa, altura_vazia: js.alturaDaCaixa_('', ctx.MEDIDA), livro, esticam, metrica,
  leituras: { nivel: indice.nivel, pontos: indice['pontos disponíveis'], pericias: indice['perícias disponíveis'],
    oficios: indice['ofícios disponíveis'], testes: indice['testes disponíveis'], escolhas: indice['escolhas de perícia'] } };
fs.writeFileSync(path.join(aqui, 'src/carteira_viva/criacao_mapa.json'), JSON.stringify(mapa, null, 1) + '\n');

// ---------- o que o script original faz em cada transição, para o teste comparar
const vazias = cartas.map(() => ({ nome: '', texto: '' })), semAutos = cartas.map(() => ['', '']);
const curto = s => crypto.createHash('sha256').update(s).digest('hex').slice(0, 16);
const passo = (caminho, trilha, antes, trilhaAntes, atuais, anteriores) => {
  const fica = js.trilhaQueFica_(trilhas, caminho, trilha, 'Escolha sua Trilha');
  const p = js.periciasDoCaminho_(tabela, caminho, antes);
  const c = js.cartasDaFicha_(ctx.LIVRO, cartas, caminho, fica, atuais, anteriores);
  const tr = js.treinoDoCaminho_(t.armas, t.grupos, caminho, nomes, todas, t.conjurador);
  return { caminho, trilha, antes, trilhaAntes, fica, marcar: p.marcar, desmarcar: p.desmarcar, bruto: c,
    treino: Object.keys(tr).filter(k => tr[k]).sort() };
};
const casos = [], vazio = ['Escolha seu Caminho', 'Escolha sua Trilha'];
for (const c of nomes) {
  casos.push(passo(c, vazio[1], ...vazio, vazias, semAutos));
  for (const x of trilhas.filter(x => x.caminho === c)) casos.push(passo(c, x.trilha, ...vazio, vazias, semAutos));
}
// Troca de Caminho com uma carta editada pelo jogador: a edição fica.
for (const [de, x] of [['Vanguarda', 'Estocada'], ['Incursor', 'Pugilista'], ['Evocador', 'Parceria']]) {
  const a = casos.find(k => k.caminho === de && k.trilha === x);
  const atuais = a.bruto.map(k => ({ nome: k.nome, texto: k.texto }));
  atuais[0].texto += '\n\nAnotação da mesa';
  for (const para of nomes) casos.push(passo(para, x, de, x, atuais, a.bruto.map(k => [k.automatico, k.livro])));
}
const esperado = casos.map(({ bruto, ...k }) => ({ ...k, cartas: bruto.map(n => ({ nome: n.nome, texto: curto(n.texto),
  nota: n.nota && curto(n.nota), automatico: n.automatico, livro: curto(n.livro),
  negritos: n.texto !== '' && n.texto === n.livro ? js.negritosDoTexto_(n.texto, n.titulos) : [],
  altura: js.alturaDaCaixa_(n.texto, ctx.MEDIDA) })) }));
const amostras = ['', 'curto', 'a b c d e f g h '.repeat(60), 'Uma história longa, com acento e “aspas”. '.repeat(40), 'linha 1\n\nlinha 3\n' + 'x'.repeat(300), '呪術 🗡 '.repeat(90)];
const alturas = [];
for (const [nome, grupo] of Object.entries(esticam)) for (let k = 0; k < amostras.length; k++) {
  const textos = grupo.map((_, i) => amostras[(i + k) % amostras.length]);
  alturas.push({ grupo: nome, amostra: k, alturas: js.alturasQueEsticam_(
    grupo.map(g => [g.largura, g.celulas, g.linha, g.linhas, g.folga]), textos, ctx.MEDIDA, undefined, null) });
}
const linhas = [];
for (const texto of amostras) linhas.push([texto, Array.from({ length: 63 }, (_, k) =>
  js.linhasDoTexto_(texto, { ...metrica, largura: 60 + 7 * k }))]);
fs.writeFileSync(path.join(aqui, 'src/testes/dados_criacao_esperado.json'), JSON.stringify({ casos: esperado, alturas, linhas }) + '\n');
console.log(JSON.stringify({ ficha: commit.slice(0, 8), identidade: identidade.length, caixas: caixas.length, livro: livro.length, casos: casos.length }));
