from os import system, name


def change_username() -> None:
    return input("enter username: ")


def valid_usinp(max: int) -> int:
    """checks user input is valid type and within specified (max) range"""
    while True:
        try:
            usinp = int(input("$: "))
        except ValueError:
            continue
        if 0 <= usinp <= max:
            return usinp


def cli_cls() -> None:
    """clear console"""
    system("cls" if name == "nt" else "clear")


def cli_draw_logo() -> None:
    """draw 'discreet dial' logo to console"""
    print("\x1b[1;31m\n      ___                     __       ___      __\n  ___/ (_)__ ___________ ___ / /_  ___/ (_)__ _/ /\n / _  / (_-</ __/ __/ -_) -_) __/ / _  / / _ `/ /\n \_,_/_/___/\__/_/  \__/\__/\__/  \_,_/_/\_,_/_/\n\n \033[0m")
