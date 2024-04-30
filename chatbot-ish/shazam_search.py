from ShazamAPI import Shazam
from collections import Counter

def bgr_image(audio_file):
    audio = open(audio_file, 'rb').read()
    # Initialize Shazam and recognize the song
    shazam = Shazam(audio)
    recognize_generator = shazam.recognizeSong()

    # Initialize an empty list to store all background image URLs
    urls = []

    for _ in range(3):
        result = next(recognize_generator)
        track_info = result[1]['track']
        # Check if 'images' key exists before accessing it
        if 'images' in track_info:
            background_url = track_info['images'].get('coverarthq')
            if background_url:
                urls.append(background_url)
                print("Title:", track_info['title'])
                print("Background URL:", background_url)

    # Count occurrences of each URL
    url_counts = Counter(urls)

    most_common_url = max(url_counts, key=url_counts.get)

    print("Most common background image URL:", most_common_url)

    return most_common_url

# print(bgr_image(f'chatbot-ish/uploaded_files/melt_mixture.wav'))