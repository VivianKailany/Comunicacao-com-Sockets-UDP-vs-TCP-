import socket
import argparse
import threading


def compute(op1, op, op2):
    op1 = float(op1)
    op2 = float(op2)
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


def handle_client(conn, addr):
    print(f"[TCP] nova conexão de {addr}")
    try:
        with conn:
            conn_file = conn.makefile('r', encoding='utf-8')
            for line in conn_file:
                msg = line.strip()
                if not msg:
                    continue
                parts = msg.split(':')
                if len(parts) != 5 or parts[0] != 'CALC':
                    continue
                _, n, op1, op, op2 = parts
                try:
                    result = compute(op1, op, op2)
                    response = f"RESULT:{n}:{result:.2f}\n"
                except (ZeroDivisionError, ValueError, ArithmeticError) as e:
                    response = f"ERROR:{n}:{e}\n"
                conn.sendall(response.encode('utf-8'))
                print(
                    f"[TCP] {addr} | "
                    f"Cliente → {msg:<25} | "
                    f"Servidor → {response.strip()}"
                )
    except (ConnectionResetError, BrokenPipeError):
        print(f"[TCP] conexão com {addr} foi interrompida.")
    finally:
        print(f"[TCP] conexão encerrada com {addr}")


def main():
    parser = argparse.ArgumentParser(description="Servidor TCP da calculadora remota")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=9001)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))
    sock.listen(5)
    print(f"[TCP] servidor escutando em {args.host}:{args.port}")

    try:
        while True:
            conn, addr = sock.accept()
            # uma thread por cliente -> vários clientes concorrentes, sem travar
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[TCP] encerrando servidor.")
    finally:
        sock.close()


if __name__ == '__main__':
    main()