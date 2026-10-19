"""Atualiza calendário e força dos rivais em uma única coleta validada."""
import importlib.util, concurrent.futures, json, re, os, sys
from pathlib import Path
from datetime import datetime, timezone
spec=importlib.util.spec_from_file_location('form',Path(__file__).with_name('update-form.py'))
form=importlib.util.module_from_spec(spec);spec.loader.exec_module(form)
URL='https://www.flashscore.com.br/futebol/brasil/brasileirao-serie-a/calendario/'
def collect(pages,previous):
    matches=[m for page in pages for m in form.parse_matches(page)]
    data=form.update(matches,previous);ids={t['name']:t['id'] for t in data['teams']};fixtures={}
    for feed in re.findall(r'data:\s*`([^`]+)`',pages[0]):
        stage=None
        for block in feed.split('~'):
            d=dict(x.split('÷',1) for x in block.split('¬') if '÷' in x)
            if 'ZA' in d:stage=d.get('ZC')
            if stage!='hdLUdQGi' or not d.get('AA') or d.get('AB')=='3':continue
            if d.get('AB') not in {'1','2','4','5','6','7','8','9','10','11','12','13','16'}:raise ValueError('Status de partida desconhecido')
            home=ids[form.ALIASES.get(d['AE'],d['AE'])];away=ids[form.ALIASES.get(d['AF'],d['AF'])]
            fixtures[d['AA']]={'id':d['AA'],'home':home,'away':away,'date':int(d['AD'])*1000 if d.get('AD','').isdigit() else None,'round':d.get('ER','Rodada a confirmar'),'status':'scheduled' if d['AB']=='1' else 'pending'}
    # Preserva o jogo atrasado confirmado pela CBF quando a lista pública o omite.
    for old in previous['fixtures']:
        if old.get('status')!='postponed':continue
        home=next(t['name'] for t in data['teams'] if t['id']==old['home']);away=next(t['name'] for t in data['teams'] if t['id']==old['away'])
        played=any(form.ALIASES.get(m['home'],m['home'])==home and form.ALIASES.get(m['away'],m['away'])==away for m in matches)
        listed=any(m['home']==old['home'] and m['away']==old['away'] for m in fixtures.values())
        if not played and not listed:fixtures[old['id']]=old
    for t in data['teams']:
        count=sum(t['id'] in (m['home'],m['away']) for m in fixtures.values())
        if count!=38-t['played']:raise ValueError(f"Calendário incompleto: {t['name']}, {count} de {38-t['played']} partidas")
    data['fixtures']=sorted(fixtures.values(),key=lambda m:(m['date'] is None,m['date'] or 0,m['id']));data['sourceUrl']=URL
    return data

def main():
    p=Path('raio-x.json');previous=json.loads(p.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:pages=list(pool.map(form.fetch,[URL,*form.URLS]))
    data=collect(pages,previous);tmp=p.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False)+'\n');os.replace(tmp,p)
    print('Raio-X validado: calendário restante e força dos 20 clubes sincronizados.')
if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Raio-X: última coleta preservada. '+str(exc),file=sys.stderr)
        if not Path('raio-x.json').exists():sys.exit(1)
