# midi-inspo

A tiny toolkit that extracts lightweight features from Standard MIDI files and
turns them into creative prompts. Use it from the terminal or launch the Tk
based interface for a more visual workflow.

## Installation

The project has no external dependencies beyond the Python standard library.
Clone the repository and install it in editable mode if you want to experiment
locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Command line usage

Pass a path to a `.mid` or `.midi` file to generate textual inspiration:

```bash
python -m midi_inspo path/to/song.mid
```

Optional flags:

- `--show-features`: append a human readable dump of the extracted feature
  dictionary.
- `--show-json`: append the JSON representation of the features (mutually
  exclusive with `--show-features`).

## Graphical interface

The package also ships with a Tkinter interface. Launch it by passing the
`--ui` flag to the module entrypoint:

```bash
python -m midi_inspo --ui
```

The window lets you browse for a MIDI file, toggle whether feature summaries or
raw JSON should be included, and displays the generated ideas in a scrolling
text area.

> **Note:** Tkinter ships with the default CPython distribution on Windows,
> macOS, and most Linux distributions. Some minimal Linux environments may not
> include the Tk libraries by default; install `python3-tk` (or the equivalent
> package for your distribution) if the UI fails to launch.

## Development

Run the automated tests with:

```bash
pytest
```

The tests include a smoke check that ensures the CLI correctly routes the
`--ui` flag without attempting to open a window, keeping continuous integration
runs headless-friendly.
