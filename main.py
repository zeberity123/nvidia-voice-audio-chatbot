import numpy as np
import tensorflow as tf
import librosa
import musdb

# Define paths and parameters
musdb_path = 'path_to_musdb18'  # Set the correct path to your MUSDB dataset

# Function to convert audio to Mel spectrogram


def audio_to_mel_spectrogram(audio, sr, n_fft=2048, hop_length=512, n_mels=128):
    S = librosa.feature.melspectrogram(
        audio, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    S_dB = librosa.power_to_db(S, ref=np.max)
    # Add batch and channel dimensions
    return S_dB[np.newaxis, ..., np.newaxis]

# Data generator for TensorFlow Dataset


def data_generator(musdb_dataset, subset):
    for track in musdb_dataset.load_mus_tracks(subsets=[subset]):
        mixture = track.audio.T.astype(np.float32)  # Mix of all stems
        mel_spectrogram = audio_to_mel_spectrogram(
            mixture.flatten(), sr=44100)  # Flatten to mono if necessary
        yield mel_spectrogram, mel_spectrogram

# Create TensorFlow datasets


def create_dataset(musdb_dataset, subset, batch_size=8):
    def generator(): return data_generator(musdb_dataset, subset)
    dataset = tf.data.Dataset.from_generator(
        generator,
        output_signature=(
            tf.TensorSpec(shape=(None, 128, None, 1), dtype=tf.float32),
            tf.TensorSpec(shape=(None, 128, None, 1), dtype=tf.float32)
        )
    )
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)


# Initialize MUSDB dataset
musdb_dataset = musdb.DB(root=musdb_path, download=True,
                         subsets=['train', 'test'])
train_dataset = create_dataset(musdb_dataset, 'train')
valid_dataset = create_dataset(musdb_dataset, 'test')

# Define U-Net model for audio source separation


def unet_model(input_shape=(None, 128, None, 1)):
    inputs = tf.keras.Input(shape=input_shape)
    x = inputs
    skips = []
    num_filters = [16, 32, 64, 128, 256]

    # Encoding path
    for filters in num_filters:
        x = tf.keras.layers.Conv2D(filters, (3, 3), padding="same")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('relu')(x)
        skips.append(x)
        x = tf.keras.layers.Conv2D(
            filters, (3, 3), strides=2, padding="same")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('relu')(x)

    # Bottleneck
    x = tf.keras.layers.Conv2D(num_filters[-1] * 2, (3, 3), padding="same")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation('relu')(x)

    # Decoding path
    for i in reversed(range(len(num_filters))):
        filters = num_filters[i]
        x = tf.keras.layers.Conv2DTranspose(
            filters, (3, 3), strides=2, padding="same")(x)
        x = tf.keras.layers.Concatenate()([x, skips.pop()])
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('relu')(x)
        x = tf.keras.layers.Conv2D(filters, (3, 3), padding="same")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('relu')(x)

    outputs = tf.keras.layers.Conv2D(2, (1, 1), activation="sigmoid")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs,
                           name="UNet-Audio-Separator")
    return model


# Create and compile U-Net model
model_unet = unet_model()
model_unet.compile(optimizer='adam', loss='mean_squared_error')

# Define the BLSTM model for audio processing


def build_blstm_model(input_shape, lstm_units=500, output_channels=1):
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.TimeDistributed(tf.keras.layers.Flatten())(inputs)
    for _ in range(3):
        x = tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(lstm_units, return_sequences=True))(x)
    x = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(
        input_shape[1] * input_shape[2], activation='relu'))(x)
    x = tf.keras.layers.TimeDistributed(
        tf.keras.layers.Reshape(input_shape[1:]))(x)
    model = tf.keras.Model(inputs=inputs, outputs=x)
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# Create and compile BLSTM model
model_blstm = build_blstm_model((None, 128, 257))
model_blstm.summary()

# Train the models
model_unet.fit(train_dataset, epochs=10, validation_data=valid_dataset)
model_blstm.fit(train_dataset, epochs=10, validation_data=valid_dataset)
