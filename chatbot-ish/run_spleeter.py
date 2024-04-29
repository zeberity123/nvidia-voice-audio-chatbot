import subprocess
import os

INSTRUMENTS = ["bass", "drums", "other", "vocals"]
OUT_LOC = 'processed_files'
IN_LOC = 'uploaded_files'

def run_spleeter(filename):
    song_names = []
    song_names.append(filename)

    for song_name in song_names:
        name_split = song_name.split(".")[0]
        pre_folder = name_split[:]

        in_loc = f"{IN_LOC}/{song_name}"

        commands = [
            ["spleeter", "separate", "-o", OUT_LOC,
                "-p", "spleeter:4stems", in_loc]
        ]

        for i in INSTRUMENTS:
            commands.append(
                [
                    "mv",
                    f"{OUT_LOC}/{name_split}/{i}.*",
                    f"{OUT_LOC}/{pre_folder}_{i}.wav",
                ]
            )
        commands.append(["rm", "-r", f"{OUT_LOC}/{name_split}"])

        for command in commands:
            subprocess.call(command)


def delete_files(filename):
    name_split = filename.split(".")[0]
    command = ['rm', f"{OUT_LOC}/{name_split}*.wav"]
    subprocess.call(command)
