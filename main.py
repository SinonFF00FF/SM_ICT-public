from snn_console_exec import callable_fkt as c_exec  # it's used in the exec str pls don't remove it
from snn_console_exec import input_handler, our_discord, config_check, error_message, on_close


def exec_input():
    """all args will be passed as str to the fkt, I think you can not exec stuff that is not in
    console_exec.callable_fkt or tru the arg str, I think all errors are caught and I hope I didn't miss one"""
    a = input_handler()
    if a["fkt"][0] == "_":
        print("nice try")
        return
    if config_check():
        print(f"-- debug stuff: a: {a} --")
    try:
        exec("".join([f"c_exec.{a['fkt']}("] + [f"r'{y}'," for y in a["val"]] + [")"]))
    except AttributeError:
        error_message(f"no fkt with with the name '{a['fkt']}'")
    except TypeError as e:
        error_message(str(e))
    except SyntaxError:
        error_message("wrong input")


def main():
    try:
        print(f"this shitty program was made by Sinon and FF00FF(depressed beluga)"
              f" if something doesnt work like intended pls message"
              f" us at Discord: {our_discord}\n"
              f"(its our first project so there might be a lot of bugs in it (sorry in advance))\n")
        print("type 'help' for a list of fkts and 'info' for general help")
        while True:
            exec_input()
    except:
        error_message("things that are not catch went wrong")
    finally:
        on_close()


if __name__ == '__main__':
    main()
