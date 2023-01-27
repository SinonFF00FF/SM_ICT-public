from typing import List, Generator, Optional
import copy
import snn_grl as snng
from math import sqrt


# May God have mercy with whoever has to read this abomination

class snn_hash_grid:
    class hash_grid_base:
        def __init__(self, in_list: List[int], size: int):
            if len(in_list) > size ** 2:
                raise ValueError(f"input is to big ({len(in_list)} > {size ** 2})")
            self.xor_list, self.list_array, self.size, i, list1 = [], [], size, 0, []
            for y in range(size ** 2):
                a = in_list[i]
                i += 1
                if i == len(in_list):
                    i = 0
                list1.append(a)
                if len(list1) == size:
                    self.list_array.append(list1)
                    self.xor_list += list1
                    list1 = []

        def show_gitter(self, highlight_list: List[int] = None, show_all_prob: bool = False,
                        show_xor_list: bool = False) -> None:
            """ just for debug stuff """
            print("start", "-" * 50, self, "-" * 50)
            if highlight_list is None:
                highlight_list = [0]
            a, b, c, idk0, max_str_len = [], [], [], len(str(self.size)), 0
            for y in self.list_array:
                for yy in y:
                    a.append(yy)
            for y in a:
                if not (y in b):
                    b.append(y)
                    c.append(a.count(y))
                    d = len(str(y))
                    if d > max_str_len:
                        max_str_len = d

            def color_text(text: str, b_code=0, s_code=0, t_code=0):
                a_c = ""
                for yyyy in [b_code, s_code, t_code]:
                    a_c += "\33[{code}m".format(code=yyyy)
                return a_c + text

            def make_set_len(text: str, lenlen: int, fill_str: str = " "):
                return fill_str * (lenlen - len(text)) + text

            print(f"size: {self.size, self.size}")
            print(f"total slots: {len(a)}")
            print(f"div items: {sorted(b, reverse=True)}")
            print(f"total div items: {len(b)}")
            if show_xor_list:
                print(f"xor_list: {self.xor_list}")
            i, max_shown = 0, 20
            if show_all_prob:
                max_shown = 256
            print(f"\n{max_shown} most used items (count x item):")
            for iy, y in enumerate(sorted(list(zip(b, c)), key=lambda g: g[1], reverse=True)):
                i += 1
                end = " "
                if i % 5 == 0 and i != max_shown:
                    end = " |\n"
                e, f = make_set_len(str(y[1]), max_str_len), make_set_len(str(y[0]), max_str_len, "0")
                print(f"| #{make_set_len(str(iy), idk0 + 1, fill_str='0')}: {e}x'{f}'", end=end)
                if i == max_shown:
                    break
            print(f"|\n\n{'-' * (idk0 + 1)}|", "-" * (self.size * 3 + 1 + self.size * max_str_len), "|", sep="")
            for iy, y in enumerate(self.list_array):
                print(f"{make_set_len(str(iy), idk0)} |", end="", sep="")
                for yy in y:
                    if yy in highlight_list:
                        print(" ", color_text(make_set_len(str(yy), max_str_len, '0'), 97, 0, 35), end=" ")
                    else:
                        print(" ", color_text(make_set_len(str(yy), max_str_len, '0'), 0, 0, 0), end=" ")
                print(" ", color_text("|", 0, 0, 0), end="", sep="")
                print(f"\n{'-' * (idk0 + 1)}|", "-" * (self.size * 3 + 1 + self.size * max_str_len), "|", sep="")
            print("end", "-" * 52, self, "-" * 50)

        def rotate(self, dct: str) -> None:
            """
            rotates the grid \n
            :param dct: cw or ccw
            """
            dct = {"ccw": 1, "cw": -1}.get(dct)
            if not dct:
                raise ValueError(f"wrong dct (dcts: 'ccw', 'cw')")
            a, list1, list2 = [y for y in self.list_array[::dct]], [], []
            for y in range(self.size):
                b = [c[y] for c in a]
                list1.append(b)
                list2 += b[::-dct]
            self.list_array = list1[::-dct]
            self.xor_list = list2[::-dct]

        def line_swap(self, dct: str, count: int) -> None:
            if not (dct in ["x", "y"]):
                raise ValueError(f"wrong dct (dcts: 'x', 'y')")
            if not count % self.size:
                raise Exception("you will not change the grid")
            if dct == "y":
                self.list_array = self.list_array[count:] + self.list_array[:count]
            else:
                for iy, y in enumerate(list(self.list_array)):
                    self.list_array[iy] = y[count:] + y[:count]
            list1 = []
            for y0 in self.list_array:
                for y1 in y0:
                    list1.append(y1)
            self.xor_list = list1

        def item_swap(self) -> None:
            """ just swaps the items around """
            size_sqt = self.size ** 2
            a = [0] * size_sqt
            for y in self.xor_list:
                if y:
                    b = y % size_sqt
                    for yy in range(size_sqt):
                        if not a[(b + yy) % size_sqt]:
                            a[(b + yy) % size_sqt] = y
                            break
                    else:
                        raise Exception("idk something went wrong")
            self.xor_list, list1, self.list_array = a, [], []
            for y in self.xor_list:
                list1.append(y)
                if len(list1) == self.size:
                    self.list_array.append(list1)
                    list1 = []

        def xor(self, other) -> None:
            """
            xor with other hash_grid obj \n
            :param other: hash_grid obj
            """
            if self.size != other.size:
                raise ValueError("both grids must be the same size")
            a = snn_hash_grid.hash_grid_base([y0 ^ y1 for y0, y1 in zip(self.xor_list, other.xor_list)], size=self.size)
            self.list_array = a.list_array
            self.xor_list = a.xor_list

        def __getitem__(self, item: int):
            return self.xor_list[item]

    class hash_gird_bin(hash_grid_base):
        def __init__(self, size: int, in_bytes: bytes, fill_0: bool):
            in_bin = bin(int.from_bytes(in_bytes, "little"))[2:]
            if fill_0:
                in_bin += "0" * (size ** 2 - len(in_bin))
            super().__init__(in_list=[int(y) for y in in_bin], size=size)

        def to_bytes(self) -> bytes:
            # ig self.size % 4 works but if you get an Overflow error here change it + % 8 or to perma +1
            return int("".join([str(y) for y in self.xor_list]), 2).to_bytes((self.size ** 2) // 8 + (
                1 if self.size % 4 else 0), "little")

    class hash_grid_bytes(hash_grid_base):
        def __init__(self, size: int, in_bytes: bytes, fill_0: bool):
            if fill_0:
                in_bytes += bytes([0] * (size ** 2 - len(in_bytes)))
            super().__init__(in_list=[y for y in in_bytes], size=size)

        def to_bytes(self) -> bytes:
            return bytes(self.xor_list)

    class LowLoopError(Exception):
        def __init__(self, message: str):
            super().__init__(message)

    @staticmethod
    def hash_final(in_bytes: bytes, size: int, mode: str, **kwargs) -> bytes:
        """
        generates hash value of in_bytes \n
        :param mode: bin or bytes
        :param in_bytes: idk
        :param size: size of the grid  size**2 will be the output len in bytes/bin
        :return: hash value of in_bytes
        """

        """
        not the best fkt but idk it will be okay ig
        stuff that is bad:
        - if the input loops the output will be the same as if the input didn't if len(input) % size**2 == 0
         (hash('6969', 4) == hash('69', 4)) (fixed)
        - the number of possible input is greater than the number of possible outputs 
        - the bytes within the output will always be <= 2**(max(in_bytes).bit_length()) so it you use an ascii str
        you will never have bytes >= 127 (fixed in bin mode)
        - is slow
        - item_swap doesn't do much if in bin mode
        ...
        idk ig there is a lot more but iam tired and don't have the motivation to work on this rn 
        maybe I will fix some stuff in the future but not now 
        """

        kwargs_dict = {"loops": len(in_bytes), "fill_0": False, "bytes_loop_mul": 1, "bin_loop_mul": 2,
                       "low_loop_trigger": 10}
        kwargs_dict = snng.kwargs_handler(kwargs, kwargs_dict, True)
        if mode == "bytes":  # if you want to change the keywords bin/bytes change the x_loop_mul names too
            a = snn_hash_grid.hash_grid_bytes(in_bytes=in_bytes, size=size, fill_0=kwargs_dict["fill_0"])
        elif mode == "bin":
            a = snn_hash_grid.hash_gird_bin(in_bytes=in_bytes, size=size, fill_0=kwargs_dict["fill_0"])
        else:
            raise ValueError(f"wrong mode: {mode} (should be bytes or bin)")
        loops = int(kwargs_dict["loops"] * kwargs_dict[f"{mode}_loop_mul"])
        if loops < kwargs_dict["low_loop_trigger"]:
            raise snn_hash_grid.LowLoopError(f"no enough loops/in_bytes to small (loops: {loops}"
                                             f" error trigger: {kwargs_dict['low_loop_trigger']})")
        for y in range(loops):
            b = copy.deepcopy(a)
            b.item_swap()
            b.line_swap("x", 1)
            b.line_swap("y", 1)
            b.rotate("ccw")
            b.xor(a)
            a = b
        return a.to_bytes()


