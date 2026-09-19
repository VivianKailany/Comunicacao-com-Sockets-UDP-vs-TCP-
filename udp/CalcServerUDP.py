import socket
import random
import argparse
import threading

def compute_expression(expression):
    op1, operator, op2 = expression.split()
    op1 = float(op1)
    op2 = float(op2)
    if operator == '+':
        return op1 + op2
    elif operator == '-':
        return op1 - op2
    elif operator == '*':
        return op1 * op2
    elif operator == '/':
        if op2 == 0:
            raise ZeroDivisionError("divisão por zero")
        return op1 / op2
    else:
        raise ValueError(f"operação inválida: {operator}")

def handle_message(data, addr, sock, loss_rate, lock):
    try:
        msg = data.decode('utf-8').strip()
        parts = msg.split(':')
        if len(parts) != 5 or parts[0] != "CALC":
            return 
        _, n, op1, operator, op2 = parts

        if random.random() < loss_rate:
            with lock:
                print(f"[UDP] req {n} de {addr} recebida, mas descartada")
            return

        try:
            result = compute_expression(f"{op1} {operator} {op2}")
            response = f"RESULT:{n}:{result}"
        except (ZeroDivisionError, ValueError, ArithmeticError) as e:
            response = f"ERROR:{n}:{(e)}"

        sock.sendto(response.encode('utf-8'), addr)
        with lock:
            print(f"[UDP] {addr} -> {msg}  |  resposta -> {response}")
    except Exception as e:
        with lock:
            print(f"[UDP] erro ao processar mensagem de {addr}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Servidor UDP da Calculator remota')
    parser.add_argument('--host', type=str,default='0.0.0.0')
    parser.add_argument('--port', type=int, default=9000, help='Porta')
    parser.add_argument('--loss-rate', type=float, default=0.1, help='Taxa de perda de pacotes')
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    print(f"[UDP] Servidor iniciado em {args.host}:{args.port} com taxa de perda {args.loss_rate*100:.1f}%")

    lock = threading.Lock()

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_message, args=(data, addr, sock, args.loss_rate, lock)).start()
    except KeyboardInterrupt:
        print("[UDP] Servidor encerrado.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()