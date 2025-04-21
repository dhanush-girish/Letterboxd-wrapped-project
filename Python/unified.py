# TMDb enrichment script for Letterboxd project
import requests
import pandas as pd
import os

# Load your Letterboxd data
df = pd.read_csv('finalfinal.csv')
print("CSV file loaded successfully!")
print(df.head())  # Check the first few rows of the DataFrame

# TMDb API key
API_KEY = 'TMDB_API_KEY'


# Function to get all details from TMDb
def get_movie_details(movie_title, year):
    try:
        # Step 1: Search for the movie
        search_url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}&year={year}'
        search_response = requests.get(search_url).json()

        if search_response['results']:
            movie_id = search_response['results'][0]['id']

            # Step 2: Get movie details (runtime, genres, language, country)
            details_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
            details_response = requests.get(details_url).json()

            runtime = details_response.get('runtime', None)
            language = details_response.get('original_language', None)

            genres = [genre['name'] for genre in details_response.get('genres', [])]
            genre_str = ', '.join(genres) if genres else None

            countries = [country['name'] for country in details_response.get('production_countries', [])]
            country = ', '.join(countries) if countries else None

            # Step 3: Get director from credits
            credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'
            credits_response = requests.get(credits_url).json()

            director = None
            for crew_member in credits_response.get('crew', []):
                if crew_member.get('job') == 'Director':
                    director = crew_member.get('name')
                    break

            return runtime, language, genre_str, country, director
    except Exception as e:
        print(f"Error processing '{movie_title}' ({year}): {e}")

    return None, None, None, None, None


# Apply function to each row
print("Fetching movie details from TMDb...")
df[['Runtime (min)', 'Language', 'Genres', 'Country', 'Director']] = df.apply(
    lambda row: pd.Series(get_movie_details(row['Movie'], row['Year'])), axis=1
)

# Save the enriched data
output_file = 'letterboxd_enriched_full.csv'
df.to_csv(output_file, index=False)
print(f"All movie details saved successfully at: {os.path.abspath(output_file)}")
