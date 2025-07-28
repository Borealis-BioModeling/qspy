# QSPy Outputs and Logs

QSPy automatically generates a variety of outputs and logs to help you track, audit, and reproduce your modeling work. By default, these files are stored in a hidden `.qspy` folder in your project directory.

---

## What is in the `.qspy` Folder?

The `.qspy` folder is created automatically when you run QSPy code. It contains:

- **Model summaries:** Markdown files summarizing model structure, parameters, and metadata (output from the `Model.markdown_summary` function)
- **Model diagrams:** Mermaid or image files visualizing model architecture (if enabled by using the `ModelMermaidDiagrammer`).
- **Run logs:** Detailed logs of model construction, macro usage, and simulation runs.
- **Audit trails:** Metadata and hashes for reproducibility and version tracking (if enabled by using the `ModelMetadataTracker`).

This folder is intended to be a central location for all QSPy-generated artifacts, making it easy to review your modeling workflow and share results.

---

## Example Contents

```
.qspy/
├── model_summary.md
├── model_diagram.mmd
├── logs/
├───|──── qspy.log
├── metadata/
├───|──── model-name__author__short-hash__time.toml
└── ...
```

---

## Changing the Output Location

By default, QSPy writes all outputs and logs to `.qspy` in the current working directory. You can change this location using the `qspy.config` module.

!!! example "Change the output directory"
    ```python
    import qspy.config

    # Set a new output directory for QSPy logs and artifacts
    qspy.config.set_output_dir("my_outputs/qspy_artifacts")
    ```

This will update `qspy.config.OUTPUT_DIR`, and all new logs and outputs will be written to the specified folder.

---

## Tips

- **Version control:** You may want to add `.qspy/` to your `.gitignore` if you do not wish to track logs and outputs in version control.
- **Reproducibility:** The logs and metadata in `.qspy` are useful for reproducing results and tracking model changes over time.
- **Cleanup:** You can safely delete the `.qspy` folder if you want to clear outputs; it will be recreated as needed.

---

## See Also

- [Model Summary Generator](model-summary-generator.md)
- [Model Diagram Generator](./model-diagram-generator.md)
- [Metadata Tracking](./metadata-tracking.md)