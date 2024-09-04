#!/bin/bash
#SBATCH --output=xgboost.output
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jpoots04@qub.ac.uk
#SBATCH --partition=k2-himem
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --mem-per-cpu=2G
#SBATCH --nodes=1
#SBATCH --job-name=xgboost

module load apps/anaconda3/2024.06/bin

source activate cancer
python xgboost_tuning.py
