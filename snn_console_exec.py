import traceback
import warnings
from typing import Tuple, List, Union, Optional, Dict
import snn_config as snn_co
import snn_cs
import snn_picc
import sys
import io
import os
import time
import inspect
from PIL import Image
from datetime import datetime


# May God have mercy with whoever has to read this abomination

class Var:
    pw_cs_obj: snn_cs.CS = None
    pw_key = None
    pw_dict: snn_co.config_byte = None
    config_dict: snn_co.config_file = None
    okay_ext_open_container = [".snnc2"]
    okay_ext_open_image = [".png", ".jpeg", ".jpg", ".webp"]
    okay_ext_save_image = [".png"]
    current_snn_cs_obj: snn_cs.CS = None
    current_snn_picc_obj: snn_picc.IC = None
    dirs_config_dict: snn_co.config_file = None
    cc_config_dict: snn_co.config_file = None

    dir_file_edit = False
    pw_file_edit = False
    cc_file_edit = False

    @classmethod
    def make_snn_cs_obj(cls) -> snn_cs.CS:
        if cls.current_snn_cs_obj is None:
            cls.current_snn_cs_obj = snn_cs.CS()
        return cls.current_snn_cs_obj

    @classmethod
    def __make_pw_cs_obj(cls) -> snn_cs.CS:
        if cls.pw_cs_obj is None:
            a, cls.pw_cs_obj = os.path.join(os.getcwd(), cls.config_dict["save_pw_path"]), snn_cs.CS()
            if os.path.isfile(a):
                if cls.pw_key is None:
                    cls.pw_key = input_handler("pls give pw_file_key >< > ")["fkt"]
                with io.open(a, "rb") as f:
                    cls.pw_cs_obj.from_bytes(f.read())
                try:
                    cls.pw_cs_obj.decode_sub_file(0, bytes(cls.pw_key, encoding="utf8"))
                except ValueError:
                    error_message("key seems to be wrong")
                    cls.pw_key = None
                else:
                    return cls.pw_cs_obj
            cls.pw_cs_obj = snn_cs.CS()
        return cls.pw_cs_obj

    @classmethod
    def make_pw_file(cls) -> snn_co.config_byte:
        if cls.pw_dict is None:
            a = cls.__make_pw_cs_obj()
            if a:
                cls.pw_dict = snn_co.config_byte().read_config(a.get_item_info(0)["file"])
            else:
                cls.pw_dict = snn_co.config_byte()
        return cls.pw_dict

    @classmethod
    def make_dir_file(cls) -> snn_co.config_file:
        if cls.dirs_config_dict is None:
            cls.dirs_config_dict = snn_co.config_file(path_overwrite=cls.config_dict["saved_dirs_path"],
                                                      sep_char_overwrite="?").read_config()
        return cls.dirs_config_dict

    @classmethod
    def make_cc_file(cls) -> snn_co.config_file:
        if cls.cc_config_dict is None:
            cls.cc_config_dict = snn_co.config_file(path_overwrite=cls.config_dict["saved_ccs_path"])
        return cls.cc_config_dict


def input_handler(show_str: Optional[str] = None) -> Dict[str, Union[str, List[str]]]:
    """returns the edited input if no args are given the val list in the output is empty"""
    if show_str is None:
        if config_check("show_input_time"):
            show_str = f"\n{datetime.now().strftime('%X')} >> "
        else:
            show_str = "\n >> "
    list1, b, c, a = [], "", 0, input(show_str) + Var.config_dict["sep_input_char"]
    for iy, y in enumerate(a):
        if y == Var.config_dict["sep_input_char"] and c == 0:
            list1.append(b)
            b = ""
        elif y == Var.config_dict["sep_input_char_alt0"]:
            c += 1
            if c > 1:
                b += y
        elif y == Var.config_dict["sep_input_char_alt1"]:
            if c > 1:
                b += y
            c -= 1
        else:
            b += y
    return {"fkt": list1[0], "val": list1[1:]}


def item_id_check(a: str) -> bool:
    """put this in a block like this:
    if item_id_check(item_id): return
    """
    b = a.isnumeric()
    if not b:
        print("item_id should be a number in base 10")
    return not b


def config_check(a: Optional[str] = "show_debug_stuff") -> bool:
    if Var.config_dict[a] == "True":
        return True
    if not (Var.config_dict[a] == "False"):
        print(f"Warning: config entry {a} is wrong. It will be read as False")
    return False


