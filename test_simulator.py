import unittest
from simulator import *
class SimulationTests(unittest.TestCase):
 def test_accounting(self):
  rows,m=simulate([Request(0,0,0,0,False),Request(1,0,0,0,True)])
  self.assertEqual([r["finish"] for r in rows],[8,13])
  self.assertEqual(m["row_hit_rate"],.5)
 def test_conflict(self):
  rows,_=simulate([Request(0,0,0,0,False),Request(1,0,0,1,False)])
  self.assertEqual(rows[1]["finish"],19)
 def test_refresh(self):
  rows,m=simulate(list(generate(200)),timing=Timing(refi=15))
  self.assertGreater(m["refresh_wait"],0)
  self.assertEqual(len({r["id"] for r in rows}),200)
  self.assertTrue(all(r["finish"]>r["arrival"] for r in rows))
 def test_frfcfs(self):
  req=[Request(0,0,0,0,0),Request(1,0,0,1,0),Request(2,0,0,0,0)]
  self.assertEqual([r["id"] for r in simulate(req,"frfcfs")[0]],[0,2,1])
 def test_reproducible(self):
  self.assertEqual(list(generate()),list(generate()))
if __name__=="__main__":unittest.main()
