# test.py
# Import necessary libraries
from tensorflow.keras.layers import Bidirectional, LSTM, Dense, BatchNormalization, Conv2D, Multiply, Activation
from tensorflow.keras.layers import Bidirectional, LSTM, Dense, TimeDistributed, BatchNormalization, Conv2D, Multiply, Activation
import soundfile as sf
import tensorflow as tf
import numpy as np
from IPython.display import Audio
import musdb
import librosa
import librosa.display
import matplotlib.pyplot as plt

# Load musdb sample (change root for download dir)
mus_train = musdb.DB(root='musdb18_train', subsets='train',
                     split='train', download=True)
mus_valid = musdb.DB(root='musdb18_valid', subsets="train",
                     split='valid', download=True)
mus_test = musdb.DB(root='musdb18_test', subsets='test', download=True)

# check length of tracks
print(len(mus_train.tracks), len(mus_valid.tracks), len(mus_test.tracks))

# Load a specific track from the MUSDB18 dataset
# Example, loading the second track from test subset
track = mus_test.tracks[1]
audio = track.audio.T  # Transpose to get samples x channels
sample_rate = 44100  # Define the sample rate

# Function to convert audio array to a Mel spectrogram


def audio_to_mel_spectrogram(y, sr, n_fft=2048, hop_length=512, n_mels=128):
    """
    Converts an audio array to a Mel spectrogram.

    Parameters:
    - y: Audio array.
    - sr: Sampling rate.
    - n_fft: Length of the FFT window.
    - hop_length: Number of samples between successive frames.
    - n_mels: Number of Mel bands to generate.

    Returns:
    - S_dB: Mel spectrogram in dB.
    """
    S = librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    S_dB = librosa.power_to_db(S, ref=np.max)
    return S_dB

# Function to plot a Mel spectrogram


def plot_mel_spectrogram(S_dB, sr, hop_length):
    """
    Plots a Mel spectrogram.

    Parameters:
    - S_dB: Mel spectrogram (in dB).
    - sr: Sample rate of the audio signal.
    - hop_length: Number of samples between successive frames.
    """
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(
        S_dB, sr=sr, hop_length=hop_length, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel-frequency spectrogram')
    plt.tight_layout()
    plt.show()


# Convert the loaded track's audio to Mel spectrogram and plot
S_dB = audio_to_mel_spectrogram(audio, sample_rate)
plot_mel_spectrogram(S_dB, sample_rate, hop_length=512)

# Create an audio player widget in the Jupyter Notebook to play the audio data
Audio(data=audio, rate=sample_rate)

# # Install necessary libraries
# !pip install tensorflow==2.8 librosa soundfile numpy


# Define utility functions for audio processing

def stft(audio, n_fft=2048, hop_length=512):
    return librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)


def istft(spectrogram, hop_length=512):
    return librosa.istft(spectrogram, hop_length=hop_length)

# Example BLSTM and U-Net application functions


def apply_blstm(input_tensor):
    # Simple BLSTM layer configuration
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
        128, return_sequences=True))(input_tensor)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    return x


def apply_unet(input_tensor):
    # Example U-Net layer configuration
    conv1 = Conv2D(16, (3, 3), activation='relu', padding='same')(input_tensor)
    conv1 = Conv2D(16, (3, 3), activation='relu', padding='same')(conv1)
    pool1 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(32, (3, 3), activation='relu', padding='same')(pool1)
    conv2 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv2)
    up1 = tf.keras.layers.UpSampling2D(size=(2, 2))(conv2)
    merged1 = tf.keras.layers.concatenate([conv1, up1], axis=-1)
    conv3 = Conv2D(16, (3, 3), activation='relu', padding='same')(merged1)
    output_tensor = Conv2D(
        1, (1, 1), activation='sigmoid', padding='same')(conv3)
    return output_tensor


