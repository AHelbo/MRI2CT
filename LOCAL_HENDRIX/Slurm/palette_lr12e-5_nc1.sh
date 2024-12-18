#!/bin/bash
# normal cpu stuff: allocate cpus, memory
#SBATCH --ntasks=1 --cpus-per-task=10 --mem=16000M
#SBATCH -p gpu --gres=gpu:titanrtx:1
#SBATCH --time=6-24:00:00

echo "Prepping cluster:"

echo "using gpus:"
echo $CUDA_VISIBLE_DEVICES

echo "Training:"

cd ..

cd PALETTE

module load pytorch

module load cuda

source pal_env/bin/activate

python3 run.py -p train -c config/mr2ct_lr12e-5_nc1.json