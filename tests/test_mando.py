import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('mando',Path(__file__).parents[1]/'scripts/update-mando.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Mando(unittest.TestCase):
    def test_splits_and_rejects_inconsistent_matrix(self):
        names=list(m.s.CLUBS)
        header='<tr><th>Mandante \\ Visitante</th>'+''.join('<th>'+str(i)+'</th>' for i in range(20))+'</tr>'
        rows=''.join('<tr><td>'+name+'</td>'+''.join('<td>'+('—' if i==j else '2–1' if i==0 and j==1 else '')+'</td>' for j in range(20))+'</tr>' for i,name in enumerate(names))
        cols=['Pos','Equipe','Pts','J','V','E','D','GP','GC']
        standings='<tr>'+''.join('<th>'+c+'</th>' for c in cols)+'</tr>'
        for i,name in enumerate(names):
            stats=[3,1,1,0,0,2,1] if i==0 else [0,1,0,0,1,1,2] if i==1 else [0]*7
            standings+='<tr>'+''.join('<td>'+str(x)+'</td>' for x in [i+1,name,*stats])+'</tr>'
        html='<table>'+header+rows+'</table><table>'+standings+'</table>'
        data=m.collect(html)
        self.assertEqual(data['teams'][0]['home']['points'],3)
        self.assertEqual(data['teams'][0]['away']['played'],0)
        self.assertEqual(data['teams'][1]['away']['goalsAgainst'],2)
        with self.assertRaises(ValueError):m.collect(html.replace('2–1','3–1'))
if __name__=='__main__':unittest.main()
