#!/bin/bash
#SBATCH --job-name=hello_world_omp      	# Job name
#SBATCH --partition=short                       # short | medium-small | medium-large | long | very-long
#SBATCH --ntasks=32                             # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=1                               # Maximum number of nodes to be allocated
#SBATCH --ntasks-per-node=32                    # Maximum number of tasks on each node
#SBATCH --output=hello_world_omp-%j.log         # Path to the standard output and error files relative to the working directory
echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""
echo "Number of Nodes Allocated      = $SLURM_JOB_NUM_NODES"
echo "Number of Tasks Allocated      = $SLURM_NTASKS"
echo "Number of Cores/Task Allocated = $SLURM_CPUS_PER_TASK"

/mgpfs/home/i[your_user]/samples/omp/hello_world_omp

echo "Finish            = $(date)"
