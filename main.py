import os
import shutil
import requests
import ffmpeg
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('OMDB_API_KEY')

# Define the directories as the current directory
current_directory = os.getcwd()
source_directory = current_directory
destination_directory = current_directory

# Function to get movie metadata from OMDb
def get_movie_metadata(title):
    url = 'http://www.omdbapi.com/'
    params = {
        't': title,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Function to format movie directory
def format_movie_directory(source, destination):
    for root, dirs, files in os.walk(source):
        for file in files:
            if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
                movie_title = os.path.splitext(file)[0]
                metadata = get_movie_metadata(movie_title)
                
                if metadata and metadata['Response'] == 'True':
                    movie_folder_name = f"{metadata['Title']} ({metadata['Year']})"
                    movie_file_name = f"{metadata['Title']} ({metadata['Year']}){os.path.splitext(file)[1]}"
                    
                    movie_folder = os.path.join(destination, movie_folder_name)
                    formatted_movie_file_path = os.path.join(movie_folder, movie_file_name)

                    # Check if the file is already formatted correctly
                    if not os.path.exists(movie_folder):
                        os.makedirs(movie_folder)
                    
                    movie_file_path = os.path.join(root, file)
                    if movie_file_path != formatted_movie_file_path:
                        # Rename the movie file
                        shutil.move(movie_file_path, formatted_movie_file_path)

                    # Update metadata using ffmpeg
                    temp_file_path = formatted_movie_file_path + "_temp"
                    ffmpeg.input(formatted_movie_file_path).output(
                        temp_file_path,
                        **{
                            'metadata': {
                                'title': metadata['Title'],
                                'comment': metadata['Plot'],
                                'genre': metadata['Genre'],
                                'date': metadata['Year']
                            }
                        }
                    ).run()
                    
                    # Replace the original file with the updated one
                    os.remove(formatted_movie_file_path)
                    shutil.move(temp_file_path, formatted_movie_file_path)

# Run the script
format_movie_directory(source_directory, destination_directory)
