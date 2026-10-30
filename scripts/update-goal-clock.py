"""Relógio dos gols: eventos finais ESPN, minutos e placares conferidos por partida."""
import importlib.util, json, math, os, re, sys, urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
spec=importlib.util.spec_from_file_location('standings',Path(__file__).with_name('update-standings.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
URL='https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard?dates=2026&limit=1000'
ALIASES={'Atlético-MG':'Atlético Mineiro','Athletico-PR':'Athletico Paranaense'}
BINS=['1–15','16–30','31–45','45+','46–60','61–75','76–90','90+']

def minute_bin(display):
    match=re.fullmatch(r"\s*(\d+)\s*['’′]?\s*(?:\+\s*(\d+)\s*['’′]?)?\s*",str(display))
    if not match:raise ValueError('Minuto inválido')
    minute=int(match[1]);extra=int(match[2]) if match[2] is not None else None
    if extra is not None:
        if minute not in (45,90) or not 1<=extra<=30:raise ValueError('Acréscimo inválido')
        return (3 if minute==45 else 7),f'{minute}+{extra}'
    if not 0<=minute<=90:raise ValueError('Minuto sem período identificável')
    return (0 if minute<=15 else 1 if minute<=30 else 2 if minute<=45 else 4 if minute<=60 else 5 if minute<=75 else 6),str(minute)

def club_id(competitor):
    name=competitor['team']['displayName'];key=s.normalized(ALIASES.get(name,name))
    if key not in s.CLUBS:raise ValueError('Clube desconhecido: '+name)
    return s.CLUBS[key]

def first_goal(events):
    """Identifica o beneficiário do primeiro gol sem confiar na ordem da lista."""
    if not events:return {'firstScorer':None,'firstGoalStatus':'goalless'}
    def minute_key(goal):
        parts=goal['minute'].split('+');return (int(parts[0]),int(parts[1]) if len(parts)>1 else 0)
    first=min(minute_key(g) for g in events)
    candidates=[g for g in events if minute_key(g)==first]
    # Só usa os segundos para desempatar gols no mesmo minuto quando todos os têm.
    if all(isinstance(g.get('seconds'),(int,float)) and math.isfinite(g['seconds']) and g['seconds']>=0 for g in candidates):
        seconds=min(g['seconds'] for g in candidates);candidates=[g for g in candidates if g['seconds']==seconds]
    teams={g['team'] for g in candidates}
    return {'firstScorer':next(iter(teams)) if len(teams)==1 else None,'firstGoalStatus':'known' if len(teams)==1 else 'ambiguous'}

def parse_match(event,competition):
    competitors=competition['competitors']
    if len(competitors)!=2:raise ValueError('Adversários inválidos')
    home=next(c for c in competitors if c['homeAway']=='home');away=next(c for c in competitors if c['homeAway']=='away')
    ids={str(c['id']):club_id(c) for c in competitors}
    if len(set(ids.values()))!=2:raise ValueError('Clube duplicado')
    scores={str(c['id']):int(c['score']) for c in competitors}
    if any(n<0 or n>30 for n in scores.values()):raise ValueError('Placar inválido')
    goals=[];ordered=[]
    for detail in competition.get('details',[]):
        if not detail.get('scoringPlay') or detail.get('shootout'):continue
        if detail.get('scoreValue')!=1:raise ValueError('Evento sem valor de gol válido')
        # ESPN team é o beneficiário do gol, inclusive nos gols contra.
        # O atleta autor pode pertencer ao adversário e não define o crédito.
        team=str(detail['team']['id'])
        if team not in ids:raise ValueError('Beneficiário desconhecido')
        bucket,minute=minute_bin(detail['clock']['displayValue'])
        goal={'team':ids[team],'minute':minute,'bin':bucket}
        goals.append(goal);ordered.append({**goal,'seconds':detail['clock'].get('value')})
    counted=Counter(g['team'] for g in goals)
    if any(counted[ids[team]]!=score for team,score in scores.items()):raise ValueError('Gols não conferem com o placar')
    date=event['date']
    parsed=datetime.fromisoformat(date.replace('Z','+00:00'))
    if parsed.year!=2026 or parsed>datetime.now(timezone.utc):raise ValueError('Data fora da temporada')
    return {'id':str(event['id']),'date':date,'home':ids[str(home['id'])],'away':ids[str(away['id'])],'hg':scores[str(home['id'])],'ag':scores[str(away['id'])],'goals':goals,**first_goal(ordered)}

def collect(payload):
    if not any(str(l.get('id'))=='630' for l in payload.get('leagues',[])):raise ValueError('Competição incorreta')
    events=payload.get('events',[])
    if not events or len(events)>=1000:raise ValueError('Lista vazia ou possivelmente truncada')
    teams={};matches={};excluded=[];seen=set();completed=Counter()
    for e in events:
        if e.get('season',{}).get('year')!=2026:continue
        comp=e['competitions'][0]
        for c in comp['competitors']:
            cid=club_id(c);teams[cid]={'id':cid,'name':ALIASES.get(c['team']['displayName'],c['team']['displayName']),'sourceId':str(c['id'])}
        status=comp['status']['type']
        if not status.get('completed') or status.get('name')!='STATUS_FULL_TIME':continue
        if e['id'] in seen:continue
        seen.add(e['id'])
        for c in comp['competitors']:completed[club_id(c)]+=1
        try:matches[str(e['id'])]=parse_match(e,comp)
        except (ValueError,KeyError,StopIteration,TypeError) as exc:excluded.append({'id':str(e['id']),'reason':str(exc)})
    if len(teams)!=20 or not matches or len(matches)<.8*len(seen):raise ValueError('Cobertura insuficiente; última coleta preservada')
    for cid,t in teams.items():t['completed']=completed[cid]
    return {'season':2026,'fetchedAt':datetime.now(timezone.utc).isoformat(),'source':'ESPN','sourceUrl':'https://www.espn.com.br/futebol/competicao/_/nome/bra.1','bins':BINS,'completedMatches':len(seen),'excluded':excluded,'teams':sorted(teams.values(),key=lambda t:t['name']),'matches':sorted(matches.values(),key=lambda m:(m['date'],m['id']))}

def main():
    req=urllib.request.Request(URL,headers={'User-Agent':'EsporteComValor/1.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=40) as response:raw=response.read(15_000_001)
    if len(raw)>15_000_000:raise ValueError('Resposta muito grande')
    data=collect(json.loads(raw));path=Path('relogio-gols.json')
    if path.exists():
        old=json.loads(path.read_text())
        if data['completedMatches']<old['completedMatches']:raise ValueError('Lista da fonte retrocedeu')
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n');os.replace(tmp,path)
    print(f"Relógio: {len(data['matches'])}/{data['completedMatches']} partidas com gols e minutos validados; {len(data['excluded'])} excluídas.")
if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Relógio: última coleta preservada. '+str(exc),file=sys.stderr)
        if not Path('relogio-gols.json').exists():sys.exit(1)
