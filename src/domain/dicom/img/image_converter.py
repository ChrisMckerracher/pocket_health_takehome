import numpy
from PIL import Image


class ImageConverter:

    @staticmethod
    def convert(np_array: numpy.ndarray) -> Image:
        np_array = np_array.astype(float)

        # https://pycad.co/how-to-convert-a-dicom-image-into-jpg-or-png/
        rescaled_image = (numpy.maximum(np_array, 0) / np_array.max()) * 255
        return Image.fromarray(numpy.uint8(rescaled_image))
