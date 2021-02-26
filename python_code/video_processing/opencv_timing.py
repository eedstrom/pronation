#!/usr/bin/env python3
# Pronation Program
# Copyright (C) 2021 Dominic Culotta, Eric Edstrom, Jae Young Lee, Teagan Mathur, Brian Petro, Wilma Rishko, Ruizhi Wang
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
from pathlib import Path
import cv2
import numpy as np
#print(sys.argv[1])

def GetFrames(Path(os.getcwd()) / sys.argv[1]):
    vidObj = cv2.VideoCapture(sys.argv[1])
    
    count = 0
    
    success = 1
    while success:

        success, image = viObj.read()

        cv2.imwrite("frame%d.jpg" % count, image)

        count += 1

if __name__ == '__main__':
    
    GetFrame(sys.argv[1])
