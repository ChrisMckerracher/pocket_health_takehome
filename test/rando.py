import unittest

from pydicom import dcmread
from pydicom.fileset import FileSet


class MyTestCase(unittest.TestCase):
    def test_something(self):
        ds = dcmread("../assets/IM000001.dcm")
        #ds.get()
        values = ds.__dict__['_dict']
        for key in values.keys():
            print(ds.get(key=key))
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
#https://fastapi.tiangolo.com/tutorial/testing/