import pandas as pd

vocaloid_loc = 'vocaloid_musdb/'
f= open("custom_songs_list.txt","r", encoding='utf-8')
files = f.readlines()

n_tracks = 6
n_songs = len(files)//6

cnt = 0

mix_path = []
vocals_path = []
drums_path = []
bass_path = []
other_path = []
duration_path = []
accompaniment_path = []

for i in range(n_songs):
    file_lists = []
    for j in range(n_tracks):
        file_info = files[cnt].split('  ||  duration: ')
        filename = file_info[0]
        folder_loc = filename.split('_')[0] + '/'
        file_info_txt = vocaloid_loc + folder_loc + filename
        file_lists.append(file_info_txt)
        cnt += 1

    duration = files[cnt-1].split('  ||  duration: ')[1][:-1]
    mix_path.append(file_lists[3])
    vocals_path.append(file_lists[5])
    drums_path.append(file_lists[2])
    bass_path.append(file_lists[1])
    other_path.append(file_lists[4])
    accompaniment_path.append(file_lists[0])
    duration_path.append(duration)


df = pd.DataFrame()
df['mix_path'] = mix_path
df['vocals_path'] = vocals_path
df['drums_path'] = drums_path
df['bass_path'] = bass_path
df['other_path'] = other_path
df['accompaniment_path'] = accompaniment_path
df['duration'] = duration_path

df.to_csv("vocaloid_2stems.csv", index = False)