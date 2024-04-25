import subprocess
import os

# music separation
model_steps = '50' # [50, 75, 100, 130, 210]
model_data = 'vocadb'
song_names = [
    # 'itte_mixture.mp3'
    'melancholic_mixture.mp3',
    # 'raspberry_monster_mixture.wav',
    # 'melt_mixture.wav',
    # 'amanojaku_mixture.wav',
    # 'black_rock_shooter_mixture.wav',
    # 'loki_mixture.wav',
    # 'tengaku_mixture.wav',
    # 'world_is_mine_mixture.wav'
]

instruments = ['bass', 'drums', 'other', 'vocals']

for song_name in song_names:
    name_split = song_name.split('.')[0]
    short_name = name_split.split('_')[0]
    pre_folder = name_split[:-7]
    out_loc = f'processed_files/vocadb_{model_steps}k/{pre_folder}{model_steps}k'
    in_loc = f'uploaded_files/{song_name}'

    commands = [
        ['spleeter', 'separate', '-o', out_loc, '-p', 'spleeter:4stems', in_loc]
    ]

    for i in instruments:
        commands.append(['mv', f'{out_loc}/{name_split}/{i}.*', f'{out_loc}/{short_name}_{model_steps}k_{i}.wav'])
    commands.append(['rm', '-r', f'{out_loc}/{name_split}'])

    for command in commands:
        subprocess.call(command)