# Atividade: Comunicação com Sockets — UDP vs. TCP

## Como rodar parte 1, 2 e 4

### Parte 1 — UDP

Terminal 1:
```bash
cd udp
python3 CalcServerUDP.py --port 9000 --loss-rate 0.0
```

Terminal 2:
```bash
cd udp
python3 CalcClientUDP.py --host 127.0.0.1 --port 9000 -n 20
```

### Parte 2 — TCP

Terminal 1:
```bash
cd tcp
python3 CalcServerTCP.py --port 9001
```

Terminal 2 (cliente):
```bash
cd tcp
python3 CalcClientTCP.py --host 127.0.0.1 --port 9001 -n 20
```
### Parte 4 — TCP + Protobuf

```bash
cd proto
protoc --python_out=. calc.proto
```
Terminal 1:
```bash
cd proto
python3 CalcServerProto.py --port 9002
```

Terminal 2:
```bash
cd proto
python3 CalcClientProto.py --host 127.0.0.1 --port 9002 -n 20
```

## Resultado: Parte 3 — Rodando o experimento pedido (0%, 10%, 30% de perda + TCP)

Isso já foi executado e os resultados estão salvos em `results/`. Um resumo comparativo está na tabela do `RESPOSTAS.md`.

