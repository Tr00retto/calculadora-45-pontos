"""Campanha por mando, validada contra a classificação da mesma página."""
import importlib.util, json, os, re, sys, urllib.request
from pathlib import Path
from datetime import datetime, timezone
spec=importlib.util.spec_from_file_location('standings',Path(__file__).with_name('update-standings.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

def collect(html):
    parser=s.Tables();parser.feed(html)
    matrices=[t for t in parser.tables if len(t)==21 and len(t[0])==21 and 'Mandante' in t[0][0] and 'Visitante' in t[0][0]]
    if len(matrices)!=1:raise ValueError('Matriz de resultados ausente ou ambígua')
    rows=matrices[0][1:];teams=[]
    for row in rows:
        if len(row)!=21:raise ValueError('Linha incompleta')
        name=row[0];club=s.CLUBS.get(s.normalized(name))
        if club is None:raise ValueError('Clube desconhecido: '+name)
        teams.append({'id':club,'name':name,**{v:dict(played=0,points=0,wins=0,draws=0,losses=0,goalsFor=0,goalsAgainst=0) for v in ('home','away')}})
    if len({t['id'] for t in teams})!=20:raise ValueError('Clubes duplicados')
    for i,row in enumerate(rows):
        for j,cell in enumerate(row[1:]):
            if i==j:continue
            score=re.fullmatch(r'(\d+)\s*[–−-]\s*(\d+)',cell)
            if not score:
                if cell not in ('','a'):raise ValueError('Placar desconhecido: '+cell)
                continue
            hg,ag=map(int,score.groups())
            for stats,gf,ga in [(teams[i]['home'],hg,ag),(teams[j]['away'],ag,hg)]:
                stats['played']+=1;stats['goalsFor']+=gf;stats['goalsAgainst']+=ga
                stats['wins' if gf>ga else 'draws' if gf==ga else 'losses']+=1
                stats['points']+=3 if gf>ga else 1 if gf==ga else 0
    table=next(t for t in parser.tables if t and 'Pts' in t[0] and 'GP' in t[0] and 'GC' in t[0]);header=table[0]
    reference={s.CLUBS[s.normalized(r[1])]:r for r in table[1:] if r and r[0].isdigit()}
    for t in teams:
        for field,col in [('played','J'),('points','Pts'),('wins','V'),('draws','E'),('losses','D'),('goalsFor','GP'),('goalsAgainst','GC')]:
            if t['home'][field]+t['away'][field]!=int(reference[t['id']][header.index(col)]):raise ValueError('Matriz diverge da tabela: '+t['name']+' / '+field)
        if any(t[v]['played']>19 for v in ('home','away')):raise ValueError('Mais de 19 jogos por mando')
    return {'season':2026,'fetchedAt':datetime.now(timezone.utc).isoformat(),'sourceUrl':s.SOURCE,'license':'CC BY-SA 4.0','teams':teams}

def main():
    req=urllib.request.Request(s.SOURCE,headers={'User-Agent':'EsporteComValor/1.0'})
    with urllib.request.urlopen(req,timeout=40) as r:html=r.read(5_000_001)
    if len(html)>5_000_000:raise ValueError('Resposta muito grande')
    data=collect(html.decode('utf-8'));path=Path('mando.json')
    if path.exists():
        old={t['id']:t for t in json.loads(path.read_text())['teams']}
        if any(sum(t[v]['played'] for v in ('home','away'))<sum(old[t['id']][v]['played'] for v in ('home','away')) for t in data['teams']):raise ValueError('Fonte retrocedeu')
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path)
    print('Mando: 20 campanhas conferidas com pontos, jogos, V/E/D e gols da tabela.')
if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Mando: última coleta preservada. '+str(exc),file=sys.stderr)
        if not Path('mando.json').exists():sys.exit(1)