class snn_crypt_sym:
    """ one time pat class """

    class PossibleInfiniteLoopError(Exception):
        def __init__(self, message: str):
            super().__init__(message)

    class snn_lsg:
        """ random number generator class"""

        """ 
        some bad things about this generator:
        - same number can max appear self.list_mult times in a rowe 
        - is slow (after some testing I think its not that bad but jk my code is always slow
        ...
        idk I think that there is a lot more of bad things but those are the ones that I can think of rn
        """

        kwarg_dict = {"pre_gen_overwrite": 10, "max_number_overwrite": 256, "list_len_multiplayer_overwrite": 20}

        class fancy_list(list):
            def __init__(self, list_in: Optional[list] = None):
                super().__init__([] if list_in is None else list_in)

            def gen_random_item(self, index: int):
                a = self[index]
                del self[index]
                self.append(a)
                return a

        def __init__(self, seed: bytes, **kwargs):
            pre_gen, self.max_number, self.list_mult = snng.kwargs_handler(kwargs, self.kwarg_dict, True).values()
            self.seed, self.pre_gen = seed, 1
            self.a, self.b, self.m = self.__make_abm()
            c = self.__gen_number()
            for y in range(pre_gen):  # idk if there is a better way to do this, but I don't want to search hours just
                next(c)               # to save one line of code
            self.pre_gen, self.fancy_list_obj = next(c), self.__make_fancy_list()

        def __make_abm(self) -> List[int]:
            a, b = [2, (len(self.seed) * 8) // 2], bin(int.from_bytes(self.seed, "little"))
            c = [int(b[y0: y1], 2) for y0, y1 in zip(a, a[1:] + [len(b)])]
            if not c[1]:
                raise snn_crypt_sym.PossibleInfiniteLoopError("idk bad seed ig")
            return c + [c[0] + c[1]]

        def __make_fancy_list(self):
            b, c = self.fancy_list([None] * self.max_number * self.list_mult), self.__gen_number()
            for iy, y in enumerate([y % self.max_number for y in range(self.max_number * self.list_mult)]):
                new_index = next(c) % (self.max_number * self.list_mult - iy)
                while b[new_index] is not None:
                    new_index = (new_index + 1) % (self.max_number * self.list_mult)
                b[new_index] = y
            return b

        def __gen_number(self) -> Generator[int, None, None]:
            while True:
                self.pre_gen = (self.a * self.pre_gen + self.b) % self.m
                yield self.pre_gen

        def get_random_number(self) -> Generator[int, None, None]:
            for y in self.__gen_number():
                yield self.fancy_list_obj.gen_random_item(y % self.max_number)

    @staticmethod
    def __make_key(key: bytes, hashing_key: bool):
        return snn_crypt_sym.snn_lsg(
            snn_hash_grid.hash_final(key, 1 + int(sqrt(len(key) * 8)), "bin") if hashing_key else key)

    @staticmethod
    def encode(in_bytes: bytes, key: bytes, hashing_key: bool = True) -> bytes:
        """
        encoding fkt \n
        :param hashing_key: idk
        :param in_bytes: any bytes
        :param key: any bytes
        :return: encoded bytes
        """
        return bytes([(y0 + y1) % 256 for y0, y1 in zip(
            in_bytes, snn_crypt_sym.__make_key(key, hashing_key).get_random_number())])

    @staticmethod
    def decode(in_bytes: bytes, key: bytes, hashing_key: bool = True) -> bytes:
        """
        decoding fkt \n
        :param hashing_key: idk
        :param in_bytes: any bytes
        :param key: any bytes
        :return: decoded bytes
        """
        return bytes([(y0 - y1) % 256 for y0, y1 in zip(
            in_bytes, snn_crypt_sym.__make_key(key, hashing_key).get_random_number())])


class snn_crypt_asym:
    pass
