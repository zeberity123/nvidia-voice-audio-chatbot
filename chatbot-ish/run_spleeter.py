import subprocess
import os

INSTRUMENTS = ["bass", "drums", "other", "vocals"]
OUT_LOC = 'processed_files'
IN_LOC = 'uploaded_files'


def run_spleeter(filename):
    # This can be simplified as you're appending only one filename.
    song_names = [filename]

    for song_name in song_names:
        name_split = song_name.split(".")[0]
        # This is redundant, you could just use name_split.
        pre_folder = name_split

        in_loc = f"{IN_LOC}/{song_name}"
        print(f"Processing file: {in_loc}")

        commands = [
            ["spleeter", "separate", "-o", OUT_LOC,
                "-p", "spleeter:4stems", in_loc]
        ]

        for i in INSTRUMENTS:
            source_path = f"{OUT_LOC}/{name_split}/{i}.*"
            destination_path = f"{OUT_LOC}/{pre_folder}_{i}.wav"
            # Check if source file exists, assume .wav for check.
            if os.path.exists(source_path.replace("*", ".wav")):
                commands.append(["mv", source_path, destination_path])
            else:
                print(f"File not found: {source_path}")

        # directory_path = f"{OUT_LOC}/{name_split}"
        # if os.path.exists(directory_path):
        #     commands.append(["rm", "-r", directory_path])

        for command in commands:
            print("Executing command:", ' '.join(command))
            subprocess.call(command)


def delete_processed():
    command = ['rm', f"{OUT_LOC}/*.wav"]
    subprocess.call(command)


def delete_uploaded(filename):
    name_split = filename.split(".")[0]
    command = ['rm', f"{IN_LOC}/{name_split}*.wav"]
    subprocess.call(command)
