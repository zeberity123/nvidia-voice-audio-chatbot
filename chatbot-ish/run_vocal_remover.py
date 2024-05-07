import os
import subprocess


def run_vocal_remover(filename):
    # Define paths using absolute references based on the script's location
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    IN_LOC = 'uploaded_files'
    OUT_LOC = 'processed_files'

    # Full path to the input file
    in_loc = os.path.join(IN_LOC, filename)
    if not os.path.isfile(in_loc):
        print(f"Input file not found: {in_loc}")
        return

    # Ensure output directory exists
    os.makedirs(OUT_LOC, exist_ok=True)

    commands = []
    # Command to run the Python script using 'python' directly
    command = [
        "python", 'inference.py', "--input", in_loc,
        "--output_dir", OUT_LOC, "--gpu", "0"
    ]
    # print("Executing command:", ' '.join(command))

    commands.append(command)

    name_split = filename.split(".")[0]
    # Post-processing (assuming files are created by the script)
    # for instrument in ["Instruments", "Vocals"]:
        # source_path = os.path.join(
        #     OUT_LOC, f"{os.path.splitext(filename)[0]}_{instrument}.wav")
        # if os.path.exists(source_path):
        #     print(f"File processed successfully: {source_path}")
        # else:
        #     print(f"Processed file not found: {source_path}")

    # commands.append(['rm', f'processed_files/{name_split}_Instruments.*'])
    commands.append(['mv', f'processed_files/{name_split}_Vocals.*', f'processed_files/{name_split}_vocals.wav'])

    for i in commands:
        subprocess.call(i)

# run_vocal_remover('melt.wav')