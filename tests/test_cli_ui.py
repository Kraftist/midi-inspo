import types

import pytest

import midi_inspo.__main__ as cli
from midi_inspo.ui import MidiInspirationApp, UiDependencies


class DummyVar:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class DummyText:
    def __init__(self):
        self.value = ""

    def delete(self, start, end):
        self.value = ""

    def insert(self, start, text):
        self.value = text

    def pack(self, *_, **__):
        return None


class DummyWidget:
    def pack(self, *_, **__):
        return None


class DummyFileDialog:
    def __init__(self):
        self.calls = []

    def askopenfilename(self, **kwargs):
        self.calls.append(kwargs)
        return ""


class DummyMessageBox:
    def __init__(self):
        self.messages = []

    def showinfo(self, title, message):
        self.messages.append((title, message))

    def showerror(self, title, message):
        self.messages.append((title, message))


class DummyGenerator:
    def __init__(self, features):
        self.features = features

    def generate_ideas(self, **kwargs):
        return "dummy output"


class DummyRoot:
    def __init__(self):
        self.methods = []

    def title(self, value):
        self.methods.append(("title", value))

    def geometry(self, value):
        self.methods.append(("geometry", value))

    def mainloop(self):
        self.methods.append(("mainloop", None))


def test_cli_ui_flag_invokes_helper(monkeypatch):
    called = {}

    def fake_launch():
        called["value"] = True
        return 0

    monkeypatch.setattr(cli, "launch_ui", fake_launch)
    exit_code = cli.main(["--ui"])
    assert exit_code == 0
    assert called["value"] is True


@pytest.mark.parametrize("show_features,show_json", [(False, False), (True, False)])
def test_create_app_builds_interface(show_features, show_json):
    deps = UiDependencies(
        tk=types.SimpleNamespace(StringVar=DummyVar, BooleanVar=DummyVar, Text=lambda *a, **k: DummyText()),
        ttk=types.SimpleNamespace(
            Frame=lambda *a, **k: DummyWidget(),
            Label=lambda *a, **k: DummyWidget(),
            Entry=lambda *a, **k: DummyWidget(),
            Button=lambda *a, **k: DummyWidget(),
            Checkbutton=lambda *a, **k: DummyWidget(),
        ),
        filedialog=DummyFileDialog(),
        messagebox=DummyMessageBox(),
    )

    root = DummyRoot()
    app = MidiInspirationApp(root, deps, generator_factory=DummyGenerator)
    app.show_features.set(show_features)
    app.show_json.set(show_json)

    # Without a file path the UI should prompt the user instead of crashing.
    app.generate_ideas()
    assert deps.messagebox.messages


