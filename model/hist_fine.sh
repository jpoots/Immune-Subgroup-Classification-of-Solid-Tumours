#!/bin/bash
#SBATCH --output=hist_fine.output
#SBATCH --time=2-00:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jpoots04@qub.ac.uk
#SBATCH --partition=k2-lowpri
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --mem-per-cpu=2G
#SBATCH --nodes=1
#SBATCH --job-name=h_fine

module load apps/anaconda3/2022.10/bin

conda create --name cancer
source activate cancer
conda install -c conda-forge imbalanced-learn
conda install anaconda::pandas
conda install conda-forge::matplotlib
python hist_fine.py
