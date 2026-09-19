# Respostas — Atividade Sockets UDP vs. TCP

## Resultados do experimento

| Execução        | Tempo total | RTT médio | RTT máximo | Retransmissões | Requisições perdidas |
| --------------- | ----------: | --------: | ---------: | -------------: | -------------------: |
| UDP — perda 0%  |     28,0 ms |    1,1 ms |     1,8 ms |              0 |                    0 |
| UDP — perda 10% |   1549,7 ms |    1,5 ms |     3,9 ms |              3 |                    0 |
| UDP — perda 30% |   6106,6 ms |    1,3 ms |     3,0 ms |             11 |                    1 |
| TCP             |     12,7 ms |    0,4 ms |     1,3 ms |              — |                    — |
| TCP + Protobuf  |     13,3 ms |    0,4 ms |     1,3 ms |              — |                    — |


| Formato        | Tamanho médio da mensagem |
| -------------- | ------------------------: |
| TCP            |                19,1 bytes |
| TCP + Protobuf |                21,9 bytes |


