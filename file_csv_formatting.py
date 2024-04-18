import os
import librosa


def get_audio_duration(audio_path, sample_rate=44100, mono=True):

    audio, sr = librosa.load(audio_path, sr=sample_rate, mono=mono)

    duration = librosa.get_duration(y=audio, sr=sample_rate)

    formatted_duration = f"{duration:.5f}"

    return formatted_duration


def get_all_entries(directory):
    dir_list = os.listdir(directory)
    results = []  # Create an empty list to store results
    for i in dir_list:
        dir_path = os.path.join(directory, i)  # Ensure proper path joining
        if os.path.isdir(dir_path):  # Check if it's a directory
            file_names = os.listdir(dir_path)
            for e in file_names:
                # Append each file path to the results list
                results.append(f"train/{i}/{e}")

    all_file_names = ",".join(results)

    for j in file_names:
        if j.endswith("mixture.mp3"):

            du = dir_path + "/" + file_names[1]
    # can be changed to write a new scv file
    print(all_file_names + "," + str(get_audio_duration(du)))


# Specified directory
directory_path = "C:/Users/birth/Desktop/songs/"

# Call the function with the provided directory path
get_all_entries(directory_path)
