import unittest

from pydicom import DataElement

from src.domain.dicom.tag.dicom_tag import DicomTag


class DicomTagTest(unittest.TestCase):

    class Helper:

        @staticmethod
        def construct_test_data_element(group_id, element_id, vr, name, value, vm=1):
            data_element = DataElement(tag=(group_id, element_id),
                                       VR=vr, value=value)
            expected_tag = DicomTag(
                group_id=group_id,
                element_id=element_id,
                vr=vr,
                vm=vm,
                name=name,
                value=value
            )

            return data_element, expected_tag

    def test_from_data_element(self):
        expected_group_id = 8
        expected_element_id = 4410
        expected_vr = "CS"
        expected_value = "1"
        expected_name = 'Referenced Waveform Sequence'

        data_element, expected_tag = DicomTagTest.Helper.construct_test_data_element(
            expected_group_id, expected_element_id, expected_vr, expected_name, expected_value
        )

        actual_tag = DicomTag.from_data_element(data_element)

        self.assertEqual(expected_tag, actual_tag)

    def test_from_data_element_list(self):
        expected_group_id = 8
        expected_element_id = 4410
        expected_vr = "CS"
        expected_value = ["1", "2", "3"]
        expected_name = 'Referenced Waveform Sequence'

        data_element, expected_tag = DicomTagTest.Helper.construct_test_data_element(
            expected_group_id, expected_element_id, expected_vr, expected_name, expected_value,
            3
        )

        actual_tag = DicomTag.from_data_element(data_element)

        self.assertEqual(expected_tag, actual_tag)


if __name__ == '__main__':
    unittest.main()
