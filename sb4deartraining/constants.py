"""A few constants"""

# external imports
import numpy as np


### MATHEMATICS ###

PI = np.pi              # 3.14159... you know it
SQRT12 = np.sqrt(0.5)   # needed for pan laws

### MUSIC ###

# Semi-tone ratios (0 to 11 semi-tones up)
ST_RATIOS = [2 ** (st / 12) for st in range(0,12)]