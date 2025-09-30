"""Default settings for reoccurring parameters."""

# --- Audio Settings ---
_SR = 44100                         # default sample rate
_JUST_BELOW_NYQUIST = _SR // 2 - 1  # frequency just  below nyquist
_BLOCKSIZE = 1024                   # default block size for audio streams

# --- Default Paths ---
_AUDIO_SAMPLE_PATH = "./samples/"   # default sample path