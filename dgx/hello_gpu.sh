#!/bin/bash
#SBATCH --job-name=test
#SBATCH --partition=short
#SBATCH --gres=gpu:1
#SBATCH --mem=4
#SBATCH --out=test.out

conda activate rapids-24.04
python test.py
