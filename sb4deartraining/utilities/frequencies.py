
from ..constants import ST_RATIOS

def add_semi_tones(freq:float, st:int|float=0):
    if st == 0:
        return freq
    elif type(st) == int:
        # write st = 12 * n + k with 0 <= k < 12
        n = st // 12
        k = st % 12
        freq *= 2 ** n
        freq *= ST_RATIOS[k]
        return freq
    else:
        return freq * 2 ** (st / 12)