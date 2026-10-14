// Roda antes do núcleo da página: o pouco de navegador que ele espera encontrar.
// Usado pelos dois motores (Node, em ponte.js, e QuickJS, em site_prompt.py), pra o pedido sair igual nos dois.
var __pronomes = "";
var document = { getElementById: () => ({ value: __pronomes }) };
if (typeof console === "undefined") var console = { log() {}, warn() {}, error() {} };
