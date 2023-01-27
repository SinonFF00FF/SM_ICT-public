from typing import Dict, Any, List, Union, Generator

# May God have mercy with whoever has to read this abomination


def kwargs_handler(kwarg_in: Dict[Any, Any], base_kwarg_dict: Dict[Any, Any],
                   test_for_type: bool = True) -> Dict[Any, Any]:
    for y in kwarg_in:
        if y in base_kwarg_dict.keys():
            if test_for_type and not isinstance(kwarg_in[y], type(base_kwarg_dict[y])):
                raise TypeError(f"wrong type for {y} (is {type(kwarg_in[y])} should be {type(base_kwarg_dict[y])})")
            base_kwarg_dict[y] = kwarg_in[y]
        else:
            raise ValueError(f"wrong kwarg {y} (possible kwargs: {base_kwarg_dict.keys()})")
    return base_kwarg_dict


def make_set_len(a: str, lenlen: int, fill_str: str = "0", side: str = "left") -> str:
    side = {"left": (1, 0), "right": (0, 1)}[side]
    return fill_str * ((lenlen - len(a)) * side[0]) + a + fill_str * ((lenlen - len(a)) * side[1])


def str_to_bytes(a: str, encoding: str = "utf8") -> bytes:
    return bytes(a, encoding=encoding)


def get_key(val: Any, search_dict: Dict[Any, Any]) -> Any:
    return list(search_dict.keys())[list(search_dict.values()).index(val)]


def write_val_bits(a: List[int], **kwargs) -> str:
    base_kwarg_dict = {"bin_map": {"0": "0", "1": "01", "end": "11", "start": ""},
                       "end_key": "end", "start_key": "start", "len_int": 8}
    kwargs = kwargs_handler(kwargs, base_kwarg_dict, True)
    list1 = [kwargs[kwargs["start_key"]]]
    for y in a:
        for yy in make_set_len(bin(y)[2:], kwargs["len_int"]):
            list1.append(kwargs["bin_map"][yy])
        list1.append(kwargs["bin_map"][kwargs["end_key"]])
    return "".join(list1)


def read_val_bits(a: Union[str, Generator[str, None, None]], int_count: int, **kwargs) -> List[int]:
    base_kwarg_dict = {"bin_map": {"0": "0", "1": "01", "end": "11", "start": ""},
                       "end_key": "end", "start_key": "start"}
    kwargs = kwargs_handler(kwargs, base_kwarg_dict, True)
    list1, list2, b = [], [], ""
    for y in a:
        b += y
        if b in kwargs["bin_map"].values():
            if b == kwargs["bin_map"][kwargs["end_key"]]:
                list2.append(int("".join(list1), 2))
                if len(list2) == int_count:
                    break
                list1 = []
            else:
                list1.append(get_key(y, kwargs["bin_map"]))
            b = ""
    else:
        raise ValueError("")
    return list2












