import streamlit as st
import pickle
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

# Load the pickled movie data and similarity matrix
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Extract movie titles for the dropdown
movies_list = movies['original_title'].values

# Placeholder image for missing posters
PLACEHOLDER_POSTER = "https://via.placeholder.com/200x300?text=No+Image"


# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")

        # ✅ Check if poster_path is valid, else return placeholder
        if poster_path and poster_path.strip():
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.exceptions.RequestException:
        return PLACEHOLDER_POSTER

    return PLACEHOLDER_POSTER  # Return placeholder if no valid poster


# Function to get movie recommendations
def recommend(movie_title):
    if movie_title not in movies['original_title'].values:
        return ["Movie not found in dataset."], [PLACEHOLDER_POSTER]

    idx = movies[movies['original_title'] == movie_title].index[0]
    similarity_scores = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = [movies.iloc[movie[0]]['original_title'] for movie in similarity_scores]
    movie_ids = [movies.iloc[movie[0]]['id'] for movie in similarity_scores]

    # Fetch posters in parallel
    with ThreadPoolExecutor() as executor:
        recommended_posters = list(executor.map(fetch_poster, movie_ids))

    return recommended_movies, recommended_posters


# Streamlit UI Styling
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #00C6FF;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
        }
        .movie-title {
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="title">🎬 Movie Recommendation System</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Find movies similar to your favorites! 🍿</p>', unsafe_allow_html=True)

# Movie selection dropdown
selected_movie_name = st.selectbox("🔎 **Select a Movie:**", movies_list, key="movie_select")

if st.button("🎥 Get Recommendations"):
    names, posters = recommend(selected_movie_name)

    # **Create Horizontal Layout using Streamlit Columns**
    cols = st.columns(5)  # Creates 5 equally spaced columns

    for i in range(5):
        with cols[i]:
            st.write(f"**{names[i]}**")  # ✅ Movie title ABOVE poster
            st.image(posters[i], width=150)  # ✅ Poster BELOW
