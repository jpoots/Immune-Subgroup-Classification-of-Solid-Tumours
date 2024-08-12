#!/bin/bash
#SBATCH --output=op_rf.output
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jpoots04@qub.ac.uk
#SBATCH --partition=k2-gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --mem-per-cpu=2G
#SBATCH --nodes=1
#SBATCH --job-name=op_rf

module load apps/anaconda3/2024.06/bin

conda create --name cancer
source activate cancer
conda install -c conda-forge imbalanced-learn
conda install anaconda::pandas
conda install conda-forge::matplotlib
python op_rf.py
