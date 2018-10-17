import argparse
from core.master import Master

def run(config, cli):
    master = Master(cli)
    master.init(config)
    master.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Master Help')
    parser.add_argument('--config', action='store', dest='config', help='Store a simple value')
    parser.add_argument('--cli', action='store_true', help='Whether to start master with CLI or headless')
    args = parser.parse_args()
    if args.config:
        run(args.config, args.cli)
    else:
        run(None, args.cli)