#!/bin/bash

# Define the output file
output_file="benchmark_results.txt"

# Clear the output file at the start
> "$output_file"

# Loop through each .qasm file in the benchmarks directory
for file in benchmarks/*.qasm; do
    filebase=$(echo $file | sed 's/^benchmarks\/\([^.]*\)\.qasm/\1/')
    echo "Running benchmark on $filebase" >> "$output_file"
    python3 main.py -b "$file" -v 0 >> "$output_file"
    python3 validate.py "$filebase">> "$output_file"
    echo "---------------------------------" >> "$output_file"
done

echo "Benchmarks completed."
