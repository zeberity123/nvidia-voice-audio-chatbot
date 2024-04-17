import os

path = 'D:\miku_project\Mixdown'
file_list = os.listdir(path)

n_songs = len(file_list)

new_songs = []
for i in range(n_songs): 
    new_songs.append(file_list[i].split('_')[0])
new_songs = list(set(new_songs))


import librosa

sample_rate = 44100
mono = True

f= open("new_songs.txt","w+", encoding='utf-8')

print(f'{len(new_songs)} songs:')
for i in file_list:
    audio_path = os.path.join(path, i)
    (audio, sample_rate) = librosa.load(audio_path, sr=sample_rate, mono=mono)
    duration = librosa.get_duration(y=audio, sr=sample_rate)

    f.write(i+' '+ ' ||  ' 'duration: ' + str(duration) +'\n')
    break