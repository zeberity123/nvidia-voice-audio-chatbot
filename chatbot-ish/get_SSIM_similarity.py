import librosa
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim
import os

# 두 개의 MP3 파일 경로
#test_path = r'C:/projects/nvauc/data/Melancholic _mixture.mp3'

def get_ssim_similarity(path): 
    # 두 MP3 파일을 로드하여 Mel spectrogram으로 변환
    y, sr = librosa.load(path)
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_spectrogram_normalized = mel_spectrogram / np.max(mel_spectrogram)
    folder_path = r'recommending/data/mel_data_vocalo'

    similarity_list = []
    files = os.listdir(folder_path)
    for i in range(10):
        file_names = files[10*i:10*(i+1)]
        for file_name in file_names:
            data = np.load(os.path.join(folder_path, file_name))
            max_len = max(mel_spectrogram_normalized.shape[1], data.shape[1])
            mel_spectrogram_normalized_padded = np.pad(mel_spectrogram_normalized, ((0, 0), (0, max_len - mel_spectrogram_normalized.shape[1])), mode='constant')
            data_padded = np.pad(data, ((0, 0), (0, max_len - data.shape[1])), mode='constant')
            
            try:
                # Calculate SSIM similarity with data_range specified
                ssim = compare_ssim(mel_spectrogram_normalized_padded, data_padded, data_range=1.0)
                file_name = file_name.replace('_mixture.npy','')
                similarity_list.append({file_name: ssim})
            except ValueError as e:
                print(mel_spectrogram_normalized_padded.shape, data_padded.shape)
    return similarity_list


def get_top_n_songs(similarity_list, n=5):
    # Sort the similarity_list based on similarity scores in descending order
    sorted_similarity = sorted(similarity_list, key=lambda x: list(x.values())[0], reverse=True)
    # Extract top n songs
    top_n_songs = sorted_similarity[:n]
    res = [list(data.keys())[0] for data in top_n_songs]
    return res
