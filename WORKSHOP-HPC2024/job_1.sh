#!/bin/bash

#SBATCH --job-name=fancy-hello
#SBATCH --nodelist=a1
#SBATCH --partition=short
#SBATCH --gres=gpu:1

# Your script goes here
date;
python fancy_hello.py
date;