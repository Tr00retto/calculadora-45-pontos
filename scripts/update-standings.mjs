import {writeFile,rename} from 'node:fs/promises';
export function normalize(body){
 if(!body||!body.errors)throw Error('Resposta inesperada da API; classificação anterior preservada.');
 if(Object.keys(body.errors).length){
  let detail=JSON.stringify(body.errors);
  const key=process.env.API_FOOTBALL_KEY;
  if(key)detail=detail.split(key).join('[CHAVE OCULTA]');
  detail=detail.replace(/[\\r\\n]/g,' ').slice(0,600);
  throw Error('Erro informado pela API-Sports: '+detail+'; classificação anterior preservada.');
 }
 const league=body.response?.[0]?.league;
 if(league?.id!==71||league?.season!==2026)throw Error('Campeonato ou temporada inesperados.');
 const rows=league.standings?.[0];
 if(!Array.isArray(rows)||rows.length!==20)throw Error('Classificação incompleta: esperados 20 clubes.');
 const teams=rows.map(r=>({id:r.team?.id,name:r.team?.name,points:r.points,played:r.all?.played}));
 if(new Set(teams.map(t=>t.id)).size!==20||teams.some(t=>!Number.isInteger(t.id)||!t.name||!Number.isInteger(t.points)||!Number.isInteger(t.played)||t.points<0||t.played<0||t.played>38||t.points>3*t.played))throw Error('Dados de classificação inválidos.');
 const sourceUpdatedAt=rows.map(r=>r.update).filter(Boolean).sort().at(-1)||null;
 return {league:71,season:2026,fetchedAt:new Date().toISOString(),sourceUpdatedAt,source:'API-Football / API-Sports',teams};
}
export async function update(){
 const key=process.env.API_FOOTBALL_KEY;
 if(!key)throw Error('Cadastre o Secret API_FOOTBALL_KEY antes de executar.');
 const res=await fetch('https://v3.football.api-sports.io/standings?league=71&season=2026',{headers:{'x-apisports-key':key},signal:AbortSignal.timeout(30000)});
 if(!res.ok)throw Error('Falha HTTP '+res.status+'; classificação anterior preservada.');
 const data=normalize(await res.json());
 await writeFile('classificacao.json.tmp',JSON.stringify(data,null,2)+'\n');
 await rename('classificacao.json.tmp','classificacao.json');
 console.log('Classificação validada: '+data.teams.length+' clubes.');
}
if(process.argv[1]?.endsWith('update-standings.mjs'))update().catch(e=>{console.error(e.message);process.exitCode=1;});
