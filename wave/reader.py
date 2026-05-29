import cocotb

test_arguments_exist = True

try:
    from test_customization import Arguments
except:
    test_arguments_exist = False


def read_argument(name, optional=False):
    if name in cocotb.plusargs:
        return cocotb.plusargs[name]
    elif hasattr(Arguments,name):
        return getattr(Arguments,name)

    if not optional:
        raise ValueError("Argument ", name, " is required and must be provided via plusarg or a test_cusomization.py file on path")
    else:
        return None


# Registry mapping a wave-file extension to a zero-arg factory returning its
# reader class. Factories import lazily so a format whose backend isn't
# installed (e.g. a future fsdb reader needing a vendor lib) only fails if you
# actually try to use that format.
#
# To add a new format: implement a ReaderBase subclass in wave/<fmt>_reader.py,
# then register it here -- read_wave() itself needs no changes.
def _vcd_reader():
    from wave.vcd_reader import VcdReader
    return VcdReader


WAVE_READERS = {
    'vcd': _vcd_reader,
}


def read_wave():
    wavefile = read_argument('wavefile')
    wave_type = wavefile.split('.')[-1]

    if wave_type not in WAVE_READERS:
        raise ValueError("Wavefile type: ", wave_type,
                         " is currently not supported. Supported formats are: ",
                         sorted(WAVE_READERS.keys()))

    replay_block = read_argument('replay_block')

    # optional args
    inputs_only = read_argument('inputs_only')
    excluded_sigs = read_argument('excluded_sigs')

    reader_cls = WAVE_READERS[wave_type]()
    return reader_cls(replay_block, wavefile, excluded_sigs, inputs_only)
