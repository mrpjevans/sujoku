#
# SuJoKu
# A sudoku sketcher for Joto
# (c) 2019 PJ Evans <pj@mrpjevans.com>
#
# See LICENSE and README.md
#
import json
import argparse
import os
import sys
import serial
import random
import time

# Command line arguments
parser = argparse.ArgumentParser(description='Sudoko for Joto')
parser.add_argument('--pen-up', type=float, default=70,
                    help='Pen up value')
parser.add_argument('--pen-down', type=float, default=170,
                    help='Pen down value')
parser.add_argument('--pen-dock', type=float, default=235,
                    help='Pen dock value')
parser.add_argument('--no-grid', action="store_true", default=False,
                    help='Don\'t draw the grid')
parser.add_argument('--no-start-end', action="store_true", default=False,
                    help='Don\'t include start and finish scripts')
parser.add_argument('--no-numbers', action="store_true", default=False,
                    help='Don\'t draw numbers')
parser.add_argument('--no-wipe', action="store_true", default=False,
                    help='Don\'t start by wiping the board')
parser.add_argument('--port', type=str, default="",
                    help='Joto port')
parser.add_argument('-x', type=int, default=27,
                    help='X-axis offset')
parser.add_argument('-y', type=int, default=0,
                    help='Y-axis offset')
parser.add_argument('--puzzle', type=int, default=-1,
                    help='Puzzle number (otherwise random)')

args = parser.parse_args()
pen_up = str(args.pen_up)
pen_down = str(args.pen_down)
pen_dock = str(args.pen_dock)
x_origin = args.x
y_origin = args.y


# Read a file in line-by-line
def read_to_array(file_name):

    out = []
    f = open(file_name, "r")
    for line in f:
        line = line.replace("{{pen_up}}", pen_up)
        line = line.replace("{{pen_down}}", pen_down)
        line = line.replace("{{pen_dock}}", pen_dock)
        out.append(line.rstrip())

    return out


# Send a line to Joto
def send_line(line):

    while True:

        # Clean the line and don't bother if empty
        line = str.strip(line)
        if line == '' or line[0] == ';':
            return True

        # Send line
        print("<< " + line)
        ser.write(str.encode(line + '\r\n'))

        # Check response
        response = ""
        timeout = 100

        while response == "":
            time.sleep(0.2)
            while ser.inWaiting() > 0:
                response += ser.read(1).decode("utf-8")
            timeout -= 1
            if timeout == 0:
                print("Timeout waiting for Joto's response")
                return False
            if response.strip() == "busy:processing":
                print("Waiting")
                time.sleep(1)
                response = ""

        # Validate response
        gotOk = False
        responseByLine = response.splitlines(False)
        for responseLine in responseByLine:
            print(">> " + responseLine)
            if responseLine == 'ok 0':
                gotOk = True

        if gotOk:
            break

    return True

# Read in files
my_dir = os.path.dirname(os.path.realpath(__file__))
wipe_gcode = read_to_array(my_dir + "/wipe.gcode")
start_gcode = read_to_array(my_dir + "/start.gcode")
end_gcode = read_to_array(my_dir + "/end.gcode")

# Load font information
with open(my_dir + "/default_font.json", "r") as f:
    font = json.load(f)

# Load puzzles
with open(my_dir + "/grids.txt", "r") as f:
    grids_raw = f.read()
grids = grids_raw.split("\n\n")

# Select the puzzle
if args.puzzle == -1:
    args.puzzle = random.randint(0, len(grids))

# Check out puzzle can be rendered
if len(grids) < args.puzzle:
    print("Puzzle %i does not exist. Choose one between 1 and %i"
          % (args.puzzle, len(grids)))
    sys.exit(1)

grid = grids[args.puzzle].split("\n")

# Settings
gcode = []
font_size = 0.2

x_boundary = 280
y_boundary = 300

