import argparse

from guacamole.xo.game_server import GameServer


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Hostname', required=False, dest='host', default="0.0.0.0")
    parser.add_argument('--port', help='port', required=False, default=50000, dest='port', type=int)
    args = parser.parse_args()
    return args.host, args.port


def main():
    host, port = get_args()
    client = GameServer(host=host, port=port)
    client.start()


if __name__ == '__main__':
    main()
