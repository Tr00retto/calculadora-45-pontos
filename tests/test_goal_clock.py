import copy,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('clock',Path(__file__).parents[1]/'scripts/update-goal-clock.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def fixture():
 return {'id':'1','date':'2026-01-28T22:00Z'}, {'competitors':[{'id':'2029','team':{'displayName':'Palmeiras'},'homeAway':'home','score':'1'},{'id':'819','team':{'displayName':'Flamengo'},'homeAway':'away','score':'0'}],'details':[{'team':{'id':'2029'},'scoringPlay':True,'scoreValue':1,'clock':{'displayValue':"45'+2'"},'ownGoal':True,'athletesInvolved':[{'team':{'id':'819'}}]}]}
class GoalClock(unittest.TestCase):
 def test_boundaries_and_stoppage_time(self):
  for minute,bucket in [('0',0),('15',0),('16',1),('30',1),('31',2),('45',2),("45'+1'",3),('46',4),('60',4),('61',5),('75',5),('76',6),('90',6),('90+12',7)]:
   with self.subTest(minute=minute):self.assertEqual(c.minute_bin(minute)[0],bucket)
  for invalid in ['94','46+1','45+0','90+31','HT','-1']:
   with self.subTest(invalid=invalid),self.assertRaises(ValueError):c.minute_bin(invalid)
 def test_own_goal_credits_beneficiary(self):
  event,comp=fixture();match=c.parse_match(event,comp)
  self.assertEqual(match['goals'],[{'team':121,'minute':'45+2','bin':3}])
 def test_missing_or_wrong_team_events_rejected(self):
  event,comp=fixture();comp['details']=[]
  with self.assertRaises(ValueError):c.parse_match(event,comp)
  event,comp=fixture();comp['details'][0]['team']['id']='819'
  with self.assertRaises(ValueError):c.parse_match(event,comp)
 def test_goalless_match_included(self):
  event,comp=fixture();comp['competitors'][0]['score']='0';comp['details']=[]
  self.assertEqual(c.parse_match(event,comp)['goals'],[])
 def test_shootout_not_counted_and_same_minute_goals_preserved(self):
  event,comp=fixture();comp['details'].append({**copy.deepcopy(comp['details'][0]),'shootout':True})
  self.assertEqual(len(c.parse_match(event,comp)['goals']),1)
  comp['details'][-1]['shootout']=False;comp['competitors'][0]['score']='2'
  self.assertEqual(len(c.parse_match(event,comp)['goals']),2)
if __name__=='__main__':unittest.main()
