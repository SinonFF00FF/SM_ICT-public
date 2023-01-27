import os
import io
from snn_grl import kwargs_handler
from datetime import datetime


class OM:
    default_kwargs = {"show_time": False, "save_as_log": True, "log_path_overwrite": None}
    default_log_path = os.path.join(os.getcwd(), "logs")

    def __init__(self, **kwargs):
        kwargs = kwargs_handler(kwargs, self.default_kwargs)
        self.log_path = os.path.join(self.default_log_path, f"log_{datetime.now().strftime('%x, %X')}"
                                     ) if kwargs["log_path_overwrite"] is None else kwargs["log_path_overwrite"]
        self.show_time, self.save_after = kwargs["show_time"], kwargs["save_as_log"]
        self.contains = []

    def print(self, *a: str, sep: str = " ", end: str = "\n", show_time: bool = None) -> None:
        show_time = self.show_time if show_time is None else show_time
        time_str = f"{datetime.now().strftime('%X')} << " if show_time else "<< "
        print(time_str, a, sep=sep, end=end)
        if self.save_after:
            self.contains += [time_str + sep]+[f"{y}{sep}" for y in list(a) + [end]]

    def save_log(self) -> None:
        if self.save_after:
            with io.open(self.log_path, "w", encoding="utf8") as f:
                f.write("".join(self.contains))
            print(f"log was saved at {self.log_path}")
