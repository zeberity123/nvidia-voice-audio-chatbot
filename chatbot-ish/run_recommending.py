# main.py

# Importing the get_cos_similarity function from get_cos_similarity.py
#from get_cos_similarity import *
from get_SSIM_similarity import *

def main(path):
    # Set the test path
    
    # Call the get_cos_similarity function with the test_path
    similarity_list = get_ssim_similarity(path)
    similarity_songs = get_top_n_songs(similarity_list)
    print("Similarity Songs:", similarity_songs)
    return similarity_songs