"""
QSPy Model Metadata Tracking and Export
=======================================

This module provides utilities for capturing, tracking, and exporting model metadata
in QSPy workflows. It includes environment capture, model hashing, and TOML export
for reproducibility and provenance tracking.

Classes
-------
QSPyBench : MicroBench-based class for capturing Python and host environment info.
ModelMetadataTracker : Tracks model metadata, environment, and provides export/load utilities.

Examples
--------
>>> tracker = ModelMetadataTracker(version="1.0", author="Alice", export_toml=True)
>>> tracker.metadata["model_name"]
'MyModel'
>>> ModelMetadataTracker.load_metadata_toml("MyModel__Alice__abcd1234__2024-07-01.toml")
"""

import getpass
import hashlib
import io
import json
import logging
import os
import platform
from datetime import datetime
from pathlib import Path

import numpy
import pysb
import scipy
import sympy
import pysb.pkpd
import pysb.units
import mergram
import toml
from microbench import MicroBench, MBHostInfo, MBPythonVersion
from pysb.core import SelfExporter

import qspy
from qspy.config import METADATA_DIR, LOGGER_NAME
from qspy.utils.logging import ensure_qspy_logging


class QSPyBench(MicroBench, MBPythonVersion, MBHostInfo):
    """
    MicroBench-based class for capturing Python and host environment information.

    Captures versions of key scientific libraries and host metadata for reproducibility.

    Attributes
    ----------
    capture_versions : tuple
        Tuple of modules to capture version info for (qspy, numpy, scipy, sympy, pysb, pysb.pkpd, pysb.units, mergram).
    """
    capture_versions = (qspy, numpy, scipy, sympy, pysb, pysb.pkpd, pysb.units, mergram)


