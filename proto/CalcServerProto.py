
import socket
import argparse
import threading
import struct

import calc_pb2


def compute(op1, op, op2):
    if op == '+':
        return op1 + op2
    elif op == '-':
        return op1 - op2
    elif op == '*':
        return op1 * op2
    elif op == '/':
        if op2 == 0:
            raise ZeroDivisionError("divisão por zero")
        return op1 / op2
    else:
        raise ValueError(f"operação inválida: {op}")


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


def recv_message(conn, message_cls):
    header = recv_exact(conn, 4)
    if header is None:
        return None
    (length,) = struct.unpack('!I', header)
    payload = recv_exact(conn, length)
    if payload is None:
        return None
    message = message_cls()
    message.ParseFromString(payload)
    return message


def handle_client(conn, addr):
    print(f"[PROTO] nova conexão de {addr}")
    try:
        with conn:
            while True:
                req = recv_message(conn, calc_pb2.CalcRequest)
                if req is None:
                    break
                resp = calc_pb2.CalcResponse()
                resp.n = req.n
                try:
                    resp.result = compute(req.operand1, req.op, req.operand2)
                    resp.success = True
                except (ZeroDivisionError, ValueError, ArithmeticError) as e:
                    resp.success = False
                    resp.error = str(e)
                send_message(conn, resp)
                status = f"RESULT:{resp.result}" if resp.success else f"ERROR:{resp.error}"
                print(
                    f"[PROTO] {addr} | "
                    f"Cliente → CALC:{req.n}:{req.operand1}:{req.op}:{req.operand2:<15} | "
                    f"Servidor → {status}"
                )
    except (ConnectionResetError, BrokenPipeError):
        print(f"[PROTO] conexão com {addr} foi interrompida.")
    finally:
        print(f"[PROTO] conexão encerrada com {addr}")


def main():
    parser = argparse.ArgumentParser(description="Servidor TCP+Protobuf da calculadora remota")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=9002)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))
    sock.listen(5)
    print(f"[PROTO] servidor escutando em {args.host}:{args.port}")

    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[PROTO] encerrando servidor.")
    finally:
        sock.close()

if __name__ == '__main__':
    main()