# 6502-emu

6502-emu is a work in progress, and aims to be a emulator for the NES version of the 6502 hardware.

# Note

This is a personal learning project, and isn't indended to be feature complete. For a more comprehensive solution, check out [py65](https://github.com/mnaberez/py65) for Python, or [Easy6502](https://github.com/skilldrick/easy6502) for JavaScript

# Progress

## emu6502.py
The emulator has a limited number of opcodes. To function, it must be supplied with a list of integers.

The MemoryMap class represents the memory of a single hardware instance. Multiple maps can be created and manipulated via the emu6502 module's functions.

Lookup tables are here, but I may move them or reformat them

## parse6502.py
The parser contains some functions for converting between various formats of assembly code

The asm parser currently can't handle labels

## monitor.py
The monitor can subscribe to events, though only one event currently reports.

It will be configurable to print useful info about the state of the emulator into the terminal

## main.py
Main brings together some examples, but currently lacks the ability to take input from the user

## /input
The input folder contains a few samples, in various formats. The samples are taken from Nick Morgan's [Easy6502](https://github.com/skilldrick/easy6502), and are used under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license

## /gui/memoryview.py
The graphical memory viewer is currently disconnected from the emulator, but it can be used to view the contents of a binary file. /input/snake6502.rom is in the format expected