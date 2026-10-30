import importlib.util,unittest
from pathlib import Path
sp=importlib.util.spec_from_file_location('firstgoal',Path(__file__).parents[1]/'scripts/update-goal-clock.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class FirstGoal(unittest.TestCase):
 def test_unordered_feed(self):
  self.assertEqual(m.first_goal([{'team':1,'minute':'80'},{'team':2,'minute':'12'}]),{'firstScorer':2,'firstGoalStatus':'known'})
 def test_stoppage_does_not_spill_into_next_half(self):
  self.assertEqual(m.first_goal([{'team':1,'minute':'46'},{'team':2,'minute':'45+12'}])['firstScorer'],2)
 def test_same_minute_uses_seconds_only_when_available(self):
  goals=[{'team':1,'minute':'10','seconds':580},{'team':2,'minute':'10','seconds':555}]
  self.assertEqual(m.first_goal(goals)['firstScorer'],2)
  goals[0].pop('seconds');self.assertEqual(m.first_goal(goals)['firstGoalStatus'],'ambiguous')
 def test_equal_seconds_excluded(self):
  self.assertEqual(m.first_goal([{'team':1,'minute':'10','seconds':555},{'team':2,'minute':'10','seconds':555}])['firstGoalStatus'],'ambiguous')
 def test_same_team_tie_and_no_goal(self):
  self.assertEqual(m.first_goal([{'team':1,'minute':'10'},{'team':1,'minute':'10'}])['firstScorer'],1)
  self.assertEqual(m.first_goal([]),{'firstScorer':None,'firstGoalStatus':'goalless'})
if __name__=='__main__':unittest.main()
