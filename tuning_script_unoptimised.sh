#!/bin/bash
#SBATCH --output=tuning_unoptimised.output
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jpoots04@qub.ac.uk
#SBATCH --partition=k2-medpri
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=2G
#SBATCH --nodes=1

module load apps/anaconda3/2022.10/bin

conda create --name cancer
source activate cancer
conda install -c conda-forge imbalanced-learn
conda install anaconda::pandas
conda install conda-forge::matplotlib
python model_tuning_optimised.py
