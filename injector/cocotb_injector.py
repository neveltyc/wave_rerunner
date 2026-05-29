# Adapted to cocotb 2.0 API:
#   - cocotb.binary.BinaryValue (removed) -> cocotb.types.LogicArray
#   - handle assignment `sig <= Force(v)` (removed) -> `sig.set(Force(v))`
#   - cocotb.handle.NonHierarchyIndexableObject (removed) -> no longer imported
from cocotb.types import LogicArray
from cocotb.handle import Force

from injector.injector_base import InjectorBase

from functools import reduce

class CocotbInjector(InjectorBase):
    def __init__(self, dut, prefix = ""):
        self.coco_dut = dut
        self.prefix = prefix
        self.error_signals = []

        super().__init__()

    def remove_prefix(self, str, prefix):
        if str.startswith(prefix):
            return str[len(prefix):]
        return str  # or whatever

    def get_cocotb_sig(self,sig_name):
         return reduce(getattr, self.remove_prefix(sig_name, self.prefix).split('.')[1:], self.coco_dut)


    def inject_values(self, values):
        for sig_name, value in values.items():
            # structs/arrays injection not supported yet.
            if '{' in value:
                print("skipping hier signal?: ", sig_name)
                continue

            if sig_name in self.error_signals:
                continue

            coco_sig = self.get_cocotb_sig(sig_name)

            bin_value = LogicArray(value)

            try:
                coco_sig.set(Force(bin_value))
            except ValueError:
                print("Value error. The values requested to inject are: ", values)
            except TypeError:
                self.error_signals.append(sig_name)
                print("Type error. Signal name is: ", sig_name, " sig value: ", value)