def error_message(a: Optional[str] = ""):
    print(a)
    if config_check("show_debug_stuff"):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"-- debug stuff: {str(exc_type)[8:-2]}: {exc_obj} --")
        print("-" * 75)
        for y in traceback.extract_tb(exc_tb):
            print(f"-- {str(y)[14:-1]} --")


def pw_handler(a: str) -> str:
    if (a in Var.make_pw_file().contains.keys()) and config_check("use_saved_pw"):
        return Var.pw_dict[a]
    return a


def path_input_handler(a: str) -> str:
    if config_check("use_saved_dirs"):
        if a in Var.make_dir_file().contains.keys():
            if input_handler(f"do you want to use {Var.dirs_config_dict[a]} as input? (Y/n) > ")["fkt"] == "Y":
                return Var.dirs_config_dict[a]
        else:
            b, Var.dir_file_edit = len(Var.make_dir_file().contains), True
            Var.dirs_config_dict.append(f"P{b}", a)
            print(f"{a} was saved as path P{b}")
    return a


def on_close():
    if config_check("use_saved_dirs") and Var.dir_file_edit:
        Var.make_dir_file().write_config()
        print(f"dir_file was saved as {Var.make_dir_file().path}")
    if config_check("use_saved_pw") and Var.pw_file_edit:
        callable_fkt.save_pws()
    if config_check("use_saved_ccs") and Var.cc_file_edit:
        Var.make_cc_file().write_config()
        print(f"cc_file was saved as {Var.make_cc_file().path}")


def on_start():
    if not os.path.isfile(os.path.join(os.getcwd(), snn_co.config_file.default_config_path)):
        dcd = {'save_pw_path': 'saved_pws.snnc2', 'sep_input_char': ' ', 'sep_input_char_alt0': '(',
               'sep_input_char_alt1': ')', 'show_debug_stuff': 'True', 'show_input_time': 'True',
               'show_output_time': 'False', 'use_saved_pw': 'True', 'saved_dirs_path': 'saved_dirs.txt',
               'use_saved_dirs': 'True', 'use_saved_ccs': 'True', "saved_ccs_path": "saved_ccs.txt"}
        snn_co.config_file(dcd).write_config()
        print("config file was created")
    Var.config_dict = snn_co.config_file().read_config()
    warnings.simplefilter("error", Image.DecompressionBombWarning)
    warnings.simplefilter("always", snn_cs.EncodeCSWarning)
    global our_discord, fight_club_fkts  # ik this is bad, but it looks better this way, so it stays
    our_discord = "add a Name pls Sinon"  # edit later pls pls pls pls pls pls
    fight_club_fkts = ["sum", "exec"
                       ] + [y for y in callable_fkt.__dict__ if ("funfact" in y) and callable(getattr(callable_fkt, y))]


def make_cc(a: str) -> Tuple[int, ...]:
    """'a' should look like 1, 42, 69, ..."""
    list1, b, a = [], 0, cc_input_handler(a)
    for iy, y in enumerate(a + ","):
        if y == ",":
            list1.append(int(a[b:iy].replace(" ", "")))
            b = iy + 1
    return tuple(list1)


def cc_input_handler(a: str) -> str:
    if config_check("use_saved_ccs"):
        if a in Var.make_cc_file().contains.keys():
            if input_handler(f"do you want to use {Var.cc_config_dict[a]} as input? (Y/n) > ")["fkt"] == "Y":
                return Var.cc_config_dict[a]
        else:
            b, Var.cc_file_edit = len(Var.make_cc_file().contains), True
            Var.cc_config_dict.append(f"C{b}", a)
            print(f"{a} was saved as path C{b}")
    return a


