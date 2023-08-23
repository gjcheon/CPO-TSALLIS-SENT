python main.py --name CPO-HalfCheetah-No-Tsallis --seed 1 --env_name HalfCheetah-v3 --beta_intr 0.0 --gpu_idx 0 --wandb
python main.py --name CPO-HalfCheetah-Tsallis-q=1.0 --seed 1 --env_name HalfCheetah-v3 --beta_intr 0.03 --tsallis_q 1.0 --gpu_idx 0 --wandb
python main.py --name CPO-HalfCheetah-Tsallis-q=1.2 --seed 1 --env_name HalfCheetah-v3 --beta_intr 0.03 --tsallis_q 1.2 --gpu_idx 0 --wandb