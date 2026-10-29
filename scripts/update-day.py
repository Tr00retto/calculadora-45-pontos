"""Preserva a última tabela anterior ao dia, no fuso de Brasília."""
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def update(current, previous):
    stamp = datetime.fromisoformat(current['fetchedAt'])
    day = stamp.astimezone(ZoneInfo('America/Sao_Paulo')).date().isoformat()
    snapshot = {'date': day, 'fetchedAt': current['fetchedAt'], 'teams': current['teams']}
    if previous and previous['current']['date'] > day:
        raise ValueError('Data de coleta retrocedeu')
    baseline = (previous.get('before') if previous['current']['date'] == day else previous['current']) if previous else None
    return {'current': snapshot, 'before': baseline}


if __name__ == '__main__':
    path = Path('mudancas.json')
    current = json.loads(Path('classificacao.json').read_text())
    previous = json.loads(path.read_text()) if path.exists() else None
    result = update(current, previous)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    temp.replace(path)
