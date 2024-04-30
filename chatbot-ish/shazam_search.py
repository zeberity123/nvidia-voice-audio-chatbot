import os
import re
from ShazamAPI import Shazam
import httpx

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def bgr_image(audio_file):
    # Check if the file extension is supported (MP3 or WAV)
    file_extension = os.path.splitext(audio_file)[1].lower()
    if file_extension not in ['.mp3', '.wav']:
        raise ValueError("Invalid file format. Supported formats: MP3, WAV")

    audio = open(audio_file, 'rb').read()
    # Initialize Shazam and recognize the song
    shazam = Shazam(audio)
    recognize_generator = shazam.recognizeSong()

    # Initialize an empty list to store all background image URLs and other information
    results = []

    result = next(recognize_generator)
    track_info = result[1]['track']
    # Check if 'images' key exists before accessing it
    if 'images' in track_info:
        background_url = track_info['images']
        artist = track_info['subtitle']
        if background_url:
            title = track_info['title']
            artist = artist.encode('utf-8').decode('cp949', 'ignore')  # Convert artist to cp949 encoding
            title = title.encode('utf-8').decode('cp949', 'ignore')  # Convert title to cp949 encoding
            print("Title:", title)
            results.append(title)
            print("Artist:", artist)
            results.append(artist)
            background_image_url = background_url['coverarthq']
            #print("Most common background image URL:", background_image_url)
            results.append(background_image_url)
            # Create the info directory if it doesn't exist
            info_dir = os.path.join(os.path.dirname(audio_file), "info")
            os.makedirs(info_dir, exist_ok=True)
            # Save the title and artist information to a text file in the info directory
            info_filename = os.path.join(info_dir, "info.txt")
            with open(info_filename, 'w', encoding='utf-8') as info_file:  # Specify UTF-8 encoding
                info_file.write("Title: {}\n".format(title))
                info_file.write("Artist: {}\n".format(artist))
            #print("Title and artist information saved to:", info_filename)
            # Check if the artist is "Hatsune Miku"
            if artist != "Hatsune Miku":
                # Sanitize the title to create a valid filename
                sanitized_title = sanitize_filename(title)
                # Save the background image to the info directory with the sanitized title as the filename
                image_filename = os.path.join(info_dir, "{}.jpg".format(sanitized_title))
                with open(image_filename, 'wb') as img_file:
                    img_file.write(httpx.get(background_image_url).content)
                #print("Background image saved to:", image_filename)
            else:
                print("Background image not saved because the artist is Hatsune Miku")

    return results

# Example usage
# audio_file_path = 'chatbot-ish/Melancholic_mixture.mp3'
# print(bgr_image(audio_file_path))
