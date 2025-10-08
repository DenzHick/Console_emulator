import sys
import shlex
import getpass
import socket

from vfs import VFS
from commands import BUILTIN_COMMANDS

class Emulator:
    def __init__(self, config):
        self.config = config
        self.vfs = VFS()
        self.vfs.load_vfs(config['vfs_file'])

    def make_prompt(self):
        user = getpass.getuser()
        host = socket.gethostname().split('.')[0]
        short = self.vfs.get_current_path()
        return f"{user}@{host}:{short}$ "

    def parse_command(self, line):
        return shlex.split(line, posix=True)

    def execute_command(self, line):
        line = line.strip()
        if not line:
            return

        try:
            argv = self.parse_command(line)
        except ValueError as ve:
            print(f"parse error: {ve}")
            return

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
        elif cmd in BUILTIN_COMMANDS:
            command_func = BUILTIN_COMMANDS[cmd]
            command_func(args, self.vfs)
        else:
            print(f"{cmd}: command not found")

    def run_script(self, script_path):
        try:
            with open(script_path, 'r') as f:
                for line in f:
                    clean_line = line.strip()
                    if not clean_line or clean_line.startswith('#'):
                        continue

                    prompt = self.make_prompt()
                    print(prompt + clean_line)

                    self.execute_command(clean_line)

        except FileNotFoundError:
            print(f"error: startup script not found at '{script_path}'")
        except Exception as e:
            print(f"error reading script '{script_path}': {e}")

    def repl(self):
        if self.config['startup_script']:
            self.run_script(self.config['startup_script'])
        else:
            while True:
                try:
                    prompt = self.make_prompt()
                    line = input(prompt)
                    self.execute_command(line)
                except EOFError:
                    print("\nExiting shell...")
                    break
                except KeyboardInterrupt:
                    print()
                    continue
