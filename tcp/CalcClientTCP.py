import socket
import argparse
import random
import time

OPS = ['+', '-', '*', '/']


def gen_request(n):
    op1 = round(random.uniform(-100, 100), 2)
    op2 = round(random.uniform(-100, 100), 2)
    op = random.choice(OPS)
    return f"CALC:{n}:{op1}:{op}:{op2}"


def main():
    parser = argparse.ArgumentParser(description="Cliente TCP da calculadora remota")
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=9001)
    parser.add_argument('-n', '--num-requests', type=int, default=20)
    parser.add_argument('--seed', type=int, default=None)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))
    sock_file = sock.makefile('r', encoding='utf-8')

    rtts = []
    sent_bytes = []
    recv_bytes = []
    start_total = time.perf_counter()

    for n in range(args.num_requests):
        request = gen_request(n)
        payload = (request + "\n").encode('utf-8')
        t0 = time.perf_counter()
        sock.sendall(payload)
        line = sock_file.readline()
        rtt = (time.perf_counter() - t0) * 1000
        response = line.strip()
        rtts.append(rtt)
        sent_bytes.append(len(payload))
        recv_bytes.append(len(line.encode('utf-8')))
        print(f"[{n:02d}] {request}  ->  {response}   (RTT={rtt:.1f} ms)")

    total_time = (time.perf_counter() - start_total) * 1000
    sock.close()

    print("\n----- Estatísticas (TCP) -----")
    print(f"Requisições enviadas: {args.num_requests}")
    print(f"Requisições respondidas: {len(rtts)}")
    print(f"Tempo total da sequência: {total_time:.1f} ms")
    if rtts:
        print(f"RTT médio: {sum(rtts) / len(rtts):.1f} ms")
        print(f"RTT máximo: {max(rtts):.1f} ms")


if __name__ == '__main__':
    main()
