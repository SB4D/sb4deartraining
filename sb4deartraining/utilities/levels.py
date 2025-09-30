"""Utility functions for working with audio levels."""

import numpy as np

def convert_ratio_to_db(ratio:float) -> float:
    """Converts level difference (dB) to amplitude ratio."""
    # db = 20 * np.log10(ratio)
    db = 20 * np.log10(np.maximum(ratio, 1e-12))
    return db

def convert_db_to_ratio(db):
    """Converts amplitude ratio to level difference (dB)."""
    ratio = 10 ** (db / 20)
    return ratio

def add_db(signal:np.ndarray, db:float) -> np.ndarray:
    ratio = convert_db_to_ratio(db)
    new_signal = signal * ratio
    return new_signal