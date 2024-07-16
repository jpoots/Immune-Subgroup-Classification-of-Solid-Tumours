#!/bin/bash
#SBATCH --output=hist_finer.output
#SBATCH --time=4-00:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jpoots04@qub.ac.uk
#SBATCH --partition=k2-himem
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=50
#SBATCH --mem-per-cpu=2G
#SBATCH --nodes=1
#SBATCH --job-name=h_finer

module load apps/anaconda3/2022.10/bin

conda create --name cancer
source activate cancer
conda install -c conda-forge imbalanced-learn
conda install anaconda::pandas
conda install conda-forge::matplotlib
python hist_finer.py
