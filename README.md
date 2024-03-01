# Running the Benchmark

To run the file, please follow these steps:

## Installation

First, if Qiskit isntalled, install it with version 0.45 using pip:

```bash
pip install qiskit==0.45
```
Then, run the main file.
verbose 0 only output the result
verbose 1 will output the circuit
The below example outputs for bv_n10 in the benchmarks.
```bash
python main.py -b benchmarks/bv_n10.qasm -v 0
```
The modified circuit will be found in the output folder with ```_reuse``` appended to its file name. For the above example, the resulting code will be saved at ```output/bv_n10_reuse.qasm```. Additional files ending with ```_reuse_chain.txt``` and ```_reuse_map.txt``` will also be created.

To verify the output files, run validate.py. Below is an example using bv_n10: 
```bash 
python validate.py bv_n10
```

