import unittest

from pydicom import dcmread


class MyTestCase(unittest.TestCase):
    def test_something(self):
        ds = dcmread("../assets/IM000001.dcm")
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
#https://fastapi.tiangolo.com/tutorial/testing/