class callable_fkt:
    """class of fkt you can call in the program, all fkt need to be static, need to except str inputs and
     can't have kwargs  (all protected or private fkts cant be called (everything with '_' as the first char))"""
    """its just a little less ugly than do this stuff with a big if block 
    (but still ugly but idk how to do it better rn and I think I will stick to this method of doing it)"""

    @staticmethod
    def funfact1():
        """the first fight club fkt ^^"""
        print("Sinon and FF00FF are the same person just some neet that enjoys writing code")

    @staticmethod
    def funfact2():
        """the second fight club fkt ^^"""
        print("nobody likes people that like python or pineapple pizza ...")
        time.sleep(0.5)
        print("maybe that is the reason why I/we dont have friends")

    @staticmethod
    def funfact3():
        """the third fight club fkt ^^"""
        print("I dont think that anybody will ever read this shit so I can keep writing this stuff() "
              "(I/we definitely dont do this funfact bs because I/we have no clue how to write okay fkts)")

    @staticmethod
    def funfact4():
        """the 4th fight club fkt ^^"""
        print("I really hope I will delete this ship before I/we make this thing public")
        time.sleep(0.5)
        print("maybe some shit posting will lower the pain somebody will feel if he/she reads this super nice written "
              "code \n(maybe it will be much bigger because of this idk idc rn)")

    @staticmethod
    def funfact5():
        """the 5th fight club fkt ^^"""
        print("to this point this console stuff is way better to write than some tkinter bs (I really dont like to"
              "write UIs and except the fact that I dont find a way to use some file dialog that works without tkinter"
              "all works fine till now)")

    @staticmethod
    def sum(*args):
        """just some testing stuff delete later"""
        a = 0
        for y in args:
            a += int(y)
        print(f"{'+'.join(args)}={a}")

    @staticmethod
    def exec(a: str):
        """just for testing delete late"""
        exec(a)

    """ the real fkts start now yay """

    @staticmethod
    def help():
        """shows all fkts you can use in form of 'name:...\n args:...\n  doc:...'"""
        for y in dir(callable_fkt):
            if callable(getattr(callable_fkt, y)) and y[0] != "_" and not (y in fight_club_fkts):
                print("-" * 50)
                a = getattr(callable_fkt, y)
                b = str(inspect.signature(a))[1:-1]
                print(f"{y}:")
                if b:
                    print(f"args: {b}")
                print(f"doc: {a.__doc__}")

    @staticmethod
    def info(a: Optional[str] = None):
        """shows some general help"""
        if a is None:
            print("your input should look like this: fkt-name arg1 arg2 ...\n"
                  "the arg seperator is a space. if you want to use spaces in an arg you can put () around it.\n"
                  "(...) in an arg will be ignored (exp: (random arg(1)) will be read as 'random arg(1)')\n"
                  "if you want to change those seperator chars you can change them in the config.txt file\n"
                  "P.S. you should use \ in your paths and filenames and not / \n")
            print(f"if you have any problems or questions you can contact us at Discord: {our_discord}")
        elif a == "picc":
            print("pls add some stuff Sinon (snn_picc)")  # add stuff pls pls pls pls pls pls pls pls pls pls pls pls
            print("list of all supported formats:"
                  " https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html"
                  " (I didn't test all but I think all formats that are not animated should work)")
        elif a == "cs":
            print("pls add some stuff Sinon (snn_cs)")  # add stuff pls pls pls pls pls pls pls pls pls pls pls pls pls
        else:
            print("wrong arg sorry ><")

    @staticmethod
    def reread_config():
        """call it if you have changed something in the config.txt file (or restart the program)"""
        Var.config_dict = snn_co.config_file().read_config()
        print("new config file:\n")
        for y in Var.config_dict.contains:
            print(f"{y}: '{Var.config_dict[y]}'")

    @staticmethod
    def quit():
        """closes the program"""
        print("Goodbye and have a nice one (also thx for using this program)")
        time.sleep(0.5)
        sys.exit()

    @staticmethod
    def close_all():
        """closes the current snn_cs, snn_picc obj and all files that are opened rn"""
        Var.current_snn_picc_obj, Var.current_snn_cs_obj = None, None

    """start of the snn_cs fkts (except one (kinda))"""

    @staticmethod
    def add_file(file_path: str, key: str = None):
        """adds a file to the current cs file (key should be longer than 15 chars if you use one)"""
        try:
            with io.open(path_input_handler(file_path), "rb") as f:
                a, b = f.read(), str(f).split("\\")[-1][:-2].split(".")  # maybe change the \\ to also split at /
        except OSError:
            error_message(f"{file_path} can not be opened (wrong file path or no permission)")
        else:
            Var.make_snn_cs_obj().append(item=a, ext="." + b[1], name=b[0],
                                         key=None if key is None else bytes(pw_handler(key), encoding="utf8"))

    @staticmethod
    def show_cs_info():
        """shows some info about the current cs obj"""
        if Var.current_snn_cs_obj is None or not Var.current_snn_cs_obj:
            print("empty obj")
        else:
            for iy, y in enumerate(Var.current_snn_cs_obj.files.keys()):
                a = Var.current_snn_cs_obj[y]
                print(f"{'-' * 20}<file:{iy}>{'-' * 20}")
                print(f"file id: {y}, name: {a.name}, ext: {a.ext}, is encrypted: {bool(a.crypt)}")
                print(f"size: {f'{len(a.contains)} bytes' if a.contains else 'not encoded jet'}",
                      end=", " if a.crypt else "\n")
                if a.crypt:
                    print(f"key used: {a.key if a.key else 'not encoded jet'}")

    @staticmethod
    def remove_file(item_id: str):
        """removes the file from the snn_cs obj (item id should be a number in base 10)"""
        if item_id_check(item_id): return
        try:
            Var.make_snn_cs_obj().remove(int(item_id))
        except KeyError:
            error_message("wrong item_id" if Var.current_snn_cs_obj else "the obj is empty")

    @staticmethod
    def save_cs_file(file_path: str, save_not_rdy_files: Optional[str] = None):
        """saves the currently opened snn_cs file to a snnc2 file
        (if you want to save it with another ext type the full path with ext in it)"""
        file_path = path_input_handler(file_path)
        a = file_path.split(".")
        if os.path.isfile(file_path) or os.path.isfile(file_path + ".snnc2"):
            if not (input_handler("this file already exists do you want to replace it? (Y/n) > ")["fkt"] == "Y"):
                return
        elif (not (a[0] == file_path)) and (a[1] != ".snnc2"):
            if not (input_handler(f"your path already has an ext do you want to save it as an {a[1]}"
                                  f" file else it will be saved as an .snnc2 file (Y/n) > ")["fkt"] == "Y"):
                file_path = a[0] + ".snnc2"
        else:
            file_path += ".snnc2"
        try:
            with io.open(file_path, "wb") as f:
                f.write(Var.current_snn_cs_obj.to_bytes(save_not_rdy_files=save_not_rdy_files == "True"))
        except OSError:
            error_message(f"{file_path} can not be opened (wrong file path or no permission)")
        except ValueError:
            error_message(f"{file_path} can not be saved (encode error)")

    @staticmethod
    def open_file(file_path: str):
        """opens a snnc2 or Image file (or other files if you want)"""
        file_path = path_input_handler(file_path)
        file_ext, is_c, is_i = os.path.splitext(file_path)[1], False, False
        if not (file_ext in Var.okay_ext_open_image + Var.okay_ext_open_container):
            if input_handler("the format is an format you cant normally open"
                             " do you want to open it anyway? (Y/n) > ")["fkt"] == "Y":
                b = input_handler("do you want it to open as a Image or a snnc2 container? (I/C) > ")["fkt"]
                if b == "I":
                    is_i = True
                elif b == "C":
                    is_c = True
                else:
                    print("wrong input try again")
                    return
            else:
                return
        try:
            if file_ext in Var.okay_ext_open_container or is_c:
                with io.open(file_path, "rb") as f:
                    a = f.read()
                Var.make_snn_cs_obj().from_bytes(a)
            elif file_ext in Var.okay_ext_open_image or is_i:
                for y in range(2):
                    try:
                        d = Image.open(file_path)
                        if y:
                            Image.MAX_IMAGE_PIXELS = idk0
                    except Image.DecompressionBombWarning:
                        error_message("this file is to big to open it")
                        if input_handler("do you want to disable the Error and decode the file regardless of that?"
                                         " (Y/n)")["fkt"] == "Y" and not y:
                            print("happy system crashing :)")
                            idk0 = Image.MAX_IMAGE_PIXELS
                            Image.MAX_IMAGE_PIXELS = None
                            continue
                        else:
                            return
                    else:
                        try:
                            Var.current_snn_picc_obj = snn_picc.IC(d)
                        except snn_picc.BuildICError:
                            error_message("animated Images are not supported sorry :(")
                            return
                        break
                else:
                    print("idk something went wrong sorry")
                    return
            else:
                print("idk something went wrong (sorry I never thought that you need to see this message "
                      "... really big sorry :( :( :( )")
                if config_check():
                    print("Iam not really smart really big sorry that I overlooked smth sorry :("
                          "the problem might be in the list of okay ext's or in the lines above this if block")
                return
        except OSError:
            error_message(f"{file_path} can not be opened (wrong file path or no permission)")
        except ValueError:
            error_message(f"{file_path} can not be opened (decode error)")

    @staticmethod
    def encode_cs(item_id: str, key: str):
        """adds a key to the snn_cs.subfile"""
        if item_id_check(item_id): return
        try:
            Var.current_snn_cs_obj.encode_sub_file(item_id=int(item_id), key=bytes(pw_handler(key), encoding="utf8"))
        except KeyError:
            error_message("wrong item_id" if Var.current_snn_cs_obj else "the obj is empty")

    @staticmethod
    def decode_cs(item_id: str, key: str):
        """decodes a snn_cs.subfile (you can not really tell if the key is right so if the header contains some
        name and ext this fkt will pass)"""
        if item_id_check(item_id): return
        try:
            Var.current_snn_cs_obj.decode_sub_file(item_id=int(item_id), key=bytes(pw_handler(key), encoding="utf8"))
        except KeyError:
            error_message("wrong item_id" if Var.current_snn_cs_obj else "the obj is empty")
        except ValueError:
            error_message("seems to be the wrong key (or I did some mistake and fucked up)")
        else:
            if config_check():
                a = Var.current_snn_cs_obj[int(item_id)]
                print(f"smth about the new file:\n"
                      f"name: {a.name}, ext: {a.ext}, size: {len(a.contains)} bytes")
                if input_handler("show contain bytes? (Y/n) > ")["fkt"] == "Y":
                    print(f"contains:\n{a.contains}")

    @staticmethod
    def save_cs(file_path: str, item_id: Optional[str] = None):
        """saves the subfiles inside the snn_cs file"""
        file_path = path_input_handler(file_path)
        if not os.path.isdir(file_path):
            print("this path doesnt exist")
            return
        if item_id is not None:
            if item_id_check(item_id): return
            b = [int(item_id)]
        else:
            b = Var.current_snn_cs_obj.files.keys()
        for y in b:
            try:
                try:
                    a = Var.current_snn_cs_obj.get_item_info(y)
                    if a["full_name"] is None or not a["save_rdy"]:
                        raise ValueError("file is not save_rdy")
                except UnicodeDecodeError as e:
                    raise ValueError(f"UnicodeDecodeError: {e}")
            except ValueError:
                error_message(f"file with item_id {y} cannot be saved (wrong name and/or ext)")
                continue
            c = os.path.join(file_path, a["full_name"])
            if os.path.isfile(c):
                if not (input_handler("this file already exits do you want to overwrite it (Y/n) > ")["fkt"] == "Y"):
                    i, c = 1, os.path.join(file_path, f"{a['name']}({1}){a['ext']}")
                    while os.path.isfile(c):
                        i += 1
                        c = os.path.join(file_path, a["name"] + f"({i}){a['ext']}")
            try:
                with io.open(c, "wb") as f:
                    f.write(a["file"])
                print(f"file saved as: {c}")
            except OSError:
                error_message(f"{a['full_name']} can not be saved")

    """pw stuff start"""

    @staticmethod
    def save_pws(new_pw: Optional[str] = None):
        """saves the pws to the pw_file"""
        if not Var.pw_key and new_pw is None:
            print("you didn't change anything at the file why you wanna save it")
            return
        a = snn_cs.CS()
        a.append(Var.make_pw_file().write_config(), "", "",
                 bytes(Var.pw_key if new_pw is None else new_pw, encoding="utf8"))
        try:
            b = os.path.join(os.getcwd(), Var.config_dict["save_pw_path"])
            with io.open(b, "wb") as f:
                f.write(a.to_bytes())
            print(f"pw_file was saved as {b}")
            if new_pw is not None:
                Var.pw_key = new_pw
        except UnicodeDecodeError:
            error_message("idk something went wrong")

    @staticmethod
    def add_pw(pw: str, pw_key: str):
        """adds a pw"""
        Var.make_pw_file().append(pw_key, pw)
        print(f"{pw_key}: {pw} was saved")
        Var.pw_file_edit = True

    @staticmethod
    def remove_pw(pw_key: str):
        """removes a pw"""
        try:
            Var.make_pw_file().remove(pw_key)
            print(f"{pw_key} was removed")
            Var.pw_file_edit = True
        except KeyError:
            error_message("wrong pw_key")

    @staticmethod
    def show_pws():
        """shows all saved pws"""
        if not [print(y0, ":", y1) for y0, y1 in Var.make_pw_file().contains.items()]:  # I like this
            print("no pws are saved")  # it's not good for runtime and used ram, but I like it regardless

    """saved paths stuff start"""

    @staticmethod
    def show_dirs():
        """shows all saved dirs/paths"""
        if not [print(y0, ":", y1) for y0, y1 in Var.make_dir_file().contains.items()]:
            print("no dirs to show")

    @staticmethod
    def remove_dir(path_key: str):
        """removes a dir/path"""
        try:
            Var.make_dir_file().remove(path_key)
            print(f"{path_key} was removed")
            Var.dir_file_edit = True
        except KeyError:
            error_message("wrong path_key")

    """image coding stuff start"""

    @staticmethod
    def encode_img(cc: str, save_not_rdy_files: Optional[str] = None, data_path: Optional[str] = None):
        """the cc input should look like (69, 1, 42, ...), if save_not_rdy_files is True those files will be saved
        without ext and name, if data_path is not used the snn_cs obj will be used"""
        if Var.current_snn_picc_obj is None:
            print("you need to open an Image first (with open file)")
            return
        if data_path is None:
            a = Var.make_snn_cs_obj().to_bytes(save_not_rdy_files=save_not_rdy_files == "True")
        else:
            try:
                with io.open(data_path, "rb") as f:
                    a = f.read()
            except OSError:
                error_message("this file can not be opened/fount")
                return
        try:
            Var.current_snn_picc_obj = snn_picc.IC(Var.current_snn_picc_obj.encode(cc=make_cc(cc), data=a))
        except snn_picc.EncodeICError:
            error_message("Encode error sorry")
        except snn_picc.SetCCError:
            error_message("wrong cc")

    @staticmethod
    def decode_img(save_path: Optional[str] = None):
        if Var.current_snn_picc_obj is None:
            print("you need to open an Image first (with open file)")
            return
        try:
            a = Var.current_snn_picc_obj.decode()
        except snn_picc.DecodeICError:
            error_message("Image decode error")
            return
        if save_path is None:
            if Var.current_snn_cs_obj is not None and input_handler("do you want to overwrite the cs obj? else the  "
                                                                    "obj will be appended (Y/n) > ")["fkt"] == "Y":
                Var.current_snn_cs_obj = snn_cs.CS()
            try:
                Var.make_snn_cs_obj().from_bytes(a)
            except ValueError:
                error_message("it seems like the data in the image is not an snnc2 file")
        else:
            try:
                with io.open(save_path, "wb") as f:
                    f.write(a)
            except OSError:
                error_message("idk something went wrong")

    @staticmethod
    def save_img(save_path: str):
        """saves the opened image, works with all write formats of Pil"""
        save_path = path_input_handler(save_path)
        if Var.current_snn_picc_obj is not None:
            if not (os.path.splitext(save_path)[1] in Var.okay_ext_save_image):
                if not input_handler("the format you want to use is not lossless you want to use it regardless? "
                                     "(Y/n) > ")["fkt"] == "Y":
                    return
            try:
                Var.current_snn_picc_obj.img_obj.save(save_path)
            except OSError:
                error_message("the file could not be written")
                if os.path.isfile(save_path):
                    os.remove(save_path)
            except ValueError:
                error_message("your save_path must contain the ext of the file (none was found)")
        else:
            print("there is no Image you could save")

    @staticmethod
    def show_img_info(cc: Optional[str] = None):
        if Var.current_snn_picc_obj is None:
            print("you need to open an Image first (with open file)")
        else:
            print(f"format: {Var.current_snn_picc_obj.img_obj.format}\nsize: {Var.current_snn_picc_obj.img_obj.size}")
            a = tuple([1] * len(Var.current_snn_picc_obj.mode_edit)) if cc is None else make_cc(cc)
            print(f"max size for cc {a}: {Var.current_snn_picc_obj.get_max_space(a)} bytes")

    @staticmethod
    def show_img():
        """opens the img"""
        if Var.current_snn_picc_obj is None:
            print("you need to open an Image first (with open file)")
        else:
            Var.current_snn_picc_obj.img_obj.show()

    """save cc stuff"""

    @staticmethod
    def show_ccs():
        if not [print(y0, ":", y1) for y0, y1 in Var.make_cc_file().contains.items()]:
            print("no ccs to show")

    @staticmethod
    def remove_cc(cc_key: str):
        try:
            Var.make_cc_file().remove(cc_key)
            print(f"{cc_key} was removed")
            Var.cc_file_edit = True
        except KeyError:
            error_message("wrong cc_key")


on_start()
