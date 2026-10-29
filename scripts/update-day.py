"""Comparações diária (legada) e acumulada desde o início da rodada.

A ordem vem da tabela publicada: não recalculamos desempates incompletos.
As observações com mudanças são guardadas para recuperar o início da rodada.
"""
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def snapshot(current):
    stamp = datetime.fromisoformat(current['fetchedAt'])
    return {'date': stamp.astimezone(ZoneInfo('America/Sao_Paulo')).date().isoformat(),
            'fetchedAt': current['fetchedAt'], 'teams': current['teams']}


def round_number(label):
    match = re.fullmatch(r'Rodada\s+(\d+)', str(label or '').strip())
    return int(match[1]) if match and 1 <= int(match[1]) <= 38 else None


def active_round(form, calendar):
    # Rodada mais alta com resultado final. Jogo atrasado de rodada anterior
    # não reinicia o balanço; partidas futuras não antecipam sua troca.
    completed = {m['id']: m for t in form.get('teams', []) for m in t.get('recent', [])}
    known = [(round_number(m.get('round')), m) for m in completed.values()]
    known = [(n, m) for n, m in known if n is not None]
    if not known:
        return None
    number = max(n for n, _ in known)
    starts = [m['date'] for n, m in known if n == number]
    starts += [m['date'] for m in calendar.get('fixtures', [])
               if round_number(m.get('round')) == number and isinstance(m.get('date'), (int, float))]
    return {'number': number, 'startedAt': datetime.fromtimestamp(min(starts)/1000, timezone.utc).isoformat()}


def update(current, previous, form=None, calendar=None):
    now = snapshot(current)
    if previous and datetime.fromisoformat(previous['current']['fetchedAt']) > datetime.fromisoformat(now['fetchedAt']):
        raise ValueError('Data de coleta retrocedeu')
    # Mantém o contrato diário usado pelo Apps Script já instalado.
    daily = (previous.get('before') if previous['current']['date'] == now['date'] else previous['current']) if previous else None
    observations = list((previous or {}).get('history', []))
    for item in [daily, (previous or {}).get('current'), now]:
        if item:
            observations.append(item)
    observations.sort(key=lambda s: datetime.fromisoformat(s['fetchedAt']))
    history = []
    for item in observations:
        if not history or item['teams'] != history[-1]['teams']:
            history.append(item)
    # O último estado anterior à mudança é a referência mais recente disponível.
        else:
            history[-1] = item
    info = active_round(form or {}, calendar or {})
    old_round = (previous or {}).get('round')
    if info is None:
        info = old_round
    if old_round and info and info['number'] < old_round['number']:
        info = old_round
    baseline = None
    if info:
        if old_round and old_round['number'] == info['number']:
            # Congela também a data inicial: fontes podem omitir jogos depois.
            info = old_round
            baseline = (previous or {}).get('roundBefore')
        if baseline is None:
            start = datetime.fromisoformat(info['startedAt'])
            candidates = [s for s in observations if datetime.fromisoformat(s['fetchedAt']) < start]
            if candidates:
                baseline = max(candidates, key=lambda s: datetime.fromisoformat(s['fetchedAt']))
    return {'current': now, 'before': daily, 'round': info,
            'roundBefore': baseline, 'history': history[-120:]}


if __name__ == '__main__':
    path = Path('mudancas.json')
    current = json.loads(Path('classificacao.json').read_text())
    previous = json.loads(path.read_text()) if path.exists() else None
    form = json.loads(Path('forma.json').read_text())
    calendar = json.loads(Path('raio-x.json').read_text())
    result = update(current, previous, form, calendar)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    temp.replace(path)
