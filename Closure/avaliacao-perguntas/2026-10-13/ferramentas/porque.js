const fs=require("fs");const [,,pag,...msgs]=process.argv;let html=fs.readFileSync(pag,"utf8");
html=html.replace(/(const nota = buscar\(qPal[^\n]*;)/,'$1 globalThis.__n=nota.slice(0,6).map(([s,b])=>s.toFixed(1)+" "+b.ancora);');
html=html.replace(/if \(qPal\.size && \((.*)\)\) \{/, (m,c)=>`globalThis.__g={termos:termos.length>0,familia:[...familia],titulo:titulo.size,seg:!!seg,perg:!!pergunta,regra:REGRA.test(semAspas),q:[...qPal].map(x=>x.join(':')).join(' '),ct:[...comTermo].map(([i,n])=>D.livro[i].ancora+':'+n).join(' ')};`+m);
const js=html.slice(html.lastIndexOf("<script>")+8,html.lastIndexOf("</script>"));
const el=()=>new Proxy({value:"",style:{},classList:{add(){},remove(){}}},{get:(t,k)=>k in t?t[k]:(typeof k==="string"?(()=>el()):undefined),set:(t,k,v)=>(t[k]=v,true)});
global.document={getElementById:()=>el(),createElement:()=>el(),body:el()};global.setInterval=()=>0;global.navigator={};global.window={top:1};
const api=new Function(js+";return {blocosLivro,ativar,TERMO,tok};")();
for(const m of msgs){const [msg,...ants]=m.split("||");globalThis.__g=null;globalThis.__n=null;const a=api.ativar(msg);const r=api.blocosLivro(msg,a.termos,ants);console.log("##",msg,"->",r.map(b=>b.ancora).join(", "));console.log("   ",JSON.stringify(globalThis.__g));if(globalThis.__n)console.log("   ",globalThis.__n.join(" | "));}
console.log("katan:",JSON.stringify([...(api.TERMO.get("katana")||api.TERMO.get(api.tok("katana")[0])||[])]));
