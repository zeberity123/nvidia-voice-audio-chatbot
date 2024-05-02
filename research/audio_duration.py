import os

path = r"D:/musdb18hq/vocaloid_4stems"
file_list = os.listdir(path)

n_songs = len(file_list)

print(f'{n_songs} songs:')
print(file_list)


import librosa

sample_rate = 44100
mono = True

f= open("custom_songs_list.txt","w+", encoding='utf-8')

for i in file_list:
    audio_path = os.path.join(path, i)
    audio_files = os.listdir(audio_path)
    for j in audio_files:
        file_path = os.path.join(audio_path, j)
        print(f'file_pathL----------------:{file_path}')
        (audio, sample_rate) = librosa.load(file_path, sr=sample_rate, mono=mono)
        duration = librosa.get_duration(y=audio, sr=sample_rate)

        f.write(j+' '+ ' ||  ' 'duration: ' + str(duration) +'\n')