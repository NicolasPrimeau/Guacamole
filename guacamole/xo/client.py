import argparse

from guacamole.xo.game_client import GameClient


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Hostname', required=False, dest='host', default='localhost')
    parser.add_argument('--port', help='port', required=False, default=50000, dest='port', type=int)
    parser.add_argument('--restart', help='Restart', action='store_true', dest='restart')
    args = parser.parse_args()
    return args.host, args.port, args.restart


def main():
    host, port, restart = get_args()
    client = GameClient(host=host, port=port, restart=restart)
    client.start()


if __name__ == '__main__':
    main()
