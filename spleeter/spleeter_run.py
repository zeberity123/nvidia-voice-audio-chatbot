import subprocess
import os

# python -m spleeter train -p configs/vocadb_config.json -d C:/musdb18hq --verbose

# spleeter separate -o results/melan_90k -p spleeter:4stems test_audio/melancholic_mixture.mp3

# music separation
model_steps = '130' # [50, 75, 100, 130]
model_data = 'vocadb'
song_names = [
    'melancholic_mixture.mp3',
    'raspberry_monster_mixture.wav',
    'melt_mixture.wav',
    'amanojaku_mixture.wav',
    # 'black_rock_shooter_mixture.wav',
    # 'loki_mixture.wav',
    # 'tengaku_mixture.wav',
    # 'world_is_mine_mixture.wav'
]

for song_name in song_names:
    pre_folder = song_name.split('mixture.')[0]
    out_loc = f'results/vocadb_{model_steps}k/{pre_folder}{model_steps}k_'
    in_loc = f'test_audio/{song_name}'
    command = ['spleeter', 'separate', '-o', out_loc, '-p', 'spleeter:4stems', in_loc]
    C:\Users\hancom05\Desktop\nvidia-voice-audio-chatbot\spleeter\results\vocadb_130k\melancholic_130k_\melancholic_mixture
    command = ['mv', ]


    subprocess.call(command)