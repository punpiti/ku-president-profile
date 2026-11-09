# Project Agent Notes

This OneDrive folder stores KU president/vision/selection working material.
Do not create or maintain `.venv`, `venv`, `env`, or `.conda` inside this
folder.

Use a machine-local conda/micromamba environment for the small Python tool stack
listed in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Generated website builds and local private workspaces should remain ignored as
configured in `.gitignore`.