x_grid_start = x_origin
x_grid_end = x_grid_start + 225
y_grid_start = 300 - y_origin
y_grid_end = y_grid_start - 225

x_start = x_origin + 3
y_start = 297 - y_origin
x_offset = x_start
y_offset = y_start - (100 * font_size)

# Wipe?
if args.no_wipe is False:
    gcode = wipe_gcode

# Add the start gcode?
if args.no_start_end is False:
    gcode = gcode + start_gcode

# Draw the grid?
if args.no_grid is False:

    direction = 0
    for vertical in range(y_grid_start, y_grid_start - 250, -25):
        gcode.extend(("M106 S%s" % (pen_up),
                      "G4 P60.0",
                      "G1 X%i Y%i" % (x_grid_start + direction, vertical),
                      "M106 S%s" % (pen_down),
                      "G4 P60.0",
                      "G1 X%i Y%i" % (x_grid_end - direction, vertical)))
        if direction == 225:
            direction = 0
        else:
            direction = 225
    direction = 225
    for horizontal in range(x_grid_start, x_grid_start + 250, 25):
        gcode.extend(("M106 S%s" % (pen_up),
                      "G4 P60.0",
                      "G1 X%i Y%i" % (horizontal, y_grid_start - direction),
                      "M106 S%s" % (pen_down),
                      "G4 P60.0",
                      "G1 X%i Y%i" % (horizontal, y_grid_end + direction)))
        if direction == 225:
            direction = 0
        else:
            direction = 225

    # Finally draw the inner lines
    gcode.extend(("M106 S%s" % (pen_up),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_end, y_grid_start - 149),
                  "M106 S%s" % (pen_down),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_start, y_grid_start - 149)))

    gcode.extend(("M106 S%s" % (pen_up),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_start, y_grid_start - 74),
                  "M106 S%s" % (pen_down),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_end, y_grid_start - 74)))

    gcode.extend(("M106 S%s" % (pen_up),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_start + 151, y_grid_start),
                  "M106 S%s" % (pen_down),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_start + 151, y_grid_end)))

    gcode.extend(("M106 S%s" % (pen_up),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_start + 76, y_grid_end),
                  "M106 S%s" % (pen_down),
                  "G4 P60.0",
                  "G1 X%i Y%i" % (x_grid_start + 76, y_grid_start)))

# Generate the gcode to write out the numbers
# Rows
if args.no_numbers is False:

    for row in grid:

        # Number (Columns)
        for col in row:

            if col != "0":
                for cmd in font[col]:

                    if cmd[0] == 'u':  # Pen up
                        gcode.append('M106 S%s' % (pen_up))
                        gcode.append('G4 P60.0')
                    elif cmd[0] == 'd':  # Pen down
                        gcode.append('M106 S%s' % (pen_down))
                        gcode.append('G4 P60.0')
                    elif cmd[0] == 'm':  # Move

                        # Calc actual position to move to
                        x = x_offset + (cmd[1] * font_size)
                        y = y_offset + (cmd[2] * font_size)

                        # Boundary check
                        if x > x_boundary or y > y_boundary:
                            print("Too big! Would make Joto sad.")
                            sys.exit(1)

                        # Add instruction
                        gcode.append('G1 X%.2f Y%.2f' % (x, y))

            # Move along one place
            x_offset += 25

        # Move down one row and back to the start typewriter-stylee
        y_offset -= 25
        x_offset = x_start

# Add the end gcode?
if args.no_start_end is False:
    gcode = gcode + end_gcode

#
# Output section
#

# Output to console or send to Joto?
if args.port != "":

    # Configure serial
    ser = serial.Serial(
        port=args.port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    # Cycle the port
    ser.close()
    ser.open()

    for line in gcode:
        if send_line(line) is False:
            print("Communication error, stopping")
            sys.exit(1)

    # Close the port
    ser.close()

else:
    for line in gcode:
        print(line)
