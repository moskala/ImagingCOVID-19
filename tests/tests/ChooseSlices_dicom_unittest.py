import unittest
import os, sys
from pathlib import Path
# sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Methods'))
sys.path.append(str(Path().resolve().parent))
from ChooseSlices import ChooseSlices

testDir = Path('test_data/79262/')


class ChooseSlicesDicomUnittest(unittest.TestCase):
    def test_choose(self):
        cs = ChooseSlices()
        ind = cs.choose(testDir, 0.1)
        self.assertIsNotNone(ind)
        self.assertTrue(len(ind) > 0)


if __name__ == '__main__':
    unittest.main()
