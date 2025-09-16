"""Tkinter based user-interface for MIDI inspiration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .analysis import MidiFeatureError, extract_features
from .ideas import InspirationGenerator


@dataclass
class UiDependencies:
    tk: object
    ttk: object
    filedialog: object
    messagebox: object


class MidiInspirationApp:
    """Encapsulates the Tkinter application and widgets."""

    def __init__(
        self,
        root,
        deps: UiDependencies,
        *,
        generator_factory: Callable[[dict], InspirationGenerator] = InspirationGenerator,
    ) -> None:
        self.root = root
        self.deps = deps
        self.generator_factory = generator_factory

        self.root.title("MIDI Inspiration")
        self.root.geometry("640x480")

        tk = deps.tk
        ttk = deps.ttk

        self.selected_file = tk.StringVar()
        self.show_features = tk.BooleanVar(value=False)
        self.show_json = tk.BooleanVar(value=False)

        container = ttk.Frame(root, padding=12)
        container.pack(fill="both", expand=True)

        file_frame = ttk.Frame(container)
        file_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(file_frame, text="Selected MIDI file:").pack(side="left")
        entry = ttk.Entry(file_frame, textvariable=self.selected_file)
        entry.pack(side="left", fill="x", expand=True, padx=(8, 8))

        ttk.Button(file_frame, text="Browse…", command=self.open_file_dialog).pack(side="right")

        options_frame = ttk.Frame(container)
        options_frame.pack(fill="x", pady=(0, 8))

        ttk.Checkbutton(
            options_frame,
            text="Show features",
            variable=self.show_features,
            command=self._sync_toggles,
        ).pack(side="left")
        ttk.Checkbutton(
            options_frame,
            text="Show JSON",
            variable=self.show_json,
            command=self._sync_toggles,
        ).pack(side="left", padx=(8, 0))

        ttk.Button(container, text="Generate Inspiration", command=self.generate_ideas).pack(fill="x")

        self.text = tk.Text(container, wrap="word", height=20)
        self.text.pack(fill="both", expand=True, pady=(8, 0))

    def _sync_toggles(self) -> None:
        if self.show_features.get():
            self.show_json.set(False)

    def open_file_dialog(self) -> None:
        filename = self.deps.filedialog.askopenfilename(
            title="Select MIDI file",
            filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")],
        )
        if filename:
            self.selected_file.set(filename)

    def generate_ideas(self) -> None:
        path = self.selected_file.get()
        if not path:
            self.deps.messagebox.showinfo("No file selected", "Choose a MIDI file to analyze.")
            return
        try:
            features = extract_features(path)
        except MidiFeatureError as exc:
            self.deps.messagebox.showerror("Feature extraction failed", str(exc))
            return
        generator = self.generator_factory(features)
        ideas = generator.generate_ideas(
            show_features=self.show_features.get(),
            show_json=self.show_json.get(),
        )
        self.text.delete("1.0", "end")
        self.text.insert("1.0", ideas)

    def run(self) -> None:
        self.root.mainloop()


def create_app(root, *, deps: Optional[UiDependencies] = None) -> MidiInspirationApp:
    """Create the Tk application without starting the main loop.

    This helper facilitates testing in headless environments where instantiating
    ``tkinter.Tk`` may not be possible.
    """

    if deps is None:
        import tkinter as tk  # type: ignore
        from tkinter import filedialog, messagebox, ttk

        deps = UiDependencies(tk=tk, ttk=ttk, filedialog=filedialog, messagebox=messagebox)
    return MidiInspirationApp(root, deps)


def launch_ui() -> None:
    """Launch the Tkinter application and start the main loop."""

    try:
        import tkinter as tk  # type: ignore
        from tkinter import filedialog, messagebox, ttk
    except ImportError as exc:  # pragma: no cover - platform dependent
        raise RuntimeError("Tkinter is not available on this platform.") from exc

    try:
        root = tk.Tk()
    except tk.TclError as exc:  # pragma: no cover - platform dependent
        raise RuntimeError("Unable to initialize Tkinter.") from exc

    app = MidiInspirationApp(
        root,
        UiDependencies(tk=tk, ttk=ttk, filedialog=filedialog, messagebox=messagebox),
    )
    app.run()
