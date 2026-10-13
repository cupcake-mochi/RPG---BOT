// Roda depois do núcleo da página, no mesmo escopo: monta o pedido de uma mensagem.
//   pedido: { pers: "kal"|"clo", msg, nome, pronomes, turnos: [{de:"user",nome,texto} | {de:"bot",pers,texto}],
//             agora: <milissegundos, opcional>,      (a hora do pedido; sem ela vale a do relógio)
//             falas_anteriores: ["texto", ...],      (últimas falas da personagem no canal, de outras conversas; opcional)
//             estado: { bloco: "[Estado agora: ...]", lembretes: ["...", ...] } }   (o estado que o bot calculou; opcional)
// Pode ser chamado várias vezes no mesmo contexto: tudo o que troca na página é devolvido no fim.
;(() => {
  const estadoDaPagina = linhaEstado, foraDaPagina = foraDoPlantao, relogio = Date.now;
  globalThis.__montar = p => {
    __pronomes = p.pronomes || "";
    if (p.agora) Date.now = () => p.agora;
    try {
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
        linhaEstado = () => p.estado.bloco;
        foraDoPlantao = (...a) => { const f = foraDaPagina(...a); return f + (p.estado.lembretes || []).slice(0, f ? 1 : 2).map(l => "\n[" + l + "]").join(""); };
      }
      const r = montarPrompt(p.msg, p.nome || "");
      if (aviso !== null) {
        const ultimo = r.input[r.input.length - 1], so_desta = repeticoes();
        if (so_desta && ultimo.content.endsWith(so_desta)) ultimo.content = ultimo.content.slice(0, -so_desta.length);
        ultimo.content += aviso.replace("Você já usou nesta conversa:", "Você já usou nas suas últimas respostas:");
      }
      return { input: r.input, ativadas: r.ativadas, versoes: D.versoes };
    } finally {
      linhaEstado = estadoDaPagina; foraDoPlantao = foraDaPagina; Date.now = relogio; turnos = [];
    }
  };
  globalThis.__montarJSON = texto => JSON.stringify(__montar(JSON.parse(texto)));
})();
