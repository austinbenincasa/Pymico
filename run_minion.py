import argparse
from core.minion import Minion


def run(config):
    minion = Minion()
    minion.init(config)
    minion.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Minion Help')
    parser.add_argument('--config', action='store', dest='config', help='Path to config file')
    args = parser.parse_args()
    if args.config:
        run(args.config)
    else:
        run(None)
