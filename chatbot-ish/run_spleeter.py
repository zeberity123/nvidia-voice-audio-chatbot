import subprocess
import os


def run_spleeter(filename):
    song_names = []

    instruments = ["bass", "drums", "other", "vocals"]

    song_names.append(filename)

    for song_name in song_names:
        name_split = song_name.split(".")[0]
        pre_folder = name_split[:]

        out_loc = f"processed_files/"
        in_loc = f"uploaded_files/{song_name}"

        commands = [
            ["spleeter", "separate", "-o", out_loc,
                "-p", "spleeter:4stems", in_loc]
        ]

        for i in instruments:
            commands.append(
                [
                    "mv",
                    f"{out_loc}/{name_split}/{i}.*",
                    f"{out_loc}/{pre_folder}{i}.wav",
                ]
            )
        commands.append(["rm", "-r", f"{out_loc}/{name_split}"])

        for command in commands:
            subprocess.call(command)
