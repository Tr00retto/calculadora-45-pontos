"""Tabela comunitária da Wikipédia; consulta periódica, sem chave ou dependências."""
import json, os, re, sys, unicodedata, urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

SOURCE='https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A'
LICENSE='https://creativecommons.org/licenses/by-sa/4.0/'
CLUBS={'flamengo':127,'palmeiras':121,'athletico paranaense':134,'fluminense':124,'bahia':118,'cruzeiro':135,'atletico mineiro':1062,'santos':128,'red bull bragantino':794,'sao paulo':126,'coritiba':147,'vitoria':136,'botafogo':120,'mirassol':7848,'vasco da gama':133,'corinthians':131,'internacional':119,'gremio':130,'remo':1198,'chapecoense':132}

def normalized(s):
    s=re.sub(r'\([^)]*\)|\[[^]]*\]','',s)
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c)).lower().split())

class Tables(HTMLParser):
    def __init__(self):
        super().__init__();self.tables=[];self.stack=[];self.cell=None;self.skip=0;self.row=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('style','script'):self.skip+=1
        if tag=='table':self.stack.append([])
        if self.stack and tag=='tr':self.row=[]
        if self.stack and tag in ('td','th'):self.cell=[]
    def handle_data(self,data):
        if self.cell is not None and not self.skip:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('style','script'):self.skip=max(0,self.skip-1)
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        if tag=='tr' and self.stack:self.stack[-1].append(self.row)
        if tag=='table' and self.stack:self.tables.append(self.stack.pop())

def parse_table(html):
    parser=Tables();parser.feed(html)
    candidates=[]
    for table in parser.tables:
        if not table:continue
        header=table[0]
        if 'Pts' not in header or 'J' not in header:continue
        pi,ji=header.index('Pts'),header.index('J')
        teams=[]
        for row in table[1:]:
            if len(row)<=max(pi,ji) or not row[0].isdigit():continue
            name=normalized(row[1]);clubid=CLUBS.get(name)
            if clubid is None:raise ValueError('Time desconhecido na classificação: '+name)
            points,played=int(row[pi]),int(row[ji])
            if not 0<=played<=38 or not 0<=points<=3*played:raise ValueError('Pontos ou jogos inválidos')
            teams.append({'id':clubid,'name':re.sub(r'\s*\([^)]*\)','',row[1]).strip(),'points':points,'played':played})
        if len(teams)==20 and len({t['id'] for t in teams})==20:candidates.append(teams)
    if len(candidates)!=1:raise ValueError('Não foi encontrada uma classificação única com os 20 clubes')
    if sum(t['played'] for t in candidates[0])%2:raise ValueError('Quantidade de jogos inconsistente')
    return candidates[0]

def make_data(html,previous):
    teams=parse_table(html)
    old={t['id']:t for t in previous.get('teams',[])}
    if any(t['played']<old.get(t['id'],{}).get('played',0) for t in teams):
        raise ValueError('Fonte está atrás do cadastro anterior; atualização rejeitada para não retroceder jogos')
    revision=re.search(r'wgRevisionId["\s]*:\s*(\d+)',html)
    return {'league':71,'season':2026,'fetchedAt':datetime.now(timezone.utc).isoformat(),'sourceUpdatedAt':None,'source':'Wikipédia — colaboradores do artigo','sourceUrl':SOURCE,'sourceHistoryUrl':SOURCE+'&action=history' if '?' in SOURCE else SOURCE+'?action=history','sourceRevision':revision.group(1) if revision else None,'license':'CC BY-SA 4.0','licenseUrl':LICENSE,'notice':'Extração e normalização dos pontos e jogos da tabela comunitária. A data de consulta não garante atualização após cada partida.','teams':teams}

def main():
    path=Path('classificacao.json');previous=json.loads(path.read_text()) if path.exists() else {}
    req=urllib.request.Request(SOURCE,headers={'User-Agent':'EsporteComValorStandings/1.0 (https://github.com/Tr00retto/calculadora-45-pontos; periodic table update)','Accept':'text/html'})
    with urllib.request.urlopen(req,timeout=45) as res:
        if res.status!=200:raise ValueError('Falha HTTP '+str(res.status))
        html=res.read(5_000_001)
        if len(html)>5_000_000:raise ValueError('Resposta excede tamanho esperado')
    data=make_data(html.decode('utf-8'),previous)
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path)
    print('Classificação validada: 20 clubes. Fonte: Wikipédia, CC BY-SA 4.0. Nenhuma chave utilizada.')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Atualização cancelada; dados anteriores preservados: '+str(exc),file=sys.stderr);sys.exit(1)
