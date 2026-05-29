"""Simulator-free tests for CocotbInjector under the cocotb 2.0 API.

These fake the cocotb handle hierarchy so the read->LogicArray->Force->set
injection path can be regression-tested without a commercial simulator.
"""
from cocotb.types import LogicArray
from cocotb.handle import Force
from injector.cocotb_injector import CocotbInjector


class FakeHandle:
    def __init__(self, name="top"):
        self._name = name
        self._children = {}
        self.forced = None

    def __getattr__(self, child):
        if child.startswith("_"):
            raise AttributeError(child)
        h = self._children.get(child)
        if h is None:
            h = FakeHandle(f"{self._name}.{child}")
            self._children[child] = h
        return h

    def set(self, action):
        assert isinstance(action, Force), f"expected Force, got {type(action)!r}"
        self.forced = str(action.value)


def test_inject_scalar_vector_and_x():
    dut = FakeHandle("top")
    inj = CocotbInjector(dut)
    inj.inject_values({
        "top.block_i.clk":  "1",
        "top.block_i.din":  "0",
        "top.block_i.ctr":  "101",   # multi-bit vector
        "top.block_i.dout": "x",     # X state
    })
    blk = dut.block_i
    assert blk.clk.forced == "1"
    assert blk.din.forced == "0"
    assert blk.ctr.forced == "101"
    assert blk.dout.forced.lower() == "x"
    assert inj.error_signals == []


def test_struct_values_are_skipped():
    dut = FakeHandle("top")
    inj = CocotbInjector(dut)
    # packed struct / array dumps contain '{' and are intentionally skipped
    inj.inject_values({"top.block_i.bus": "{0 1 2}"})
    assert dut.block_i.bus.forced is None
