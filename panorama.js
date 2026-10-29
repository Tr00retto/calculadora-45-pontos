/* As simulações da calculadora não alteram estes dados. */
(function(){
'use strict';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const stamp=s=>new Date(s).toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'});
const badge=t=>typeof badges!=='undefined'&&badges[t.id]?`<img src="${badges[t.id]}" alt="" loading="lazy">`:'';
async function read(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error('Falha na coleta');return r.json();}
function top(teams,key,direction){const sorted=[...teams].sort((a,b)=>direction*(a[key]-b[key])||a.name.localeCompare(b.name,'pt-BR'));const limit=sorted[2][key];return sorted.filter(t=>direction*(t[key]-limit)<=0);}
async function goals(){const el=document.getElementById('goal-content');try{
const data=await read('./forma.json');
if(data.teams?.length!==20||!data.teams.every(t=>Number.isInteger(t.goalsFor)&&t.goalsFor>=0&&Number.isInteger(t.goalsAgainst)&&t.goalsAgainst>=0&&Number.isInteger(t.played)&&t.played>0))throw Error('Gols incompletos');
const cards=[['Três melhores ataques','goalsFor',-1,'marcados'],['Três melhores defesas','goalsAgainst',1,'sofridos'],['Três piores ataques','goalsFor',1,'marcados'],['Três piores defesas','goalsAgainst',-1,'sofridos']];
el.innerHTML=`<p class="small">Última consulta: ${esc(stamp(data.fetchedAt))} (Brasília). Fonte: <a href="https://www.flashscore.com.br/futebol/brasil/brasileirao-serie-a/">Flashscore</a>.${Date.now()-new Date(data.fetchedAt)>36*3600000?' Atenção: dados há mais de 36 horas sem atualização.':''}</p><div class="goal-grid">`+cards.map(([title,key,dir,label])=>`<article class="goal-card"><h3>${title}</h3><ul class="goal-list">${top(data.teams,key,dir).map((t,i,arr)=>`<li><span>${i&&arr[i-1][key]===t[key]?arr.findIndex(a=>a[key]===t[key])+1:i+1}º</span>${badge(t)}<strong class="goal-name">${esc(t.name)}</strong><span class="goal-value"><strong>${t[key]}</strong> ${label}<small>${(t[key]/t.played).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})}/jogo · ${t.played} jogos</small></span></li>`).join('')}</ul></article>`).join('')+'</div>';
}catch(e){el.textContent='Rankings indisponíveis nesta consulta. Tente novamente mais tarde.';}}
async function day(){const el=document.getElementById('day-content');try{const data=await read('./mudancas.json');const {current}=data;const before=data.roundBefore;const round=data.round;
if(!current||current.teams?.length!==20)throw Error('Tabela incompleta');
if(!before||!round){el.textContent="Referência anterior ao início da rodada indisponível. A comparação será exibida quando houver um registro válido, sem presumir que os clubes mantiveram a posição.";return;}
const old=new Map(before.teams.map((t,i)=>[t.id,{...t,position:i+1}]));
if(old.size!==20||current.teams.some(t=>!old.has(t.id)))throw Error('Tabelas incompatíveis');

const games=(current.teams.reduce((n,t)=>n+t.played,0)-before.teams.reduce((n,t)=>n+t.played,0))/2;
el.innerHTML=`<p><strong>Balanço da ${esc(round.number)}ª rodada</strong> · ${games} jogo(s) incorporado(s) desde o início da rodada.</p><p class="small">Referência antes da rodada: ${esc(stamp(before.fetchedAt))}. Última consulta: ${esc(stamp(current.fetchedAt))} (Brasília).${Date.now()-new Date(current.fetchedAt)>36*3600000?' Atenção: coleta desatualizada.':''} Comparação acumulada dos 20 clubes desde o início da rodada, incluindo mudanças causadas por resultados dos rivais. A referência não muda à meia-noite. O balanço pode ser parcial enquanto houver jogos ou atualização pendente da fonte; partidas atrasadas disputadas no intervalo também afetam a tabela.</p><div class="day-scroll"><table class="day-table"><thead><tr><th scope="col">Clube</th><th scope="col">Antes da rodada</th><th scope="col">Agora</th><th scope="col">Mudança</th><th scope="col">Pontos</th></tr></thead><tbody>${current.teams.map((t,i)=>{const prev=old.get(t.id),delta=prev.position-i-1;return `<tr><td><span class="day-club">${badge(t)}${esc(t.name)}</span></td><td>${prev.position}º</td><td>${i+1}º</td><td class="day-${delta>0?'up':delta<0?'down':'flat'}">${delta>0?'▲ Subiu '+delta:delta<0?'▼ Caiu '+(-delta):'— Manteve'}</td><td>${prev.points} → ${t.points}</td></tr>`;}).join('')}</tbody></table></div><p class="small">Ordem da tabela comunitária da <a href="https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A">Wikipédia</a> (CC BY-SA 4.0), preservando os desempates publicados.</p>`;
}catch(e){el.textContent='Comparação da rodada indisponível nesta consulta. Tente novamente mais tarde.';}}
goals();day();
})();

