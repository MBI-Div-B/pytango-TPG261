from .TPG261 import TPG261


def main():
    import sys
    import tango.server

    args = ["TPG261"] + sys.argv[1:]
    tango.server.run((TPG261,), args=args)
