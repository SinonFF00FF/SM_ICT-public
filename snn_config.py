from typing import Dict, Tuple
import io
import os


class config:
    sep_char = ":"

    """ dont use sep_char in the keys or items of config_dict 
    if you use setitem, append or remove you need to update the config with write_config else the changes wont be 
    saved"""

    def __init__(self, config_dict: Dict[str, str],  sep_char_overwrite: str = None):
        self.sep = self.sep_char if sep_char_overwrite is None else sep_char_overwrite
        self.contains = config_dict

    def __getitem__(self, item):
        return self.contains[item]

    def __setitem__(self, key, value):
        self.contains[key] = value

    def append(self, key: str, value: str):
        self.contains[key] = value

    def remove(self, key: str):
        del self.contains[key]

    def read_config_str(self, a: str):
        b, self.contains = 0, {}
        for iy, y in enumerate(a):
            if y == "\n":
                c = a[b:iy].split(self.sep)
                if len(c) > 2:
                    raise ValueError(f"wrong sep_char ({c})")
                self.contains[c[0]] = c[1]
                b = iy + 1
        return self

    def write_config_str(self):
        return "".join([f"{y0}{self.sep}{y1}\n" for y0, y1 in self.contains.items()])


class config_byte(config):
    def __init__(self, config_dict: Dict[str, str] = None, sep_char_overwrite: str = None):
        super().__init__(sep_char_overwrite=sep_char_overwrite,
                         config_dict={} if config_dict is None else config_dict)

    def write_config(self) -> bytes:
        return bytes(self.write_config_str(), encoding="utf8")

    def read_config(self, a: bytes):
        return self.read_config_str(a.decode(encoding="utf8"))


class config_file(config):
    default_config_path = "config.txt"

    def __init__(self, config_dict: Dict[str, str] = None, path_overwrite: str = None, sep_char_overwrite: str = None):
        super().__init__(sep_char_overwrite=sep_char_overwrite,
                         config_dict={} if config_dict is None else config_dict)
        self.path = os.getcwd() + rf"\{self.default_config_path if path_overwrite is None else path_overwrite}"

    def read_config(self):
        with io.open(self.path, "r", encoding="utf8") as f:
            return self.read_config_str(f.read())

    def write_config(self):
        with io.open(self.path, "w", encoding="utf8") as f:
            f.write(self.write_config_str())
