import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const dir=path.resolve(process.argv[2]);
const casos=JSON.parse(await fs.readFile(path.join(dir,'casos.json'),'utf8'));
const inicio=Number(process.argv[3]||1);
const fim=Number(process.argv[4]||999);
for (const c of casos.filter(c=>c.n>=inicio&&c.n<=fim)) {
  const wb=Workbook.create();
  const sh=wb.worksheets.add('ANALISE');
  let linhas=c.linhas;
  if (c.duplicada) linhas=[...linhas,linhas.find(l=>l[0]==='vida_max')];
  sh.getRange(`A1:D${linhas.length}`).values=linhas.map(l=>l.map(v=>typeof v==='string'&&v.startsWith('=')?"'"+v:v));
  sh.showGridLines=false;
  sh.freezePanes.freezeRows(1);
  sh.getRange(`A1:D${linhas.length}`).format.font={name:'Arial',size:10};
  sh.getRange('A1:D1').format={fill:'#28384C',font:{name:'Arial',bold:true,color:'#FFFFFF'},rowHeight:24};
  sh.getRange(`A1:A${linhas.length}`).format.columnWidth=48;
  sh.getRange(`B1:B${linhas.length}`).format.columnWidth=48;
  sh.getRange(`C1:C${linhas.length}`).format.columnWidth=34;
  sh.getRange(`D1:D${linhas.length}`).format.columnWidth=16;
  wb.recalculate();
  if (c.n===1) {
    console.log((await wb.inspect({kind:'table',range:'ANALISE!A1:D10',include:'values,formulas',tableMaxRows:10,tableMaxCols:4,maxChars:2000})).ndjson);
    const preview=await wb.render({sheetName:'ANALISE',range:'A1:D10',scale:1,format:'png'});
    await fs.writeFile(path.join(dir,'analise-preview.png'),new Uint8Array(await preview.arrayBuffer()));
  }
  const file=await SpreadsheetFile.exportXlsx(wb);
  await file.save(path.join(dir,c.file));
  console.log(c.file);
}
