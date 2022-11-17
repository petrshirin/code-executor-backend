#!/bin/bash
touch ./run_file.py
for var in "$@"
do
    echo "$var" >> ./run_file.py
done
python ./run_file.py
