# Model Metadata Tracking in QSPy

QSPy provides robust metadata tracking for all models using the `ModelMetadataTracker` class. This enables reproducibility, provenance, and environment capture for quantitative systems pharmacology (QSP) workflows.

---

## What is `ModelMetadataTracker`?

`ModelMetadataTracker` is a utility class that captures and manages metadata about your QSPy model, including:

- Model version, author, and creation timestamp
- The current user and environment details (Python, OS, package versions)
- A hash of the model's rules and parameters (for provenance)
- Optional export to TOML for archiving and sharing

Metadata is automatically attached to the model instance and can be exported or loaded as needed.

---

## Typical Usage

### 1. Automatic Tracking

When you instantiate `ModelMetadataTracker`, it attaches itself to the current PySB/QSPy model:

```python
from qspy.validation.metadata import ModelMetadataTracker

Model().with_units(...)
...
...

# After building your model
ModelMetadataTracker(version="1.0", author="Alice", export_toml=True)
```

- The tracker will automatically attach itself to `model.qspy_metadata_tracker`.
- Metadata is available as a dictionary: `model.qspy_metadata_tracker.metadata`
- If `export_toml=True`, metadata is saved to a TOML file your configured metadata directory (`.qspy` by default).

### 2. Accessing Metadata

You can access the metadata dictionary at any time:

```python
meta = model.qspy_metadata_tracker.metadata
print(meta["model_name"])
print(meta["hash"])
print(meta["env"])  # Environment details
```

### 3. Exporting and Loading Metadata

Export metadata to a TOML file:

```python
model.qspy_metadata_tracker.export_metadata_toml() # Auto-generates filename
model.qspy_metadata_tracker.export_metadata_toml(path="custom_metadata.toml")
```

Load metadata from a TOML file:

```python
from qspy.validation.metadata import ModelMetadataTracker

meta = ModelMetadataTracker.load_metadata_toml("MyModel__Alice__abcd1234__2024-07-01.toml")
print(meta["version"])
```

**Example**

```python
from qspy.validation.metadata import ModelMetadataTracker

# Build your model here...

# Track and export metadata
tracker = ModelMetadataTracker(version="2.0.1", author="Bob", export_toml=True)

# Access metadata
print(tracker.metadata["model_name"])
print(tracker.metadata["created_at"])
print(tracker.metadata["env"]["platform"])
```

## Why Use Metadata Tracking?

- **Reproducibility**: Know exactly which code, environment, and parameters produced your results.
- **Provenance**: Track model changes and authorship over time.
- **Environment Capture**: Record Python, OS, and package versions for future reference.
- **Archival**: Export metadata alongside your model for publication or collaboration.
