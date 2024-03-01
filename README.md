The code is for the paper: "CaQR: A Compiler-Assisted Approach for Qubit Reuse through Dynamic Circuit". It is for resizing logical circuits. 

# Running the Benchmark

To run the file, please follow these steps:

## Installation

First, if Qiskit isn't installed, install it with version 0.45 using pip:

```bash
pip install qiskit==0.45
```
Then, you can run the main.py file. There are a few command line options.
1. -v 0 only outputs the result, and -v 1 outputs the circuit
2. -b is for specifying the benchmark
3. -w is for setting the weight of the cost function to strike a balance between qubit reuse and weight cost. The one we used for the paper is weight = 1. 

Below is an example of running the bv_n10 benchmark in the benchmarks folder. You must put all test qasm files in the "benchmarks" folder. 

```bash
python main.py -b benchmarks/bv_n10.qasm -v 0
```

The modified circuit will be in the output folder with ```_reuse``` appended to its file name. For the above example, the resulting code will be saved at ```output/bv_n10_reuse.qasm```. Additional files ending with ```_reuse_chain.txt``` and ```_reuse_map.txt``` will also be created, for verification purpose. 

To verify the output, run validate.py. Below is an example using bv_n10: 
```bash 
python validate.py bv_n10
```

Note that you must run the "main.py" to generate the output for one benchmark file before you run "validate.py" on the same benchmark. For running "validate.py", you do not have to specify the path of the benchmark, as the path is hardcoded. 

