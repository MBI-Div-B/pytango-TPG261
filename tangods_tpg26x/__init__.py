from .TPG26xTango import TPG26xTango


def main():
    import sys
    import tango.server

    args = ["TPG26xTango"] + sys.argv[1:]
    tango.server.run((TPG26xTango,), args=args)
