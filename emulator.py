import os
import sys
import shlex
import getpass
import socket


def make_prompt():
    user = getpass.getuser()
    host = socket.gethostname().split('.')[0]
    home = os.path.expanduser('~')
    cwd = os.getcwd()
    if cwd == home or cwd.startswith(home + os.sep):
        if cwd == home:
            short = '~'
        else:
            short = '~' + cwd[len(home):]
    else:
        short = cwd
    return f"{user}@{host}:{short}$ "

def parse_command(line):
    return shlex.split(line, posix=True)

def ls(args):
    print("COMMAND: ls")
    print("ARGS:", args)
    # for name in os.listdir('.'):
    #     print(name)
    # Но в задании сказано — заглушка, поэтому только имя и args.

def cd(args):
    print("COMMAND: cd")
    print("ARGS:", args)
    if len(args) == 0:
        target = os.path.expanduser('~')
    else:
        target = args[0]

    try:
        os.chdir(os.path.expanduser(target))
        print(f"(changed directory to {os.getcwd()})")
    except FileNotFoundError:
        print(f"cd: no such file or directory: {target}")
    except NotADirectoryError:
        print(f"cd: not a directory: {target}")
    except PermissionError:
        print(f"cd: permission denied: {target}")
    except Exception as e:
        print(f"cd: error: {e}")

def repl():
    while True:
        try:
            prompt = make_prompt()
            line = input(prompt)
        except EOFError:
            # Ctrl-D полный выход
            break
        except KeyboardInterrupt:
            # Ctrl-C перенос строки
            print()
            continue

        line = line.strip()
        if not line:
            continue

        try:
            argv = parse_command(line)
        except ValueError as ve:
            print(f"parse error: {ve}")
            continue

        cmd = argv[0]
        args = argv[1:]

        if cmd == 'exit':
            code = 0
            if len(args) >= 1:
                try:
                    code = int(args[0])
                except ValueError:
                    print("exit: numeric argument required")
                    code = 1
            print("Exiting shell...")
            sys.exit(code)
        elif cmd == 'ls':
            ls(args)
        elif cmd == 'cd':
            cd(args)
        else:
            print(f"{cmd}: command not found")
