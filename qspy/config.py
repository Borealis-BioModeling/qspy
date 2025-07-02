"""
QSPy Configuration Module
=========================

This module centralizes configuration constants for QSPy, including logging,
unit defaults, output/reporting directories, and versioning information.

Attributes
----------
LOGGER_NAME : str
    Name of the logger used throughout QSPy.
LOG_PATH : str
    Path to the QSPy log file.
DEFAULT_UNITS : dict
    Default units for concentration, time, and volume.
METADATA_DIR : str
    Directory for storing model metadata files.
SUMMARY_DIR : str
    Path for the model summary markdown file.
QSPY_VERSION : str
    The current version of QSPy.
"""

# Logging
LOGGER_NAME = "qspy"
LOG_PATH = ".qspy/logs/qspy.log"

# Unit defaults
DEFAULT_UNITS = {"concentration": "mg/L", "time": "h", "volume": "L"}



# Output & reporting
METADATA_DIR = ".qspy"
SUMMARY_DIR = METADATA_DIR + "/model_summary.md"

# Versioning
QSPY_VERSION = "0.1.0"