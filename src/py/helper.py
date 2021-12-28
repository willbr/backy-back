from os import path
from glob import glob

script_dir = path.dirname(path.realpath(__file__))

def parse_output(o):
    return '\n'.join([x.strip() for x in o.split('\n')])


def parse_test(t):
    with open(t) as f:
        sections = [s.strip() for s in f.read().split("-----")]
        return [path.basename(t), *sections]


def tests():
    needle = path.join(script_dir, "../tests/*.txt")
    return [parse_test(t) for t in glob(needle)]

