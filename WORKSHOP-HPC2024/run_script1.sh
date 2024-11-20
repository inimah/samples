#!/bin/bash
#SBATCH --job-name=test-1
#SBATCH --nodelist=a100
#SBATCH --partition=short
#SBATCH --gres=gpu:1

source /home/ifti001/miniconda3/etc/profile.d/conda.sh
conda activate my_env


python python_script1.py 