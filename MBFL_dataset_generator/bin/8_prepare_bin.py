#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent


def clone_musicup(musicup_dir):
    name = musicup_dir.name
    parent = musicup_dir.parent

    sp.run(f"git clone https://github.com/swtv-kaist/MUSICUP.git {name}", shell=True, cwd=parent)
    sp.run(f"git checkout develop", shell=True, cwd=musicup_dir)

def build_musicup(musicup_dir):
    sp.run(f"make LLVM_BUILD_PATH=/usr/lib/llvm-13 -j20", shell=True, cwd=musicup_dir)

def copy_musicup(musicup_exe, bin_on_machine):
    sp.run(f"cp {musicup_exe} {bin_on_machine}", shell=True)

def musicup(musicup_dir):

    # Clone MUSICUP
    if not musicup_dir.exists():
        clone_musicup(musicup_dir)
    
    # Build MUSICUP
    musicup_exe = musicup_dir / 'music'
    if not musicup_exe.exists():
        build_musicup(musicup_dir)
    
    # copy to bin_on_machine
    bin_on_machine = main_dir / 'bin_on_machine/musicup'
    if not bin_on_machine.exists():
        copy_musicup(musicup_exe, bin_on_machine)


def start_program():
    musicup_dir = root_dir / 'MUSICUP'
    musicup(musicup_dir)
    


if __name__ == "__main__":
    start_program()
