# DDR Traffic and Refresh Performance Simulator

Reproducible FCFS and first-ready FCFS scheduling experiments, explicit bank row state, activation/precharge/CAS costs, periodic refresh stalls, CSV traces, and latency/throughput/row-hit metrics. The simulator serializes commands and models scheduler effects rather than physical DDR signaling.

## Run

Run `python -m unittest -v`, then `python simulator.py --workload mixed --count 1000`. A SystemVerilog sequential trace generator is included under rtl/.
