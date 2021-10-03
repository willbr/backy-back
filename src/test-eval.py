import unittest
import src.eval

def setup_stack(s):
        rs = reversed(s.split())
        src.eval.input_stack = list(rs)

class Prefix_Tests(unittest.TestCase):
    def setUp(self):
        src.eval.input_stack = []

    def test_simple(self):
        setup_stack("+ 1 2 ]")
        r = src.eval.parse_prefix()
        er = "1 2 +".split()
        self.assertEqual(r,er)

    def test_child_prefix(self):
        setup_stack("+ 1 [ + 2 3 ] ]")
        r = src.eval.parse_prefix()
        er = "1 2 3 + +".split()
        self.assertEqual(r,er)

    def test_child_infix(self):
        setup_stack("+ 1 ( 2 + 3 ) ]")
        r = src.eval.parse_prefix()
        er = "1 2 3 + +".split()
        self.assertEqual(r,er)

    def test_child_postfix(self):
        setup_stack("+ 1 { 2 3 + } ]")
        r = src.eval.parse_prefix()
        er = "1 2 3 + +".split()
        self.assertEqual(r,er)

    def on_cleanup(self):
        print("clean")


if __name__ == '__main__':
    unittest.main()

