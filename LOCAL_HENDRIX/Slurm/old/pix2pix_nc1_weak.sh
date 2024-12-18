#!/bin/bash
# normal cpu stuff: allocate cpus, memory
#SBATCH --ntasks=1 --cpus-per-task=10 --mem=6000M
#SBATCH -p gpu --gres=gpu:titanrtx:1
#SBATCH --time=5-24:00:00

echo "Prepping cluster:"

echo "using gpus:"
echo $CUDA_VISIBLE_DEVICES

module load pytorch

module load cuda

echo "Training:"

cd pix2pix_weak_D

# python3 train.py --dataroot ./datasets/mr2ct_pix2pix_nc1 --name mr2ct_pix2pix_nc1 --model pix2pix --display_id -1 --load_size 266 --input_nc 1 --output_nc 1 --n_epochs 2500 --batch_size 32 --gpu_ids 0,1,2,3  --epoch_count 113 --continue_train 
python3 train.py --dataroot ./datasets/mr2ct_pix2pix_nc1 --name mr2ct_pix2pix_nc1_weak --model pix2pix --display_id -1 --load_size 266 --input_nc 1 --output_nc 1 --n_epochs 2500 --epoch_count 57 --continue_train