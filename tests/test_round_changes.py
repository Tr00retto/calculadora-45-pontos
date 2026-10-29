import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

spec = importlib.util.spec_from_file_location('changes', Path(__file__).parents[1]/'scripts/update-day.py')
changes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(changes)


def table(date, swap=False):
    teams = [{'id': i, 'name': str(i), 'points': 40-i, 'played': 32} for i in range(20)]
    if swap:
        teams[8], teams[9] = teams[9], teams[8]
    return {'fetchedAt': date, 'teams': teams}


def form(number, stamp):
    return {'teams': [{'recent': [{'id': str(number), 'round': f'Rodada {number}', 'date': int(changes.datetime.fromisoformat(stamp).timestamp()*1000)}]}]}


class RoundChanges(unittest.TestCase):
    def setUp(self):
        self.before = table('2026-10-27T23:00:00+00:00')
        self.current = table('2026-10-29T01:00:00+00:00', True)
        self.previous = {'current': changes.snapshot(self.before)}
        self.form = form(33, '2026-10-28T22:30:00+00:00')

    def test_all_clubs_including_idle_club(self):
        result = changes.update(self.current, self.previous, self.form, {})
        self.assertEqual(result['roundBefore']['teams'][8]['id'], 8)
        self.assertEqual(result['current']['teams'][9]['id'], 8)
        self.assertEqual(result['current']['teams'][9]['played'], 32)
        self.assertEqual(len(result['current']['teams']), 20)

    def test_midnight_does_not_reset_round(self):
        result = changes.update(self.current, self.previous, self.form, {})
        later = deepcopy(self.current)
        later['fetchedAt'] = '2026-10-30T04:00:00+00:00'
        updated = changes.update(later, result, self.form, {})
        self.assertEqual(updated['roundBefore'], result['roundBefore'])
        self.assertEqual(updated['before'], result['current'])

    def test_new_round_uses_last_snapshot_before_kickoff(self):
        result = changes.update(self.current, self.previous, self.form, {})
        later = deepcopy(self.current)
        later['fetchedAt'] = '2026-11-03T04:00:00+00:00'
        updated = changes.update(later, result, form(34, '2026-11-02T22:00:00+00:00'), {})
        self.assertEqual(updated['round']['number'], 34)
        self.assertEqual(updated['roundBefore'], result['current'])

    def test_delayed_match_does_not_rewind_round(self):
        result = changes.update(self.current, self.previous, self.form, {})
        updated = changes.update(self.current, result, form(30, '2026-10-29T00:00:00+00:00'), {})
        self.assertEqual(updated['round']['number'], 33)
        self.assertEqual(updated['roundBefore'], result['roundBefore'])

    def test_no_reference_is_not_maintained(self):
        result = changes.update(self.current, None, self.form, {})
        self.assertIsNone(result['roundBefore'])


if __name__ == '__main__':
    unittest.main()
