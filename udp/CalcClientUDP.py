#!/usr/bin/env python3

import argparse
import random
import socket
import time

OPS = ['+', '-', '*', '/']

def gen_request(n):
    op1 = round(random.uniform(-100, 100), 2)
    op2 = round(random.uniform(-100, 100), 2)
    op = random.choice(OPS)
    return f"CALC:{n}:{op1}:{op}:{op2}"

def main():
    parser = argparse.ArgumentParser(description='Cliente UDP da Calculator remota')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host do servidor')
    parser.add_argument('--port', type=int, default=9000, help='Porta')
    parser.add_argument('-n', type=int, default=20, help='Número de requisições')
    parser.add_argument('--timeout', type=int, default=500, help='Timeout em ms antes de retrasmitir')
    parser.add_argument('--retries', type=int, default=5, help='Número máximo de retransmissões')
    parser.add_argument('--seed', type=int, default=42, help='Semente para geração de números aleatórios')
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout / 1000.0)
    server_address = (args.host, args.port)

    rtts = []
    total_retries = 0
    lost_requests = []
    sent_bytes = []
    recved_bytes = []

    start_total = time.perf_counter()

    for i in range(args.n):
        request = gen_request(i)
        attempts = 0
        got_response = False

        while attempts < args.retries and not got_response:
            attempts += 1
            t0 = time.perf_counter()
            payload = request.encode('utf-8')
            sock.sendto(payload, server_address)
            try:
                data, _ = sock.recvfrom(4096)
                rtt = (time.perf_counter() - t0) * 1000
                response = data.decode('utf-8')
                rtts.append(rtt)
                sent_bytes.append(len(payload))
                recved_bytes.append(len(data))
                got_response = True

                if attempts > 1:
                    total_retries += (attempts - 1)
                print(f"[{i:02d}] {request}  ->  {response}   (RTT={rtt:.1f} ms, tentativa {attempts})")
            except socket.timeout:
                print(f"[{i:02d}] timeout na tentativa {attempts}/{args.retries} — reenviando...")

        if not got_response:
            total_retries += (attempts - 1)
            lost_requests.append(i)
            print(f"[{i:02d}] request perdida após {args.retries} tentativas")

    total_time = (time.perf_counter() - start_total) * 1000 # ms


    print("\n----- Estatísticas -----")
    print(f"Total de requisições enviadas: {args.n}")
    print(f"Requisições recebidas: {len(rtts)}")
    print(f"Requisições perdidas definitivamente: {len(lost_requests)} {lost_requests}")

    print(f"Total de retransmissões: {total_retries}")
    print(f"Tempo total da sequencia: {total_time:.1f} ms")
    if rtts:
        print(f"RTT máximo: {max(rtts):.1f} ms")
        print(f"RTT médio: {sum(rtts)/len(rtts):.1f} ms")
    else:
        print("Nenhuma resposta recebida, não é possível calcular RTT.")

if __name__ == "__main__":
    main()