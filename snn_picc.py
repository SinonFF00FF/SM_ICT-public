from typing import Tuple, List, Any, Optional, Generator
from PIL import Image

# May God have mercy with whoever has to read this abomination


def get_bit_deep(image_mode: str) -> int:
    """pls kill me why isn't that in the Image class \n
    :return bit_deep of the Image"""
    # pls dont change the vars names
    bit_deep_1, bit_deep_8 = ["1"], ["L", "P"]
    bit_deep_16 = ["LA", "PA", "La", "I;16", "I;16L", "I;16B", "I;16N", "BGR;16"]
    bit_deep_24 = ["RGB", "YCbCr", "LAB", "HSV", "BGR;24"]
    bit_deep_32 = ["I", "F", "CMYK", "RGBA", "BGR;32", "RGBa", "RGBX"]
    b = list(locals().keys())
    for iy, y in enumerate([bit_deep_1, bit_deep_8, bit_deep_16, bit_deep_24, bit_deep_32]):
        for yy in y:
            if image_mode == yy:
                return int(b[iy + 1].split("_")[-1])
    else:
        raise ValueError("image_mode isn't in bit_deep_list (or I forgot to add it (that's more likely))")


def bytes_to_bin(a: bytes) -> str:
    return "".join([make_set_len(bin(y)[2:], 8) for y in a])


def make_set_len(a: str, lenlen: int, fill_str: Optional[str] = "0") -> str:
    return fill_str * (lenlen - len(a)) + a


