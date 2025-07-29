"""
QSPy Configuration Module
=========================

This module centralizes configuration constants for QSPy, including logging,
unit defaults, output/reporting directories, and versioning information.

Attributes
----------
LOGGER_NAME : str
    Name of the logger used throughout QSPy.
LOG_PATH : Path
    Path to the QSPy log file.
DEFAULT_UNITS : dict
    Default units for concentration, time, and volume.
METADATA_DIR : Path
    Directory for storing model metadata files.
SUMMARY_DIR : Path
    Path for the model summary markdown file.
QSPY_VERSION : str
    The current version of QSPy.
"""

from pathlib import Path

OUTPUT_DIR = Path(".qspy")

# Logging
LOGGER_NAME = "qspy"
LOG_PATH = OUTPUT_DIR / "logs/qspy.log"

# Unit defaults
DEFAULT_UNITS = {"concentration": "mg/L", "time": "h", "volume": "L"}

# Output & reporting
METADATA_DIR = OUTPUT_DIR / "metadata"
SUMMARY_DIR = OUTPUT_DIR / "model_summary.md"

# Versioning
QSPY_VERSION = "0.1.0"

def set_output_dir(path: str | Path):
    """
    Set the output directory for QSPy reports and metadata.

    Parameters
    ----------
    path : Path
        The new output directory path.
    """
    global OUTPUT_DIR, LOG_PATH, METADATA_DIR, SUMMARY_DIR
    OUTPUT_DIR = Path(path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    global LOG_PATH, METADATA_DIR, SUMMARY_DIR
    LOG_PATH = OUTPUT_DIR / "logs/qspy.log"
    METADATA_DIR = OUTPUT_DIR / "metadata"
    SUMMARY_DIR = OUTPUT_DIR / "model_summary.md"

def set_log_path(path: str | Path):
    """
    Set the log file path for QSPy.

    Parameters
    ----------
    path : Path
        The new log file path.
    """
    global LOG_PATH
    LOG_PATH = Path(path)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def set_logger_name(name: str):
    """
    Set the logger name for QSPy.

    Parameters
    ----------
    name : str
        The new logger name.
    """
    global LOGGER_NAME
    LOGGER_NAME = name