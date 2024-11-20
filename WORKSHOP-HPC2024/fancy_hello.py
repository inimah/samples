import time
import sys

def fancy_hello():
    message = "Hello, World!"
    ascii_art = r"""
     _    _      _ _         __        __         _     _ _ 
    | |  | |    | | |        \ \      / /        | |   | | |
    | |__| | ___| | | ___     \ \ /\ / /__  _ __ | | __| | |
    |  __  |/ _ \ | |/ _ \     \ V  V / _ \| '_ \| |/ _` | |
    | |  | |  __/ | | (_) |     \_/\_/ (_) | | | | | (_| |_|
    |_|  |_|\___|_|_|\___( )                 |_| |_|\__,_(_)
                       |/                                  
    """

    for line in ascii_art.splitlines():
        print(line)
        time.sleep(0.05)

    print("\n", end="")
    for char in message:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.1)
    print()  # Newline at the end

if __name__ == "__main__":
    fancy_hello()