
# use shazam to insert music and send cover image correctly
# Shazam will be used for selection 2 only. And the image for the background changes should be used for unlikely artists.
# Popular artists will have their image stored in a separate file and the artist name will be checked upon clicking the upload button
# to check on the artist. This should probably be in a switch format. Shazam is slow enough so why waste more time finding the background image
# for famous artists?
# Make separate file for listing the information extracted from Shazam
# Shazam will be used anyway during selection 2. So the background switch should also happen only in selection 2.
# Finally, selection 2 atm needs you to insert the name of the song in order to search shazam. If you already uploaded the music then it should have
# read the file name automatically. Make that possible.
import os
from ShazamAPI import Shazam
import httpx

def bgr_image(audio_file):
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
            print("Title:", track_info['title'])
            results.append(track_info['title'])
            print("Artist:", artist)
            results.append(artist)
            background_image_url = background_url['coverarthq']
            print("Most common background image URL:", background_image_url)
            results.append(background_image_url)
            # Create the info directory if it doesn't exist
            info_dir = os.path.join(os.path.dirname(audio_file), "info")
            os.makedirs(info_dir, exist_ok=True)
            # Save the title and artist information to a text file in the info directory
            info_filename = os.path.join(info_dir, "info.txt")
            with open(info_filename, 'w') as info_file:
                info_file.write("Title: {}\n".format(track_info['title']))
                info_file.write("Artist: {}\n".format(artist))
            print("Title and artist information saved to:", info_filename)
            # Check if the artist is "Hatsune Miku"
            if artist != "Hatsune Miku":
                # Save the background image to the info directory with the title as the filename
                image_filename = os.path.join(info_dir, "{}.jpg".format(track_info['title']))
                with open(image_filename, 'wb') as img_file:
                    img_file.write(httpx.get(background_image_url).content)
                print("Background image saved to:", image_filename)
            else:
                print("Background image not saved because the artist is Hatsune Miku")

    return results

# Example usage
# audio_file_path = 'chatbot-ish/Melancholic_mixture.mp3'
# print(bgr_image(audio_file_path))
