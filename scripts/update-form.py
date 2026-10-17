"""Coleta pública de resultados encerrados do Brasileirão; preserva a última versão em falhas."""
import json, re, sys, urllib.request, concurrent.futures, os
from datetime import datetime, timezone
from pathlib import Path
URLS = ['https://www.flashscore.com.br/futebol/brasil/brasileirao-serie-a/classificacao/hdLUdQGi/forma/geral/5/','https://www.flashscore.com.br/equipe/vasco/2RABlYFn/resultados/','https://www.flashscore.com.br/equipe/chapecoense/jcQV3XP6/resultados/']
ALIASES = {'Athletico-PR':'Athletico Paranaense','Atlético-MG':'Atlético Mineiro','Vasco':'Vasco da Gama'}
def parse_matches(html):
    matches={};now=datetime.now(timezone.utc).timestamp()*1000
    for feed in re.findall(r'data:\s*`([^`]+)`',html):
        stage=None
        for block in feed.split('~'):
            d=dict(x.split('÷',1) for x in block.split('¬') if '÷' in x)
            if 'ZA' in d:stage=d.get('ZC')
            if stage!='hdLUdQGi' or not d.get('AA') or d.get('AB')!='3':continue
            if not d.get('AG','').isdigit() or not d.get('AH','').isdigit():continue
            try:date=int(d['AD'])*1000
            except (KeyError,ValueError):continue
            if not 1767225600000<=date<=now:continue
            matches[d['AA']]={'id':d['AA'],'date':date,'home':d['AE'],'away':d['AF'],'hg':int(d['AG']),'ag':int(d['AH']),'round':d.get('ER','')}
    if not matches:raise ValueError('Nenhum resultado final da Série A 2026 encontrado')
    return list(matches.values())
def update(matches,previous):
    matches=sorted({m['id']:m for m in matches}.values(),key=lambda m:(-m['date'],m['id']));teams=[]
    for t in previous['teams']:
        recent=[]
        for m in matches:
            home=ALIASES.get(m['home'],m['home'])==t['name'];away=ALIASES.get(m['away'],m['away'])==t['name']
            if not home and not away:continue
            gf,ga=(m['hg'],m['ag']) if home else (m['ag'],m['hg'])
            recent.append({**m,'points':3 if gf>ga else 1 if gf==ga else 0,'opponent':m['away'] if home else m['home'],'venue':'Casa' if home else 'Fora','score':f'{gf}–{ga}'})
        marker=next((i for i,m in enumerate(recent) if m['id']==t['lastMatchId']),None)
        if len(recent)<10 or marker is None:raise ValueError('Histórico incompleto: '+t['name'])
        points=t['points']+sum(m['points'] for m in recent[:marker]);played=t['played']+marker
        if not 0<=played<=38 or not 0<=points<=3*played:raise ValueError('Classificação inconsistente')
        if sum(m['points'] for m in recent[:10])>points:raise ValueError('Resultados incompatíveis')
        teams.append({**t,'points':points,'played':played,'recent':recent[:10],'lastMatchId':recent[0]['id'],'lastMatchDate':recent[0]['date']})
    if len(teams)!=20 or len({t['id'] for t in teams})!=20:raise ValueError('Cadastro incompleto')
    return {**previous,'teams':teams,'fetchedAt':datetime.now(timezone.utc).isoformat(),'status':'updated'}
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'EsporteComValor/1.0 (+https://esportecomvalor.wordpress.com/)','Accept':'text/html'})
    with urllib.request.urlopen(request,timeout=30) as response:
        raw=response.read(3000001)
        if len(raw)>3000000:raise ValueError('Resposta muito grande')
        return raw.decode('utf-8')
def main():
    path=Path('forma.json');previous=json.loads(path.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:pages=list(pool.map(fetch,URLS))
    matches=[m for page in pages for m in parse_matches(page)];data=update(matches,previous)
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path)
    print('Forma validada: 20 clubes, 10 partidas por clube, apenas Série A 2026.')
if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Consulta de forma falhou; última coleta preservada: '+str(exc),file=sys.stderr)
        # Mantém a publicação das ferramentas e da classificação mesmo se a fonte falhar.
        if not Path('forma.json').exists():sys.exit(1)
