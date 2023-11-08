import unittest
from typing import List

from pydicom import dcmread
from pydicom.fileset import FileSet

from src.domain.dicom.tag.dicom_tag import DicomTag


class MyTestCase(unittest.TestCase):
    def test_something(self):
        file = open("../assets/IM000001.dcm", "rb")
        ds = dcmread(fp=file)
        # ds.get()
        values = ds.__dict__['_dict']
        print(len(values.keys()))
        for key in values.keys():
            thing = ds.get(key=key)
            print(DicomTag.from_data_element(thing))
            print({
                "group_id": thing.tag.group,
                "element_id": thing.tag.element,
                "vr": thing.VR,
                "vm": thing.VM,
                "name": thing.name,
                "value": thing.value

            })
            if thing.tag.group == 8 and thing.tag.element == 144:
                DicomTag.from_data_element(thing)
                print("a")
            if thing.VM > 1:
                print(thing)
            if key.group >= 32736:
                print(key)
            # print(ds.get(key=key))
        self.assertEqual(True, False)  # add assertion here


tag = DicomTag[List[List[DicomTag]]](group_id=8, element_id=4416, name="Referenced Image Sequence", vr="SQ", value=[
    [
        DicomTag[str](group_id=8, element_id=4432, name="Referenced SOP Class UID", vr="UI",
                 value='1.2.840.10008.5.1.4.1.1.4'),
        DicomTag[str](group_id=8, element_id=4437, name="Referenced SOP Instance UID", vr="UI",
                 value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000391')
    ],
    [
        DicomTag[str](group_id=8, element_id=4432, name="Referenced SOP Class UID", vr="UI",
                 value='1.2.840.10008.5.1.4.1.1.4'),
        DicomTag[str](group_id=8, element_id=4437, name="Referenced SOP Instance UID", vr="UI",
                 value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000392')
    ],
    [
        DicomTag(group_id=8, element_id=4432, name="Referenced SOP Class UID", vr="UI",
                 value='1.2.840.10008.5.1.4.1.1.4'),
        DicomTag(group_id=8, element_id=4437, name="Referenced SOP Instance UID", vr="UI",
                 value='1.3.12.2.1107.5.2.6.24119.30000013121716094326500000390')
    ]
])
if __name__ == '__main__':
    unittest.main()
# https://fastapi.tiangolo.com/tutorial/testing/