def separate_audio(audio_path):
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)
    # Convert audio to STFT
    input_spectrogram = stft(y)
    input_tensor = np.abs(input_spectrogram)

    # Reshape for model input
    input_tensor = np.expand_dims(input_tensor, axis=0)  # Batch size of 1
    # Add channel dimension for Conv2D
    input_tensor = np.expand_dims(input_tensor, axis=-1)

    # Apply models
    vocal_tensor = apply_blstm(input_tensor)
    instrumental_tensor = apply_unet(input_tensor)

    # Convert output tensor to audio
    vocal_output = istft(vocal_tensor.numpy().squeeze())
    instrumental_output = istft(instrumental_tensor.numpy().squeeze())

    # Save the separated audio files
    sf.write('vocal_output.wav', vocal_output, sr)
    sf.write('instrumental_output.wav', instrumental_output, sr)


# Usage
# audio_path = 'path_to_audio_file.mp3'  # Ensure this path is correct or handle file uploads in Colab
separate_audio(audio_path)


# Define utility functions for audio processing

def stft(audio, n_fft=2048, hop_length=512):
    return librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)


def istft(spectrogram, hop_length=512):
    return librosa.istft(spectrogram, hop_length=hop_length)

# Example BLSTM and U-Net application functions


def apply_blstm(input_tensor):
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(
        128, return_sequences=True))(input_tensor)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    return x


def apply_unet(input_tensor):
    conv1 = Conv2D(16, (3, 3), activation='relu', padding='same')(input_tensor)
    conv1 = Conv2D(16, (3, 3), activation='relu', padding='same')(conv1)
    pool1 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(32, (3, 3), activation='relu', padding='same')(pool1)
    up1 = tf.keras.layers.UpSampling2D(size=(2, 2))(conv2)
    merged1 = tf.keras.layers.concatenate([conv1, up1], axis=-1)
    conv3 = Conv2D(16, (3, 3), activation='relu', padding='same')(merged1)
    output_tensor = Conv2D(
        1, (1, 1), activation='sigmoid', padding='same')(conv3)
    return output_tensor


def separate_audio(y, sr, track_name):
    input_spectrogram = stft(y)
    input_tensor = np.abs(input_spectrogram)
    input_tensor = np.expand_dims(input_tensor, axis=0)  # Batch size of 1
    # Add channel dimension for Conv2D
    input_tensor = np.expand_dims(input_tensor, axis=-1)

    vocal_tensor = apply_blstm(input_tensor)
    instrumental_tensor = apply_unet(input_tensor)

    vocal_output = istft(vocal_tensor.numpy().squeeze())
    instrumental_output = istft(instrumental_tensor.numpy().squeeze())

    sf.write(f'{track_name}_vocal_output.wav', vocal_output, sr)
    sf.write(f'{track_name}_instrumental_output.wav', instrumental_output, sr)


# Example usage with MUSDB18 or other pre-loaded data
for track in mus_test.tracks:  # Process all tracks in the test subset
    audio = track.audio.T  # Transpose to get samples x channels
    sample_rate = 44100  # Sample rate (assumed constant, adjust if variable)
    # Sanitize track name for use in filenames
    track_name = track.name.replace('/', '_')
    separate_audio(audio, sample_rate, track_name)


def load_and_predict(audio_path, model_path='my_unet_model.h5'):
    # Load the model
    model = tf.keras.models.load_model(model_path)

    # Load audio and convert to spectrogram as before
    spectrogram, sr = audio_to_spectrogram(audio_path)

    # Assume the model expects a batch size and an additional dimension for channels
    spectrogram = np.expand_dims(spectrogram, axis=0)  # Add batch dimension
    spectrogram = np.expand_dims(spectrogram, axis=-1)  # Add channel dimension

    # Predict
    predicted_mask = model.predict(spectrogram)

    # Inverse STFT and other post-processing to convert back to audio
    # Assuming `predicted_mask` needs to be processed to extract final audio
    # Adjust depending on actual model output
    separated_audio = istft(predicted_mask.squeeze())

    return separated_audio


# Example usage
output_audio = load_and_predict('path_to_new_audio_file.wav')
