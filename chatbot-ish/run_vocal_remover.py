import os
import subprocess

INSTRUMENTS = ["mix", "vocal"]
OUT_LOC = 'chatbot-ish/processed_files'
# Ensure this is correct, you had 'chatboot-ish' which might be a typo
IN_LOC = 'chatbot-ish/uploaded_files'


def run_vocal_remover(filename):
    # You can directly initialize the list with the filename
    song_names = [filename]

    for song_name in song_names:
        name_split = song_name.split(".")[0]
        pre_folder = name_split[:]  # This is just a copy of name_split

        # Ensure the file exists before passing to subprocess
        in_loc = f"{IN_LOC}/{song_name}"

        # Provide the full path to 'inference.py'
        script_path = "C:/Users/birth/Desktop/새 폴더/nvidia-voice-audio-chatbot/chatbot-ish/vocal_remover/inference.py"

        commands = [
            ["python", script_path, "--input", in_loc,
                "--output_dir", OUT_LOC, "--gpu", "0"]
        ]

        for instrument in INSTRUMENTS:
            commands.append(
                [
                    "mv",
                    f"{OUT_LOC}/{name_split}/{instrument}.*",
                    f"{OUT_LOC}/{pre_folder}_{instrument}.wav",
                ]
            )
        commands.append(["rm", "-r", f"{OUT_LOC}/{name_split}"])

        for command in commands:
            subprocess.call(command)
