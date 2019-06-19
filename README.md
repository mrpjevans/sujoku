# SuJoKu
Generates sudoku puzzles on a Joto whiteboard

## Requirements

* Python 3

## Connection

Joto connects to your computer as a serial device. You need to work out which one is Joto.

**Linux**
Look in /dev for a device named ttyACM0 or similar.

**macOs**
Look in /dev for a device named tty.usbmodem14201 or similar.

**Windows**
Not a clue, sorry. If someone wants to submit a PR...

## Usage

Generate gcode to draw a sudoku grid

```bash
python3 sujoku.py
```

To save gcode to a file:

```bash
python3 sujoku.py > output.gcode
```

To generate a grid and send it to the Joto:

```bash
python3 sojoku.py --port /dev/port
```

(Change /dev/port to whatever your connection is)

## Arguments

Defaults are in brackets

```
  -h, --help           show help message and exit
  --pen-up PEN_UP      Pen up value (70)
  --pen-down PEN_DOWN  Pen down value (170)
  --pen-dock PEN_DOCK  Pen dock value (40)
  --no-grid            Don't draw the grid (false)
  --no-start-end       Don't include start and finish scripts (false)
  --no-numbers         Don't draw numbers (false)
  --no-wipe            Don't start by wiping the board (false)
  --port PORT          Send to Joto on the given port (false)
  -x X                 X-axis offset (27)
  -y Y                 Y-axis offset (0)
  --puzzle PUZZLE      Puzzle number 1-50 (otherwise random)
```

## Add Grids

The grids are intentionally simple file format and stored in grids.txt.

To add your own, append a blank line followed by nine lines of nine numbers,
using 0 for blank spaces. Add as many as you like!

## Disclaimer

This utility is provided 'as is' with no warranty. Gcode can harm your Joto. Use at your own risk.

