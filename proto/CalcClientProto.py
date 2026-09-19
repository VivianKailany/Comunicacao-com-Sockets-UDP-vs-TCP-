
import socket
import argparse
import random
import time
import struct

import calc_pb2

OPS = ['+', '-', '*', '/']


def recv_exact(conn, n):
    data = b''
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_message(conn, message):
    payload = message.SerializeToString()
    header = struct.pack('!I', len(payload))
    conn.sendall(header + payload)
    return len(header) + len(payload)


def recv_message(conn, message_cls):
    header = recv_exact(conn, 4)
    if header is None:
        return None, 0
    (length,) = struct.unpack('!I', header)
    payload = recv_exact(conn, length)
    if payload is None:
        return None, 0
    message = message_cls()
    message.ParseFromString(payload)
    return message, 4 + length


def main():
    parser = argparse.ArgumentParser(description="Cliente TCP+Protobuf da calculadora remota")
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=9002)
    parser.add_argument('-n', '--num-requests', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))

    rtts = []
    sent_bytes = []
    recv_bytes = []
    start_total = time.perf_counter()

    for n in range(args.num_requests):
        req = calc_pb2.CalcRequest()
        req.n = n
        req.operand1 = round(random.uniform(-100, 100), 2)
        req.operand2 = round(random.uniform(-100, 100), 2)
        req.op = random.choice(OPS)

        t0 = time.perf_counter()
        nbytes_sent = send_message(sock, req)
        resp, nbytes_recv = recv_message(sock, calc_pb2.CalcResponse)
        rtt = (time.perf_counter() - t0) * 1000

        rtts.append(rtt)
        sent_bytes.append(nbytes_sent)
        recv_bytes.append(nbytes_recv)

        request_text = (
            f"CALC:{req.n}:{req.operand1}:{req.op}:{req.operand2}"
        )

        if resp.success:
            response_text = (
                f"RESULT:{resp.n}:{resp.result:.2f}"
            )
        else:
            response_text = (
                f"ERROR:{resp.n}:{resp.error}"
            )

        print(
            f"[{n:02d}] "
            f"Cliente → {request_text:<30} | "
            f"Servidor → {response_text:<30} | "
            f"RTT: {rtt:>5.1f} ms | "
            f"Env: {nbytes_sent:>2} B | "
            f"Resp: {nbytes_recv:>2} B"
        )

    total_time = (time.perf_counter() - start_total) * 1000
    sock.close()

    all_sizes = sent_bytes + recv_bytes
    avg_msg_size = sum(all_sizes) / len(all_sizes)

    print("\n" + "=" * 100)
    print("                         ESTATÍSTICAS TCP + PROTOBUF")
    print("=" * 100)

    print(f"{'Requisições enviadas:':<55}{args.num_requests}")
    print(f"{'Requisições respondidas:':<55}{len(rtts)}")
    print(f"{'Tempo total da sequência:':<55}{total_time:.1f} ms")
    print(f"{'RTT médio:':<55}{sum(rtts) / len(rtts):.1f} ms")
    print(f"{'RTT máximo:':<55}{max(rtts):.1f} ms")
    print(
        f"{'Tamanho médio das mensagens:':<55}"
        f"{avg_msg_size:.1f} bytes"
    )

    print("=" * 100)

if __name__ == '__main__':
    main()
