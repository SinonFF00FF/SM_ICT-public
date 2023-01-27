from PIL import Image
from typing import *
import matplotlib as mpl
from snn_picc import get_bit_deep
from snn_grl import kwargs_handler


class IA:

    def __init__(self, img_in: Image):
        self.img_obj = img_in
        self.bit_deep = get_bit_deep(img_in.mode)
        self.channel_count = len(self.img_obj.mode)

    def analyse_img(self) -> Dict[str, Any]:
        def get_img_data() -> Generator[Tuple[Tuple[int, ...], int], None, None]:
            for yn in range(self.img_obj.height):
                for xn in range(self.img_obj.width):
                    yield self.img_obj.getpixel((xn, yn)), yn * self.img_obj.width + xn

        list1, list2 = [[0] * self.bit_deep ** 2] * self.channel_count, [0] * self.channel_count
        list3, a = [[False] * self.img_obj.height * self.img_obj.width] * self.channel_count, get_img_data()
        b = tuple([0] * self.channel_count)
        for y0, y1 in a:
            for iy, yy in enumerate(zip(y0, b)):
                d = yy[0] ^ yy[1]
                e = bin(d)[2:]
                list2[iy] += sum([yy == "1" for yy in e])
                list1[iy][d] += 1
                list3[iy][y1] = e[-1] == "1" and d == 1
            b = y0

    def show_plot(self) -> Image:
        pass

    def show_a_img(self) -> Image:
        pass

    def full_a(self) -> Dict[str, Union[Image, bool, str]]:
        pass
