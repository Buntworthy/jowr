import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import numpy as np

# Test opening camera - open, not connected, closed
# Test opening video - open, not connected, closed
# Test reading frames
