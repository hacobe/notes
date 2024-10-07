"""A lossy proxy downloaded from https://csprimer.com/watch/reliable-transport/

See also:
* reliable_transport.py
"""
import argparse
import random
import socket


def trunc(bs, n=10):
    s = str(bs.rstrip())
    return f'{s[:n]}... ({len(bs)}B)' if len(s) > n else s


def red(s):
    print(f'\033[91m{s}\033[0m')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream_host', help='Host to which the upstream server is bound', default='127.0.0.1')
    parser.add_argument('--upstream_port', type=int, help='Port to which the upstream server is bound', default=8000)
    parser.add_argument('--inbound_port', type=int, help='Port to which the client should send data', default=7000)
    parser.add_argument('--drop_rate', type=float, default=0.1)
    parser.add_argument('--dup_rate', type=float, default=0.1)
    parser.add_argument('--reorder_rate', type=float, default=0.1)
    args = parser.parse_args()

    upstream_addr = (args.upstream_host, args.upstream_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('0.0.0.0', args.inbound_port or 0))

    print(f'Forwarding from {sock.getsockname()} to {upstream_addr} and back')

    client_addr = None

    random.seed(1234)

    pending = []

    while True:
        data, from_addr = sock.recvfrom(4096)
        if from_addr[1] == args.upstream_port:
            to_addr = client_addr
            print(f'{"":>20}    * <- {trunc(data)}')
        else:
            client_addr = from_addr
            to_addr = upstream_addr
            print(f'{trunc(data):>20} -> *')

        if random.random() < args.drop_rate:
            red('dropping!')
            continue

        pending.append((data, to_addr))

        if random.random() < args.reorder_rate:
            red('reordering!')
            continue

        if random.random() < args.dup_rate:
            red('duplicating!')
            pending.append((data, to_addr))

        while pending:
            data, to_addr = pending.pop()
            if to_addr == client_addr:
                print(f'{trunc(data):>20} <- *')
            else:
                print(f'{"":>20}    * -> {trunc(data)}')
            sock.sendto(data, to_addr)
