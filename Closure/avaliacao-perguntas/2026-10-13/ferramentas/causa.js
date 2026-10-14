const fs=require("fs");const [,,pag,arq]=process.argv;
let html=fs.readFileSync(pag,"utf8");
html=html.replace(/if \(qPal\.size && \((.*)\)\) \{/, (m,c)=>`globalThis.__g={termos:termos.length>0,familia:familia.size>0,titulo:titulo.size>0,seg:!!seg,noTitulo:!!noTitulo,regra:REGRA.test(t),q:[...qPal].map(x=>x.join(':')).join(' ')};`+m);
const js=html.slice(html.lastIndexOf("<script>")+8,html.lastIndexOf("</script>"));
const el=()=>new Proxy({value:"",style:{},classList:{add(){},remove(){}}},{get:(t,k)=>k in t?t[k]:(typeof k==="string"?(()=>el()):undefined),set:(t,k,v)=>(t[k]=v,true)});
global.document={getElementById:()=>el(),createElement:()=>el(),body:el()};global.setInterval=()=>0;global.navigator={};global.window={top:1};
const api=new Function(js+";return {blocosLivro,ativar};")();
const cont={};
for(const q of JSON.parse(fs.readFileSync(arq,"utf8"))){if(q.lab!=="C")continue;globalThis.__g=null;
const ant=(q.hist||[]).map(h=>h[0]);const a=api.ativar(ant.slice(-2).join(" ")+" "+q.msg);const r=api.blocosLivro(q.msg,a.termos,ant.slice(-2));
if(r.length){const g=globalThis.__g||{};const why=Object.keys(g).filter(k=>g[k]===true);why.forEach(k=>cont[k]=(cont[k]||0)+1);console.log(q.id,why.join("+"),"|",g.q,"| termos:",a.termos.map(e=>e.comment).join(","));}}
console.log(cont);
