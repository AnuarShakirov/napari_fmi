"""Module contains constants used in the plugin."""

# N of rows to consider during visualization of logview for FMI image
SAMPLING_STEP: int = 10
# sigma value for gaussian filter
SIGMA: int = 2
# constant number of logs to select
N_LOGS: int = 3
# number of columns to expect within formation tops file
N_COLS_FORMATION_TOPS: int = 6
# encoded None value within logs
ENCODED_NONE: int = -99
