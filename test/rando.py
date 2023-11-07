import unittest

from pydicom import dcmread
from pydicom.fileset import FileSet


class MyTestCase(unittest.TestCase):
    def test_something(self):
        file = open("../assets/IM000001.dcm", "rb")
        ds = dcmread(fp=file, specific_tags=["7FE0"])
        #ds.get()
        values = ds.__dict__['_dict']
        print(len(values.keys()))
        for key in values.keys():
            thing = ds.get(key=key)
            if key.group >= 32736:
                print(thing)
            #print(ds.get(key=key))
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
#https://fastapi.tiangolo.com/tutorial/testing/