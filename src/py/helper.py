from os import path
from glob import glob

script_dir = path.dirname(path.realpath(__file__))

def parse_test(t):
    with open(t) as f:
        text = f.read()
        sections = [s for s in text.split("\n-----\n")]
        return [path.basename(t), *sections]


def tests():
    needle = path.join(script_dir, "../tests/*.txt")
    return [parse_test(t) for t in glob(needle)]

