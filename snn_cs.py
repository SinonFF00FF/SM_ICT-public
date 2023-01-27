import warnings
from typing import List, Dict, Optional, Any, Tuple, Generator
import snn_cry as cyp
import snn_grl as snng


# May God have mercy with whoever has to read this abomination


class EncodeCSWarning(Warning):
    def __init__(self, a: str):
        super().__init__(a)


class CS:
    def __init__(self):
        self.files: Dict[int, sub_file] = {}
        self.next_file_id = 0

    def __getitem__(self, item: int):
        return self.files[item]

    def __len__(self):
        return len(self.files)

    def __bool__(self):
        return bool(self.files)

    def __update_file_ids(self) -> None:
        for y in range(len(self.files)):
            if y not in self.files.keys():
                self.next_file_id = y
                break
        else:
            self.next_file_id = len(self)

    def append_items(self, items: List[Tuple[bytes, str, str, Optional[bytes]]]) -> None:
        """
        appends the CS obj \n
        :param items: tuple in form of (file_bytes, file_name, file_ext, key if you want to use one)
        """
        for y in items:
            self.append(y[0], y[1], y[2], y[3] if len(y) == 4 else None)

    def append(self, item: bytes, ext: str, name: str, key: Optional[bytes] = None) -> None:
        self.files[self.next_file_id] = sub_file().bob_the_builder(item, ext, name, key)
        self.__update_file_ids()

    def remove_items(self, item_ids: List[int]) -> None:
        for y in item_ids:
            self.remove(y)

    def remove(self, item_id: int) -> None:
        del self.files[item_id]
        self.__update_file_ids()

    def encode_sub_file(self, item_id: int, key: bytes) -> None:
        self[item_id].key, self[item_id].crypt = key, True

    def decode_sub_file(self, item_id: int, key: bytes) -> None:
        if self[item_id].contains_decoded is not None:
            self[item_id].decode_contains(key)
        else:
            self[item_id].crypt = False

    def from_bytes(self, a: bytes) -> None:
        while a:
            b = sub_file()
            a = b.from_bytes(a)
            self.files[self.next_file_id] = b
            self.__update_file_ids()

    def to_bytes(self, save_not_rdy_files: bool = False) -> bytes:
        out_bytes = b''
        for y0, y1 in self.files.items():
            a = False
            if sum([yy is None for yy in [y1.ext, y1.name, y1.contains]]):
                warnings.warn(f"item_id {y0} is not save rdy "
                              f"{'(it will be saved without ext and name)' if save_not_rdy_files else ''}",
                              EncodeCSWarning)
                if save_not_rdy_files:
                    a = True
                else:
                    continue
            out_bytes += y1.to_bytes(overwrite_name_ext=a)
        return out_bytes

    def get_item_info(self, item_id: int) -> Dict[str, Any]:
        a = self[item_id]
        name = a.name.decode("utf8") if a.name else None
        ext = a.ext.decode("utf8") if a.ext else None
        return {"full_name": name + ext if a.name and a.ext else None,
                "ext": ext, "name": name, "file": a.contains, "save_rdy": bool(a)}


class sub_file:
    __header_bin_item_map = {"0": "0", "1": "10", "end": "11"}

    # I know that with this map 0 will be overrepresented but rn idc (and I don't see a fix without making the header
    # * ~1.3 times as long, so I will just cry in my corner till I find a better solution or decide it's okay)

    def __init__(self):
        self.crypt = None  # will be a bool value
        self.key = None  # will be a bytes value
        self.contains = None  # same here
        self.name = None  # and here
        self.ext = None  # and here
        # only for decode stuff
        self.contains_decoded = None  # and here

    def __bool__(self):
        return False if self.contains is None else True

    def bob_the_builder(self, in_bytes: bytes, ext: str, name: str, key: Optional[bytes] = None):
        self.crypt = int(key is not None)
        self.contains = in_bytes
        self.ext = bytes(ext, encoding="utf8")
        self.key = key
        self.name = bytes(name, encoding="utf8")
        return self

    def from_bytes(self, a: bytes, key: Optional[bytes] = None) -> bytes:
        """ returns the bytes that are not used for this file """
        b = (y for y in a)
        data_len, self.crypt = self.__read_header(b, 2)
        self.contains_decoded = bytes([next(b) for y in range(data_len)])
        if (self.crypt and key) or not self.crypt:
            self.decode_contains(key)
        return bytes([y for y in b])

    def decode_contains(self, key: Optional[bytes] = None) -> None:
        if self.crypt:
            b, self.key = cyp.snn_crypt_sym.decode(self.contains_decoded, key, True), key
        a = (y for y in (b if self.crypt else self.contains_decoded))
        self.ext, self.name = [y.to_bytes((y.bit_length() + 7) // 8, "little") for y in self.__read_header(a, 2)]
        self.contains = bytes([y for y in a])

    def to_bytes(self, overwrite_name_ext: bool = False) -> bytes:
        c = self.contains_decoded if overwrite_name_ext else self.contains
        if c is None:
            raise ValueError("this obj is empty")  # should never happen if you use IC fkts
        d = self.__make_header([int.from_bytes(y, "little") for y in (
            ["", ""] if overwrite_name_ext else [self.ext, self.name])])
        return self.__make_header([len(c) + len(d), self.crypt]) + (
            cyp.snn_crypt_sym.encode(d + c, self.key, True) if self.crypt else d + c)

    @staticmethod
    def __make_header(a: List[int]) -> bytes:
        list1 = []
        for y in a:
            for yy in bin(y)[2:]:
                list1.append(sub_file.__header_bin_item_map[yy])
            list1.append(sub_file.__header_bin_item_map["end"])
        c = (sum([len(y) for y in list1]) + 7) // 8
        return int(snng.make_set_len("".join(list1), c, side="right"), 2).to_bytes(c, "big")

    @staticmethod
    def __read_header(a: Generator[int, None, None], lenlen: int) -> List[int]:
        list1, list2, c = [], [], ""
        for y in a:
            b = snng.make_set_len(bin(y)[2:], 8)
            for yy in b:
                c += yy
                if c in sub_file.__header_bin_item_map.values():
                    if c == sub_file.__header_bin_item_map["end"]:
                        list2.append(int("".join(list1), 2))
                        list1 = []
                        if len(list2) == lenlen:
                            return list2
                    else:
                        list1.append(snng.get_key(c, sub_file.__header_bin_item_map))
                    c = ""
        else:
            raise ValueError("idk something went wrong")
