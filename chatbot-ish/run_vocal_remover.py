import os
import subprocess


def run_vocal_remover(filename):
    # Define paths using absolute references based on the script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    IN_LOC = os.path.join(base_dir, 'uploaded_files')
    OUT_LOC = os.path.join(base_dir, 'processed_files')
    script_path = os.path.join(base_dir, 'vocal_remover', 'inference.py')

    # Full path to the input file
    in_loc = os.path.join(IN_LOC, filename)
    if not os.path.isfile(in_loc):
        print(f"Input file not found: {in_loc}")
        return

    # Ensure output directory exists
    os.makedirs(OUT_LOC, exist_ok=True)

    # Command to run the Python script using 'python' directly
    command = [
        "python", script_path, "--input", in_loc,
        "--output_dir", OUT_LOC, "--gpu", "0"
    ]
    print("Executing command:", ' '.join(command))
    subprocess.call(command)

    # Post-processing (assuming files are created by the script)
    for instrument in ["mix", "vocal"]:
        source_path = os.path.join(
            OUT_LOC, f"{os.path.splitext(filename)[0]}_{instrument}.wav")
        if os.path.exists(source_path):
            print(f"File processed successfully: {source_path}")
        else:
            print(f"Processed file not found: {source_path}")


# Example call with file name
run_vocal_remover("Legends Never Die.mp3")
