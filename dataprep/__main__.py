import sys

from dataprep import cli


def main():
    cli.parse_and_run(sys.argv[1:])


if __name__ == '__main__':
    main()
