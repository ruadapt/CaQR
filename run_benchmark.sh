#!/bin/bash

# Define the output file
output_file="benchmark_results.txt"

# Clear the output file at the start
> "$output_file"

# Loop through each .qasm file in the benchmarks directory
for file in benchmarks/*.qasm; do
    echo "Running benchmark on $file" >> "$output_file"
    python main.py -b "$file" -v 0 >> "$output_file"
    echo "---------------------------------" >> "$output_file"
done

echo "Benchmarks completed."
