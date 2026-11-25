(() => {
  'use strict';
  const $ = id => document.getElementById(id), partes = location.pathname.split('/').filter(Boolean);
  const gid = partes[1], pid = partes[2], valido = /^\d{1,22}$/.test(gid || '') && /^[a-f0-9]{32}$/.test(pid || '');
  const prefixo = '/api/carteira/' + gid, query = new URLSearchParams(location.search);
  const PASSOS = ['identidade', 'atributos', 'origem', 'caminho', 'treinos', 'revisao'];
  let s = null, dono = null, st = null, passo = 0, ocupado = false, relogio, pendente = null, venceu = false;
  let lang = query.get('idioma') === 'en' ? 'en' : 'pt-BR', escolhido = query.has('idioma');
  // O que foi digitado e ainda não foi salvo, por passo. Só na memória desta página.
  let rascunho = {};
  const palavras = {
    titulo: ['Preencher ficha', 'Fill in the sheet'], subtitulo: ['Cada passo que você salva vai direto pra sua planilha.', 'Each step you save goes straight to your spreadsheet.'],
    idioma: ['Idioma da página', 'Page language'], sair: ['Encerrar sessão', 'Sign out'], demo: ['Demonstração local · contas e fichas fictícias.', 'Local demo · fictional accounts and sheets.'],
    pular: ['Ir para o conteúdo', 'Skip to content'], passos: ['Passos', 'Steps'],
    entrartitulo: ['Entre para preencher sua ficha', 'Sign in to fill in your sheet'], entrartexto: ['Use a conta Discord que cadastrou o personagem. Só quem cadastrou pode preencher.', 'Use the Discord account that registered the character. Only that account can fill it in.'], entrar: ['Entrar com Discord', 'Sign in with Discord'],
    conectado: ['Conectado como ', 'Signed in as '], jogador: ['Jogador', 'Player'], voltar: ['Voltar', 'Back'], proximo: ['Próximo passo', 'Next step'], salvar: ['Salvar na ficha', 'Save to the sheet'],
    carteira: ['Voltar pra Carteira', 'Back to the Wallet'], planilha: ['Abrir planilha', 'Open spreadsheet'], rodape: ['O bot só escreve o que você salvar aqui. Preencher não aprova a ficha: a decisão continua com o mestre.', 'The bot only writes what you save here. Filling in does not approve the sheet: the GM decides.'],
    confirmarTitulo: ['Já tem valor na ficha', 'The sheet already has a value'], confirmarTexto: ['Nada foi trocado ainda. Confira o que vai mudar:', 'Nothing was replaced yet. Check what will change:'], confirmarCaminho: ['Trocar o Caminho também tira a Trilha e as perícias fixas do antigo, e volta a troca por arma pra “Não trocou”.', 'Replacing the Path also removes the old Trail and fixed skills, and resets the weapon trade.'], trocar: ['Trocar', 'Replace'], manter: ['Deixar como está', 'Keep as it is'], vazio: ['(vazio)', '(empty)'],
    identidade: ['Identidade', 'Identity'], atributos: ['Atributos', 'Attributes'], origem: ['Origem', 'Origin'], caminho: ['Caminho e Trilha', 'Path and Trail'], treinos: ['Treinos', 'Training'], revisao: ['Revisão', 'Review'],
    tIdentidade: ['Tudo aqui é opcional. O que você não mexer fica como está na ficha.', 'Everything here is optional. What you leave alone stays as it is in the sheet.'],
    tAtributos: ['{pontos} pontos pra dividir; na criação cada atributo vai de 0 a {teto}.', '{pontos} points to spend; at creation each attribute goes from 0 to {teto}.'],
    tOrigem: ['As opções são as do menu da sua ficha. Salve a Origem primeiro: a marcante e as menores dependem dela.', 'The options come from your sheet. Save the Origin first: the other choices depend on it.'],
    tCaminho: ['Salvar aqui também marca as perícias fixas, os treinos de arma e preenche as cartas. Pode levar uns 30 segundos.', 'Saving here also marks the fixed skills and weapon training and fills in the cards. It may take about 30 seconds.'],
    tTreinos: ['Até {com} perícias com {oficios} ofícios, ou {sem} perícias sem ofício, contando as fixas do Caminho. E 2 Testes de Resistência.', 'Up to {com} skills with {oficios} crafts, or {sem} skills without crafts, including the Path’s fixed skills. And 2 Resistance Tests.'],
    tRevisao: ['O que a própria ficha diz agora:', 'What the sheet itself says now:'],
    passou: ['Essa ficha já passou do nível inicial. O que muda ao subir de nível se preenche na planilha.', 'This sheet is past the starting level. Level-up changes are made in the spreadsheet.'],
    configuracao: ['A CONFIGURAÇÃO da ficha tem um número inválido. Confira as regras de campanha na planilha.', 'The sheet’s CONFIGURAÇÃO has an invalid number. Check the campaign rules in the spreadsheet.'],
    semCaminho: ['Escolha o Caminho antes dos treinos.', 'Choose the Path before training.'], proprio: ['Sua ficha usa um Caminho ou Trilha próprio da mesa. Ele se escolhe na planilha.', 'Your sheet uses a table-specific Path or Trail. Choose it in the spreadsheet.'],
    usados: ['Usados: ', 'Used: '], de: [' de ', ' of '], salveOrigem: ['Salve a Origem pra ver as capacidades dela.', 'Save the Origin to see its abilities.'],
    marcante: ['Marcante', 'Signature'], menor1: ['Menor 1', 'Minor 1'], menor2: ['Menor 2', 'Minor 2'], nenhuma: ['Escolha…', 'Choose…'], aMao: ['Tem texto escrito à mão nessa caixa. Pra trocar por uma do livro, use o menu na planilha.', 'This box has hand-written text. To switch to a book ability, use the menu in the spreadsheet.'],
    campoCaminho: ['Caminho', 'Path'], campoTrilha: ['Trilha', 'Trail'], semTrilha: ['Ainda sem Trilha', 'No Trail yet'],
    pericias: ['Perícias', 'Skills'], oficios: ['Ofícios', 'Crafts'], testes: ['Testes de Resistência', 'Resistance Tests'], fixa: ['do Caminho', 'from the Path'], trFisico: ['Físico usa', 'Physical uses'], troca: ['Trocou perícia por arma?', 'Traded skills for weapons?'], trocas: [['Não trocou', '1 arma (−2 perícias)', '2 armas (−4 perícias)'], ['No', '1 weapon (−2 skills)', '2 weapons (−4 skills)']],
    nivel: ['Nível', 'Level'], pontos: ['Pontos de atributo', 'Attribute points'], escolhas: ['Aviso das perícias', 'Skill notice'],
    exportar: ['Falta um toque seu: na CARTEIRA, marque a caixa ao lado de “Bot:” até ela dizer “em dia”. Só aí o bot lê a ficha nova.', 'One last tap: in CARTEIRA, tick the box next to “Bot:” until it says “em dia”. Only then does the bot read the new sheet.'], emDia: ['A exportação pro bot está em dia.', 'The export for the bot is up to date.'], emitir: ['Técnica, feitiços e inventário ainda são na planilha. EMITIR fica pro fim, com o mestre.', 'Technique, spells and inventory are still done in the spreadsheet. EMITIR comes last, with the GM.'],
    carregando: ['Lendo a ficha…', 'Reading the sheet…'], salvando: ['Salvando na ficha…', 'Saving to the sheet…'], salvo: ['Salvo na ficha.', 'Saved to the sheet.'], igual: ['A ficha já estava assim.', 'The sheet already had this.'], nada: ['Você não mudou nada neste passo.', 'You changed nothing in this step.'],
    sessao: ['Sua sessão terminou. Entre de novo em outra aba e volte aqui: o que você digitou continua nesta página.', 'Your session ended. Sign in again in another tab and come back: what you typed is still here.'],
    outraConta: ['Você entrou com outra conta. Recarregue a página.', 'You signed in with another account. Reload the page.'],
    acesso: ['Só quem cadastrou o personagem pode preencher, e o preenchimento precisa estar liberado pra sua conta.', 'Only the account that registered the character can fill it in, and filling in must be enabled for it.'],
    mudou: ['A ficha mudou enquanto você preenchia. Atualizei a página: confira e salve de novo.', 'The sheet changed while you were filling it in. The page was refreshed: check and save again.'],
    formato: ['Essa ficha é de outra versão, ou tem células fora do lugar. Nada foi escrito. Por enquanto o preenchimento só vale pra ficha oficial atual do Ciclo Maldito.', 'This sheet is from another version, or has cells out of place. Nothing was written. For now this only works with the current official Ciclo Maldito sheet.'],
    oficial: ['Essa é a ficha oficial. Use a sua cópia.', 'This is the official sheet. Use your own copy.'],
    arquivo: ['Não achei a planilha na sua conta Google. Confira se ela não está na lixeira; se precisar, use /personagem reconectar.', 'Could not find the spreadsheet in your Google account. Check the bin; if needed, use /character reconnect.'],
    revogada: ['A autorização do Google foi retirada. Use /personagem reconectar no Discord.', 'The Google authorization was removed. Use /character reconnect in Discord.'],
    escrita_incerta: ['O Google não confirmou a gravação. Recarregue a página em um minuto e confira antes de salvar de novo.', 'Google did not confirm the save. Reload in a minute and check before saving again.'],
    escrita_recusada: ['O Google recusou a gravação. Nada foi salvo neste passo.', 'Google refused the save. Nothing was saved in this step.'],
    conflito: ['A ficha ou a autorização mudou. Recarregue a página.', 'The sheet or the authorization changed. Reload the page.'],
    ocupado: ['Há pedidos demais em andamento. Tente de novo em instantes.', 'Too many requests in progress. Try again shortly.'], temporario: ['Não consegui falar com o serviço agora. Tente de novo em instantes.', 'Could not reach the service right now. Try again shortly.'],
    conexao: ['Não foi possível confirmar o login. Tente de novo.', 'Could not confirm sign-in. Try again.'], instrucao: ['Abra esta página pelo cartão do personagem na Carteira.', 'Open this page from the character card in the Wallet.']
  };
  const t = (k, v = {}) => (palavras[k] || palavras.temporario)[lang === 'en' ? 1 : 0].replace(/\{(\w+)\}/g, (_, n) => v[n]);
  const el = (tag, cls, texto) => { const e = document.createElement(tag); if (cls) e.className = cls; if (texto !== undefined) e.textContent = texto; return e; };

  class Falha extends Error { constructor(codigo, corpo) { super(codigo); this.corpo = corpo || {}; } }
  async function api(caminho, corpo) {
    let r, v;
    try {
      r = await fetch(caminho, { method: corpo === undefined ? 'GET' : 'POST', credentials: 'same-origin', cache: 'no-store',
        headers: corpo === undefined ? {} : { 'Content-Type': 'application/json', 'X-CSRF-Token': s?.csrf || '' }, body: corpo === undefined ? undefined : JSON.stringify(corpo) });
      v = await r.json();
    } catch { throw new Falha('temporario'); }
    if (!r.ok) throw new Falha(v.erro || 'temporario', v);
    const segundos = Number(r.headers.get('X-Carteira-Expira-Em'));
    if (segundos > 0) { clearTimeout(relogio); relogio = setTimeout(() => falhou(new Falha('sessao')), segundos * 1000); }
    return v;
  }
  function falhou(e) {
    let codigo = e.message;
    if (codigo === 'limite') codigo = 'ocupado';
    if (codigo === 'reconectar') codigo = 'revogada';
    if (codigo === 'sessao') { venceu = true; $('area').hidden = true; $('login').hidden = !!dono; }
    $('erro').textContent = e.corpo?.motivos ? e.corpo.motivos.join(' ') : t(palavras[codigo] ? codigo : 'temporario');
    $('erro').hidden = false; $('erro').focus();
  }
  async function acao(fn, texto = 'carregando') {
    if (ocupado) return;
    ocupado = true; $('erro').hidden = true; $('andamento').textContent = t(texto); travar();
    try { if (venceu) await sessao(); await fn(); } catch (e) { falhou(e instanceof Falha ? e : new Falha('temporario')); }
    finally { ocupado = false; $('andamento').textContent = ''; travar(); }
  }
  function travar() {
    document.querySelectorAll('button:not(#sair)').forEach(b => { b.disabled = ocupado || b.dataset.fixo === '1'; });
    $('idioma').disabled = ocupado; $('voltar').hidden = passo === 0; $('pular').hidden = passo === PASSOS.length - 1;
  }
  async function sessao() {
    const nova = await api(prefixo + '/sessao');
    if (nova.autenticado && dono && nova.usuario !== dono) throw new Falha('outraConta');
    s = nova; if (!escolhido) lang = s.idioma || 'pt-BR';
    if (s.autenticado) { dono = s.usuario; venceu = false; }
    else if (dono) throw new Falha('sessao');
    $('demo').hidden = !s.demonstracao; $('login').hidden = s.autenticado; $('area').hidden = !s.autenticado || !st; $('sair').hidden = !s.autenticado;
    traduzir(); return s.autenticado;
  }
  function traduzir() {
    document.documentElement.lang = lang; document.title = t('titulo') + ' · Guias do Ciclo'; $('idioma').value = lang;
    document.querySelectorAll('[data-t]').forEach(e => { e.textContent = t(e.dataset.t); });
    document.querySelectorAll('[data-label]').forEach(e => e.setAttribute('aria-label', t(e.dataset.label)));
    $('identidade').textContent = s?.autenticado ? t('conectado') + (s.nome || t('jogador')) : '';
    if (valido) $('carteira').href = '/carteira/' + gid + '/' + pid + '?idioma=' + lang;
  }

  // ---------- formulários. Cada um lê `st` (o que está na ficha) e `rascunho` (o que foi mexido).
  const campo = (id, rotulo, controle, dica) => { const d = el('div', 'campo-form'), l = el('label', null, rotulo); l.htmlFor = id; controle.id = id; d.append(l, controle); if (dica) d.append(el('p', 'muted', dica)); return d; };
  const anota = (p, chave, valor, original) => { const r = rascunho[p] = rascunho[p] || {}; if (valor === original) delete r[chave]; else r[chave] = valor; };
  const atual = (p, chave, original) => rascunho[p] && chave in rascunho[p] ? rascunho[p][chave] : original;
  function seletor(opcoes, valor, aoMudar) {
    const c = el('select');
    for (const [v, texto] of opcoes) { const o = el('option', null, texto); o.value = v; c.append(o); }
    if (!opcoes.some(([v]) => v === valor)) { const o = el('option', null, valor); o.value = valor; c.prepend(o); }
    c.value = valor; c.onchange = () => aoMudar(c.value); return c;
  }
  const botaoSalvar = p => { const b = el('button', null, t('salvar')); b.type = 'button'; b.onclick = () => salvar(p); return b; };
  const formularios = {
    identidade(f) {
      $('passo-texto').textContent = t('tIdentidade');
      const grade = el('div', 'campos-curtos');
      for (const c of st.identidade) {
        const e = el(c.curto ? 'input' : 'textarea'); e.maxLength = c.curto ? 100 : 4000; if (!c.curto) e.rows = 3; e.autocomplete = 'off';
        e.value = atual('identidade', c.chave, c.valor); e.oninput = () => anota('identidade', c.chave, e.value, c.valor);
        (c.curto ? grade : f).append(campo('f-' + c.chave, c.rotulo, e));
      }
      f.prepend(grade); f.append(botaoSalvar('identidade'));
    },
    atributos(f) {
      if (bloqueado(f)) return;
      const lim = st.limites; $('passo-texto').textContent = t('tAtributos', { pontos: lim.pontos, teto: lim.teto_criacao });
      const grade = el('div', 'campos-curtos'), conta = el('p', 'contador'); conta.setAttribute('aria-live', 'polite');
      const soma = () => { conta.textContent = t('usados') + st.atributos.reduce((n, a) => n + (Number(atual('atributos', a.nome, a.valor)) || 0), 0) + t('de') + lim.pontos; };
      for (const a of st.atributos) {
        const e = el('input'); e.type = 'number'; e.min = 0; e.max = lim.teto_criacao; e.step = 1; e.inputMode = 'numeric'; e.value = atual('atributos', a.nome, a.valor === '' ? 0 : a.valor);
        e.oninput = () => { anota('atributos', a.nome, e.value === '' ? '' : Number(e.value), a.valor); soma(); };
        grade.append(campo('f-' + a.nome, a.nome, e));
      }
      soma(); f.append(grade, conta, botaoSalvar('atributos'));
    },
    origem(f) {
      $('passo-texto').textContent = t('tOrigem');
      const og = st.escolhas.origem, nova = atual('origem', 'origem', og);
      f.append(campo('f-origem', t('origem'), seletor(st.menus.origem.map(x => [x, x]), nova, v => { anota('origem', 'origem', v, og); desenhar(); })), botaoSalvar('origem'));
      if (nova !== og) { f.append(el('p', 'muted', t('salveOrigem'))); return; }
      for (const k of ['marcante', 'menor1', 'menor2']) {
        const v = st.escolhas[k], menu = st.menus[k === 'marcante' ? 'marcante' : 'menor'];
        f.append(campo('f-' + k, t(k), seletor([['', t('nenhuma')], ...menu.map(x => [x, x])], atual('capacidades', k, v), x => anota('capacidades', k, x, v)), st.a_mao.includes(k) ? t('aMao') : st.textos[k]));
      }
      f.append(botaoSalvar('capacidades'));
    },
    caminho(f) {
      $('passo-texto').textContent = t('tCaminho');
      const c0 = st.escolhas.caminho, t0 = st.escolhas.trilha, vazio = st.fabrica.caminho, semTrilha = st.fabrica.trilha;
      const c = atual('caminho', 'caminho', c0), trilhas = st.menus.trilhas[c] || [];
      if (c0 !== vazio && !st.menus.caminho.includes(c0)) f.append(el('p', 'aviso', t('proprio')));
      f.append(campo('f-caminho', t('campoCaminho'), seletor([...(c0 === vazio ? [[vazio, t('nenhuma')]] : []), ...st.menus.caminho.map(x => [x, x])], c, v => { anota('caminho', 'caminho', v, c0); delete rascunho.caminho?.trilha; desenhar(); })));
      const base = trilhas.includes(t0) ? t0 : semTrilha;
      f.append(campo('f-trilha', t('campoTrilha'), seletor([[semTrilha, t('semTrilha')], ...trilhas.map(x => [x, x])], atual('caminho', 'trilha', base), v => anota('caminho', 'trilha', v, base))), botaoSalvar('caminho'));
    },
    treinos(f) {
      if (bloqueado(f)) return;
      const d = st.treinos, lim = st.limites;
      $('passo-texto').textContent = t('tTreinos', { com: lim.pericias_com_oficio, sem: lim.pericias_sem_oficio, oficios: lim.oficios });
      if (!d.fixas.length) { f.append(el('p', 'aviso', t('semCaminho'))); return; }
      for (const g of ['pericias', 'oficios', 'testes']) {
        const set = el('fieldset'), leg = el('legend', null, t(g)), grade = el('div', 'caixas'), conta = el('p', 'contador');
        const marcadas = new Set(atual('treinos', g, d[g].filter(x => x.marcada).map(x => x.nome))); if (g === 'pericias') d.fixas.forEach(x => marcadas.add(x));
        const contar = () => { conta.textContent = t('usados') + marcadas.size; };
        for (const x of d[g]) {
          const l = el('label', 'checkbox'), i = el('input'), fixa = g === 'pericias' && d.fixas.includes(x.nome);
          i.type = 'checkbox'; i.checked = marcadas.has(x.nome); i.disabled = fixa;
          i.onchange = () => { i.checked ? marcadas.add(x.nome) : marcadas.delete(x.nome); (rascunho.treinos = rascunho.treinos || {})[g] = [...marcadas]; contar(); };
          l.append(i, el('span', null, x.nome + (fixa ? ' · ' + t('fixa') : ''))); grade.append(l);
        }
        contar(); set.append(leg, grade, conta); f.append(set);
      }
      f.append(campo('f-tr', t('trFisico'), seletor([['FORÇA', 'FORÇA'], ['DESTREZA', 'DESTREZA']], atual('treinos', 'tr_fisico', d.tr_fisico), v => anota('treinos', 'tr_fisico', v, d.tr_fisico))));
      if (d.pode_trocar) f.append(campo('f-troca', t('troca'), seletor(palavras.trocas[lang === 'en' ? 1 : 0].map((x, n) => [String(n), x]), String(atual('treinos', 'troca', d.troca)), v => anota('treinos', 'troca', Number(v), d.troca))));
      f.append(botaoSalvar('treinos'));
    },
    revisao(f) {
      $('passo-texto').textContent = t('tRevisao');
      const dl = el('dl');
      const linha = (k, v) => { if (v !== '') dl.append(el('dt', null, k), el('dd', null, v)); };
      linha(t('nivel'), st.leituras.nivel); linha(t('campoCaminho'), st.escolhas.caminho); linha(t('campoTrilha'), st.escolhas.trilha); linha(t('origem'), st.escolhas.origem);
      for (const k of ['pontos', 'pericias', 'oficios', 'testes', 'escolhas']) linha(t(k), st.leituras[k]);
      f.append(dl, el('p', 'aviso', t(st.exportacao === 'em_dia' ? 'emDia' : 'exportar')), el('p', 'muted', t('emitir')));
      const a = el('a', null, t('planilha')); a.href = st.arquivo; a.target = '_blank'; a.rel = 'noreferrer noopener'; f.append(a);
    }
  };
  function bloqueado(f) {
    if (st.limites && st.criacao) return false;
    $('passo-texto').textContent = ''; f.append(el('p', 'aviso', t(st.limites ? 'passou' : 'configuracao'))); return true;
  }
  function desenhar() {
    $('passos').replaceChildren(...PASSOS.map((p, n) => { const li = el('li'), b = el('button', 'secundario', (n + 1) + '. ' + t(p)); b.type = 'button'; if (n === passo) b.setAttribute('aria-current', 'step'); b.onclick = () => ir(n); li.append(b); return li; }));
    $('passo-titulo').textContent = t(PASSOS[passo]); $('confirmar').hidden = true; pendente = null;
    const f = $('formulario'); f.replaceChildren(); formularios[PASSOS[passo]](f);
    const u = new URL(st.arquivo); if (u.protocol === 'https:' && u.hostname === 'docs.google.com') { $('planilha').href = u.href; $('planilha').hidden = false; }
    $('area').hidden = false; travar();
  }
  function ir(n) { if (ocupado) return; passo = n; $('resultado').hidden = true; $('erro').hidden = true; desenhar(); $('passo-titulo').focus(); }

  // ---------- salvar
  function dadosDe(p) {
    const r = rascunho[p] || {};
    if (p === 'identidade' || p === 'capacidades') return r;
    if (p === 'atributos') return Object.keys(r).length ? Object.fromEntries(st.atributos.map(a => [a.nome, atual(p, a.nome, a.valor === '' ? 0 : a.valor)])) : {};
    if (p === 'origem') return r;
    if (p === 'caminho') return Object.keys(r).length ? { caminho: atual(p, 'caminho', st.escolhas.caminho), ...(r.trilha !== undefined ? { trilha: r.trilha } : {}) } : {};
    const d = st.treinos, lista = g => atual(p, g, d[g].filter(x => x.marcada).map(x => x.nome));
    return Object.keys(r).length ? { pericias: lista('pericias'), oficios: lista('oficios'), testes: lista('testes'), tr_fisico: atual(p, 'tr_fisico', d.tr_fisico), troca: atual(p, 'troca', d.troca) } : {};
  }
  function valorAtual(p, k) {
    if (p === 'identidade') return st.identidade.find(c => c.chave === k).valor;
    if (p === 'atributos') return String(st.atributos.find(a => a.nome === k).valor);
    if (p === 'treinos') return k === 'tr_fisico' ? st.treinos.tr_fisico : k === 'troca' ? palavras.trocas[lang === 'en' ? 1 : 0][st.treinos.troca] : st.treinos[k].filter(x => x.marcada).map(x => x.nome).join(', ');
    return st.escolhas[k];
  }
  function valorNovo(p, dados, k) {
    const v = dados[k];
    if (p === 'treinos' && k === 'troca') return palavras.trocas[lang === 'en' ? 1 : 0][v];
    if (p === 'treinos' && k === 'pericias') return [...new Set([...st.treinos.fixas, ...v])].join(', ');
    return Array.isArray(v) ? v.join(', ') : String(v ?? st.fabrica.trilha);
  }
  const rotulo = (p, k) => p === 'identidade' ? st.identidade.find(c => c.chave === k).rotulo : p === 'atributos' ? k : t({ caminho: 'campoCaminho', trilha: 'campoTrilha', tr_fisico: 'trFisico' }[k] || k);
  const INTEIROS = ['atributos', 'treinos'];      // o passo é uma escolha só: troca tudo ou nada
  function perguntar(p, dados, campos) {
    pendente = { p, dados, campos };
    $('confirmar-lista').replaceChildren(...campos.map(k => {
      const l = el('label', 'checkbox'), i = el('input'); i.type = 'checkbox'; i.checked = true; i.value = k; i.disabled = INTEIROS.includes(p);
      const corpo = el('span'); corpo.append(el('strong', null, rotulo(p, k) + ': '), document.createTextNode((valorAtual(p, k) || t('vazio')) + ' → ' + (valorNovo(p, dados, k) || t('vazio'))));
      l.append(i, corpo); return l;
    }));
    if (p === 'caminho' && campos.includes('caminho')) $('confirmar-lista').append(el('p', null, t('confirmarCaminho')));
    $('confirmar').hidden = false; $('confirmar-titulo').focus();
  }
  function salvar(p, dados = dadosDe(p), confirmados = []) {
    $('resultado').hidden = true;
    if (!Object.keys(dados).length) { mostrar([t('nada')]); return; }
    $('confirmar').hidden = true;
    acao(async () => {
      let r;
      try { r = await api(prefixo + '/personagens/' + pid + '/preencher/' + p, { dados, base: st.bases[p], confirmados }); }
      catch (e) {
        if (e.message === 'preenchido') { perguntar(p, dados, e.corpo.campos); return; }
        if (e.message === 'mudou') { st = e.corpo.estado; desenhar(); }
        throw e;
      }
      st = r; delete rascunho[p]; desenhar(); mostrar([t(r.gravou ? 'salvo' : 'igual'), ...r.avisos]);
    }, 'salvando');
  }
  function mostrar(textos) { $('resultado').replaceChildren(...textos.map(x => el('p', null, x))); $('resultado').hidden = false; }
  $('trocar').onclick = () => {
    const { p, dados, campos } = pendente, marcados = [...$('confirmar-lista').querySelectorAll('input:checked')].map(i => i.value);
    if (INTEIROS.includes(p)) { salvar(p, dados, p === 'atributos' ? ['atributos'] : campos); return; }
    const resto = { ...dados }; for (const k of campos) if (!marcados.includes(k)) delete resto[k];
    if (p === 'caminho' && !resto.caminho) { $('manter').onclick(); return; }
    salvar(p, resto, marcados);
  };
  $('manter').onclick = () => { $('confirmar').hidden = true; pendente = null; };
  $('formulario').onsubmit = e => e.preventDefault();
  $('voltar').onclick = () => ir(passo - 1); $('pular').onclick = () => ir(passo + 1);
  $('entrar').onclick = () => acao(async () => {
    if (!s || s.autenticado) { location.reload(); return; }
    const d = await api(prefixo + '/entrar', { idioma: lang, personagem: pid, preencher: true }), u = new URL(d.url);
    if ((u.protocol === 'https:' && u.hostname === 'discord.com') || (s.demonstracao && u.origin === location.origin)) location.assign(u.href); else throw new Falha('acesso');
  });
  $('sair').onclick = async () => {
    const csrf = s?.csrf; clearTimeout(relogio); s = st = null; rascunho = {}; $('area').hidden = true; $('sair').hidden = true; $('planilha').hidden = true; $('formulario').replaceChildren(); $('resultado').hidden = true; dono = null;
    try { await fetch('/api/carteira/sair', { method: 'POST', credentials: 'same-origin', cache: 'no-store', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf || '' }, body: '{}' }); } finally { location.reload(); }
  };
  $('idioma').onchange = () => { escolhido = true; lang = $('idioma').value; history.replaceState(null, '', location.pathname + '?idioma=' + lang); traduzir(); if (st) desenhar(); };
  window.addEventListener('beforeunload', e => { if (Object.values(rascunho).some(r => Object.keys(r).length)) e.preventDefault(); });
  window.addEventListener('pageshow', e => { if (e.persisted) location.reload(); });
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && venceu) acao(async () => { await sessao(); if (st) desenhar(); }); });
  async function comecar() {
    if (!valido) { $('login').hidden = false; $('entrar').hidden = true; $('login').querySelector('p').textContent = t('instrucao'); return; }
    if (await sessao()) { st = await api(prefixo + '/personagens/' + pid + '/preencher/ler', {}); desenhar(); }
    if (query.has('erro')) throw new Falha('conexao');
  }
  traduzir(); acao(comecar);
})();
