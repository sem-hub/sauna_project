#!/usr/bin/env python3

import sys
sys.path.append('.')
import tm1637

disp = tm1637.TM1637(5, 3)

disp.set_doublepoint(False)
disp.set_values([' ', ' ', ' ', ' '])