class ModelMetadataTracker:
    """
    Tracks and exports QSPy model metadata, including environment and hash.

    On initialization, captures model version, author, user, timestamp, hash, and
    environment metadata. Optionally exports metadata to TOML.

    Parameters
    ----------
    version : str, optional
        Model version string (default "0.1.0").
    author : str, optional
        Author name (default: current user).
    export_toml : bool, optional
        If True, export metadata to TOML on creation (default: False).
    capture_conda_env : bool, optional
        If True, capture the active conda environment name (default: False).

    Attributes
    ----------
    model : pysb.Model
        The active PySB model instance.
    version : str
        Model version.
    author : str
        Author name.
    current_user : str
        Username of the current user.
    timestamp : str
        ISO timestamp of metadata creation.
    hash : str
        SHA256 hash of model rules and parameters.
    env_metadata : dict
        Captured environment metadata.
    metadata : dict
        Full metadata dictionary for export.

    Methods
    -------
    compute_model_hash()
        Compute a hash from model rules and parameters.
    capture_environment()
        Capture execution environment metadata.
    export_metadata_toml(path=None, use_metadata_dir=True)
        Export metadata to a TOML file.
    load_metadata_toml(path)
        Load metadata from a TOML file.

    Examples
    --------
    >>> tracker = ModelMetadataTracker(version="1.0", author="Alice", export_toml=True)
    >>> tracker.metadata["model_name"]
    'MyModel'
    """

    def __init__(
        self, version="0.1.0", author=None, export_toml=False, capture_conda_env=False
    ):
        """
        Initialize the ModelMetadataTracker.

        Parameters
        ----------
        version : str, optional
            Model version string (default "0.1.0").
        author : str, optional
            Author name (default: current user).
        export_toml : bool, optional
            If True, export metadata to TOML on creation (default: False).
        capture_conda_env : bool, optional
            If True, capture the active conda environment name (default: False).

        Raises
        ------
        RuntimeError
            If no model is found in the current SelfExporter context.
        """
        ensure_qspy_logging()
        logger = logging.getLogger(LOGGER_NAME)
        try:
            self.model = SelfExporter.default_model
            if not self.model:
                logger.error("No model found in the current SelfExporter context")
                raise RuntimeError("No model found in the current SelfExporter context")
            self.version = version
            self.author = author or "unknown"
            self.current_user = getpass.getuser()
            self.timestamp = datetime.now().isoformat()
            self.hash = self.compute_model_hash()
            self.env_metadata = self.capture_environment()

            if capture_conda_env:
                conda_env = os.environ.get("CONDA_DEFAULT_ENV", None)
                if conda_env:
                    self.env_metadata["conda_env"] = conda_env

            self.metadata = {
                "version": self.version,
                "author": self.author,
                "current_user": self.current_user,
                "created_at": self.timestamp,
                "hash": self.hash,
                "model_name": self.model.name or "unnamed_model",
                "env": self.env_metadata,
            }

            # Attach the metadata tracker to the model
            setattr(self.model, "qspy_metadata_tracker", self)

            if export_toml:
                self.export_metadata_toml()
        except Exception as e:
            logger.error(f"[QSPy][ERROR] Exception in ModelMetadataTracker.__init__: {e}")
            raise

    def compute_model_hash(self):
        """
        Create a hash from model definition (rules + parameters).

        Returns
        -------
        str
            SHA256 hash of the model's rules and parameters.
        """
        try:
            s = repr(self.model.rules) + repr(self.model.parameters)
            return hashlib.sha256(s.encode()).hexdigest()
        except Exception as e:
            logger = logging.getLogger(LOGGER_NAME)
            logger.error(f"[QSPy][ERROR] Exception in compute_model_hash: {e}")
            raise

    def capture_environment(self):
        """
        Capture execution environment via microbench.

        Returns
        -------
        dict
            Dictionary of captured environment metadata.
        """
        try:
            bench = QSPyBench()

            @bench
            def noop():
                pass

            noop()
            bench.outfile.seek(0)
            metadata = bench.outfile.read()
            if metadata == "":
                return {"microbench": "No metadata captured."}
            else:
                return json.loads(metadata)
        except Exception as e:
            logger = logging.getLogger(LOGGER_NAME)
            logger.error(f"[QSPy][ERROR] Exception in capture_environment: {e}")
            return {"microbench": f"Error capturing metadata: {e}"}

    def export_metadata_toml(self, path=None, use_metadata_dir=True):
        """
        Export metadata to a TOML file with autogenerated filename if none is provided.

        Parameters
        ----------
        path : str or Path, optional
            Output path for the TOML file. If None, an autogenerated filename is used.
        use_metadata_dir : bool, optional
            If True, use the configured METADATA_DIR for output (default: True).

        Returns
        -------
        None
        """
        ensure_qspy_logging()
        logger = logging.getLogger(LOGGER_NAME)
        try:
            metadata_dir = Path(METADATA_DIR) if use_metadata_dir else Path(".")
            metadata_dir.mkdir(parents=True, exist_ok=True)

            if path is None:
                safe_author = self.author.replace(" ", "_")
                safe_name = (self.model.name or "model").replace(" ", "_")
                short_hash = self.hash[:8]
                safe_time = self.timestamp.replace(":", "-")
                filename = f"{safe_name}__{safe_author}__{short_hash}__{safe_time}.toml"
                path = metadata_dir / filename

            with open(path, "w") as f:
                toml.dump(self.metadata, f)
            logger.info(f"Exported model metadata to TOML: {path}")
        except Exception as e:
            logger.error(f"[QSPy][ERROR] Exception in export_metadata_toml: {e}")
            raise

    @staticmethod
    def load_metadata_toml(path):
        """
        Load model metadata from a TOML file.

        Parameters
        ----------
        path : str or Path
            Path to the TOML metadata file.

        Returns
        -------
        dict
            Loaded metadata dictionary.

        Raises
        ------
        Exception
            If loading fails.
        """
        ensure_qspy_logging()
        logger = logging.getLogger(LOGGER_NAME)
        try:
            with open(path, "r") as f:
                return toml.load(f)
        except Exception as e:
            logger.error(f"[QSPy][ERROR] Exception in load_metadata_toml: {e}")
            raise
