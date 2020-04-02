import sys


def down():
    sys.stdout.write('\n')
    sys.stdout.flush()


def up():
    sys.stdout.write('\x1b[1A')
    sys.stdout.flush()
