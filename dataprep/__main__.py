import sys

from dataprep.cli.spec import parse_and_run


def main():
    parse_and_run(sys.argv[1:])


if __name__ == '__main__':
    main()
