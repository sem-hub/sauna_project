#!/usr/bin/env python3

import sys
sys.path.append('.')
import TM1637

disp = TM1637.TM1637(5, 3)

disp.set_doublepoint(False)
disp.set_values([' ', ' ', ' ', 'PE'])