class EncodeICError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class DecodeICError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class SetCCError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class BuildICError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class IC:
    __alpha_chars = ["a", "A"]  # pls don't change if you don't know what you do (talking of you future Sinon)
    __static_cc = [[1]]  # same here
    __header_bin_item_map = {"0": "0", "1": "10", "end": "11"}  # and here

    def __init__(self, img_in: Image):
        """
        idk what to write here \n
        :param img_in: an Image obj
        """
        if img_in.is_animated:
            raise BuildICError("this doesnt work with animated Images")
        self.img_obj = img_in
        self.mode = img_in.mode
        self.bit_deep = get_bit_deep(self.mode)
        if self.mode[-1] in self.__alpha_chars:
            self.mode_edit = self.mode[:-1]
            self.bit_deep_edit = self.bit_deep - 8
        else:
            self.mode_edit = self.mode
            self.bit_deep_edit = self.bit_deep
        self.bit_change = [[0]] * len(self.mode)
        self.bit_deep_channel = self.bit_deep_edit / len(self.mode_edit)
        if str(self.bit_deep_channel)[-2:] != ".0":
            raise BuildICError(f"something is wrong sorry :): {self.get_error_vars()}")
        else:
            self.bit_deep_channel = int(self.bit_deep_channel)
        self.max_pixel_data = 0  # in bits
        self.max_pic_data_without_header = 0  # might div from the real max_data for 1 byte / in bytes
        self.header_len_bits = 0  # might div from the real header_len for 1 byte
        self.set_cc_input = None

    def get_error_vars(self) -> str:
        """ test stuff delete in the future """
        return f"\n {self}.locals:\n" + "\n".join([f"{y0}: {y1}" for y0, y1 in vars(self).items()])

    def __get_changeable_data(self) -> Generator[Tuple[int, ...], Any, None]:
        for y in range(self.img_obj.height):
            for x in range(self.img_obj.width):
                yield self.img_obj.getpixel((x, y))

    def __get_image_cords(self) -> Generator[Tuple[int, int], Any, None]:
        for y in range(self.img_obj.height):
            for x in range(self.img_obj.width):
                yield x, y

    def __set_cc(self, pixel_change: Tuple[int, ...]) -> None:
        """ needs to be called before you call the pe_encode/decode, make_header_bits or aline_data fkts"""
        if len(pixel_change) > len(self.mode):
            raise SetCCError(f"to many channels are given ({pixel_change} > {self.mode})")
        if not all([y < 2 ** self.bit_deep_channel for y in pixel_change]):
            raise SetCCError("more than one of the channel numbers are to big")
        if all([y == 0 for y in pixel_change]):
            raise SetCCError("at leased one channel must be changed")
        self.set_cc_input = pixel_change
        for iy, y in enumerate(pixel_change):
            a, list1 = [y for y in bin(y)[:1:-1]], []
            oc = a.count("1")
            if oc:
                for yy in range(oc):
                    idk_0 = a.index("1")
                    list1.append(idk_0 + 1)
                    a[idk_0] = "0"
                self.max_pixel_data += len(list1)
            else:
                list1 = [0]
            self.bit_change[iy] = list1
        self.max_pic_data_without_header = (self.max_pixel_data * self.img_obj.size[0] * self.img_obj.size[1]) // 8

    def __pe_encode(self, pixel: Tuple[int, ...], data: str, use_static_cc: Optional[bool] = False) -> Tuple[int, ...]:
        i, list1, cc = 0, [], self.bit_change
        if use_static_cc:
            cc = self.__static_cc * len(self.mode_edit)
        for y0, y1 in zip(pixel, cc):
            a = [y for y in make_set_len(bin(y0)[2:], self.bit_deep_channel)]
            for yy in y1:
                if not yy:
                    break
                else:
                    try:
                        a[self.bit_deep_channel - yy] = data[i]
                        i += 1
                    except IndexError:
                        a[self.bit_deep_channel - yy] = "0"
            list1.append(int("".join(a), 2))
        return tuple(list1)

    def __pe_decode(self, pixel: Tuple[int, ...], use_static_cc: Optional[bool] = False) -> str:
        list1, cc = [], self.bit_change
        if use_static_cc:
            cc = self.__static_cc * len(self.mode_edit)
        for y0, y1 in zip(pixel, cc):
            a = [y for y in make_set_len(bin(y0)[2:], self.bit_deep_channel)]
            for yy in y1:
                if yy == 0:
                    break
                else:
                    list1.append(a[self.bit_deep_channel - yy])
        return "".join(list1)

    def __make_header_bits(self, data_len: int) -> List[str]:
        list1, list2, list3 = [], [], []
        if len(self.set_cc_input) < len(self.mode):
            self.set_cc_input += tuple([0] * (len(self.mode) - len(self.set_cc_input)))
        for y in self.set_cc_input:
            for yy in bin(y)[2:]:
                list1.append(self.__header_bin_item_map[yy])
            list1.append(self.__header_bin_item_map["end"])
        out_str = "".join(list1 + [self.__header_bin_item_map[y] for y in bin(data_len)[2:]] +
                          [self.__header_bin_item_map["end"]])
        self.header_len_bits = len(out_str)
        for y in out_str:
            list2.append(y)
            if len(list2) == len(self.mode_edit):
                list3.append("".join(list2))
                list2 = []
        if list2:
            list3.append("".join(list2 + ["0" for y in range(len(self.mode_edit) - len(list2))]))
        return list3

    def __read_header_bits(self, gen_obj: Generator[Tuple[int, int], Any, None]) -> Tuple[Tuple[int, ...], int]:
        list1, list2, str1 = [], [], ""
        get_key = lambda val, search_dict: list(search_dict.keys())[list(search_dict.values()).index(val)]
        for iy, y in enumerate(gen_obj):
            a = self.__pe_decode(y, use_static_cc=True)
            for yy in a:
                str1 += yy
                if str1 in self.__header_bin_item_map.values():
                    if str1 == self.__header_bin_item_map["end"]:
                        list1.append(int("".join(list2), 2))
                        list2 = []
                        if len(list1) == len(self.mode) + 1:
                            return tuple(list1[:-1]), list1[-1]
                    else:
                        list2.append(get_key(str1, self.__header_bin_item_map))
                    str1 = ""
        else:
            raise DecodeICError("the header is longer than the file so its probably wrong or the file contains no data")

    def __aline_data(self, a: bytes) -> Generator[str, Any, None]:
        list1 = []
        if (len(a) * 8) // self.max_pixel_data + (self.header_len_bits * 8) // len(
                self.mode_edit) > self.max_pic_data_without_header * 8:
            idk0 = (len(a) * 8) // self.max_pixel_data + (self.header_len_bits * 8) // len(self.mode_edit)
            raise EncodeICError(f"your pic is to small >< (max_pic_data_without_header: "
                                f"{self.max_pic_data_without_header * 8} data_len + header {idk0})")
        for y in bytes_to_bin(a[::-1]):
            list1.append(y)
            if len(list1) == self.max_pixel_data:
                yield "".join(list1)
                list1 = []
        if list1:
            yield "".join(list1 + ["0" for y in range(self.max_pixel_data - len(list1))])

    def encode(self, data: bytes, cc: Tuple[int, ...]) -> Image:
        """
        for putting the data into the img
        if you want to save the img after this fkt you should save it in a format that is lossless else the decode fkt
        doesn't work\n
        :param data: data you want to save in the img
        :param cc: Tuple of bits you want to change exp: (1,1,1) for all the first bits, (69,0,0,0) for the
                   first, third and sevent bit in the first channel and no change in the 2, 3 and 4 channel
        :raises: SetCCError if the cc is wrong, EncodeICError if the img is too small for the data
        :return: a new Image obj
        """
        self.__set_cc(cc)
        header_bits, new_pic, pic_cords = self.__make_header_bits(len(data)), self.img_obj, self.__get_image_cords()
        org_img_data, i, pixels, data_lined = self.__get_changeable_data(), 0, new_pic.load(), self.__aline_data(data)
        for y in pic_cords:
            pixels[y] = self.__pe_encode(next(org_img_data), header_bits[i], use_static_cc=True)
            i += 1
            if i == len(header_bits):
                break
        else:
            raise EncodeICError("pic to small for the header sorry :(")
        for y in pic_cords:
            try:
                pixels[y] = self.__pe_encode(next(org_img_data), next(data_lined))
            except StopIteration:
                break
        else:
            raise EncodeICError("pic is to small sorry :(")
        return new_pic

    def decode(self) -> bytes:
        """
        decodes the img

        :raises: DecodeICError if the header of the file is wrong or too long
        :return: the bytes contained in the img
        """
        a, list1 = self.__get_changeable_data(), []
        cc, data_len = self.__read_header_bits(a)
        try:
            self.__set_cc(cc)
        except SetCCError:
            raise DecodeICError("the header of the file is wrong sorry :(")
        for y in a:
            list1.append(self.__pe_decode(y))
            if len(list1) * self.max_pixel_data >= data_len * 8:
                break
        else:
            raise DecodeICError("idk something went wrong sorry :( (header is wrong, the img is to small or I made a "
                                "mistake (most probably))")
        pic_data = "".join(list1)
        if len(pic_data) > data_len * 8:
            pic_data = pic_data[:data_len * 8]
        return int(pic_data, 2).to_bytes((len(pic_data) + 7) // 8, "little")

    def get_max_space(self, cc: Tuple[int, ...]) -> int:

        def idk0(a: int) -> int:
            a_bin = bin(a)[2:]
            return a_bin.count("1") * len(self.__header_bin_item_map["1"]) + a_bin.count(
                "0") * len(self.__header_bin_item_map["0"]) + len(self.__header_bin_item_map["end"])

        def data_fits(data_len: int) -> bool:
            header_len = (header_base_len + idk0(data_len)) // len(self.mode_edit) + 1
            idk1 = (data_len * 8) // bits_per_pixel_data + 1
            if header_len + idk1 <= total_pixels:
                return True
            return False

        bits_per_pixel_data = sum([bin(y)[2:].count("1") for y in cc])
        header_base_len = sum([idk0(y) for y in cc + tuple([0 for y in range(len(self.mode) - len(cc))])])
        total_pixels = self.img_obj.size[0] * self.img_obj.size[1] - 10  # the -10 is just for safety
        max_space_without_header = (bits_per_pixel_data * total_pixels) // 8
        for y in range(max_space_without_header, 0, -1):
            if data_fits(y):
                return y
        else:
            return 0
