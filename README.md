🎬 Movie Recommendation System
A content-based movie recommender built with Machine Learning and Streamlit. Select a movie, and the system suggests similar ones using cosine similarity on TMDB data.

🚀 Live Demo: Click here (Update with your Streamlit link!)

📌 Tech Stack
Python, Pandas, NumPy

Scikit-Learn (Cosine Similarity)

Streamlit (Web UI)

TMDB API (Movie Posters)

🏗️ Key Code Snippets
Loading Data & Similarity Matrix
python
Copy
Edit
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
Recommendation Function
python
Copy
Edit
def recommend(movie_title):
    idx = movies[movies['original_title'] == movie_title].index[0]
    scores = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)[1:6]
    return [movies.iloc[movie[0]]['original_title'] for movie in scores]
Fetching Movie Posters
python
Copy
Edit
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=YOUR_API_KEY"
    return f"https://image.tmdb.org/t/p/w500{requests.get(url).json().get('poster_path')}"
Streamlit UI
python
Copy
Edit
st.title("🎬 Movie Recommendation System")
selected_movie = st.selectbox("Choose a Movie:", movies['original_title'])
if st.button("Get Recommendations"):
    names, posters = recommend(selected_movie)
    for name, poster in zip(names, posters):
        st.image(poster, caption=name, width=150)
🚀 Run the Project
bash
Copy
Edit
pip install -r requirements.txt
streamlit run app.py
🌎 Deployment (Streamlit Cloud)
Upload to GitHub

Go to Streamlit Cloud

Connect repo & deploy!

📌 Author: Krishanu Maji

⭐ Star this repo if you found it useful!







