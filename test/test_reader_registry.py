"""Tests for the pluggable wave-reader registry in wave.reader.

These verify the extension point itself: dispatch by file extension and
the error path for an unregistered format. No simulator needed.
"""
import cocotb
import pytest

import wave.reader as reader_mod
from wave.reader import read_wave, WAVE_READERS


class _FakeReader:
    def __init__(self, replay_block, wavefile, excluded_sigs, inputs_only):
        self.replay_block = replay_block
        self.wavefile = wavefile
        self.excluded_sigs = excluded_sigs
        self.inputs_only = inputs_only


@pytest.fixture
def fake_args(monkeypatch):
    # read_argument first consults cocotb.plusargs; feed everything from there
    # so the tests don't depend on a test_customization.py being importable.
    monkeypatch.setattr(cocotb, "plusargs", {
        "wavefile": "dummy.fake",
        "replay_block": "top.block_i",
        "inputs_only": True,
        "excluded_sigs": [],
    }, raising=False)
    yield


def test_registry_dispatches_by_extension(monkeypatch, fake_args):
    monkeypatch.setitem(WAVE_READERS, "fake", lambda: _FakeReader)
    data = read_wave()
    assert isinstance(data, _FakeReader)
    assert data.wavefile == "dummy.fake"
    assert data.replay_block == "top.block_i"


def test_unsupported_format_raises_and_lists_supported(monkeypatch):
    monkeypatch.setattr(cocotb, "plusargs", {
        "wavefile": "dummy.nope",
        "replay_block": "top",
        "inputs_only": True,
        "excluded_sigs": [],
    }, raising=False)
    with pytest.raises(ValueError) as exc:
        read_wave()
    # the supported-format list in the message is derived from the registry
    assert "nope" in str(exc.value)
    assert "vcd" in str(exc.value)


def test_vcd_is_registered():
    assert "vcd" in WAVE_READERS
