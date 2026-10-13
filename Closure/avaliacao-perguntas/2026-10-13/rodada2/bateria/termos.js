const fs=require("fs");const [,,pag,...msgs]=process.argv;
let html=fs.readFileSync(pag,"utf8");
const js=html.slice(html.lastIndexOf("<script>")+8,html.lastIndexOf("</script>"));
const el=()=>new Proxy({value:"",style:{},classList:{add(){},remove(){}}},{get:(t,k)=>k in t?t[k]:(typeof k==="string"?(()=>el()):undefined),set:(t,k,v)=>(t[k]=v,true)});
global.document={getElementById:()=>el(),createElement:()=>el(),body:el()};global.setInterval=()=>0;global.navigator={};global.window={top:1};
const api=new Function(js+";return {TERMO,tok,DF,D};")();
for(const m of msgs){const f=" "+api.tok(m).join(" ")+" ";const hits=[];for(const [k,is] of api.TERMO) if(f.includes(" "+k+" ")) hits.push(k+"("+(api.DF.get(k)||"-")+")→"+[...is].map(i=>api.D.livro[i].ancora).slice(0,3).join(","));console.log(m,"|",hits.join(" ; "));}
