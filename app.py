import streamlit as st
import pickle
import requests
from concurrent.futures import ThreadPoolExecutor
import random

# ===============================
# CONFIG
# ===============================
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450?text=No+Image"
TMDB_KEY = "8265bd1679663a7ea12ac168da84d2e8"
OMDB_KEY = "thewdb"

movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))
movies_list = movies["original_title"].values

# ===============================
# HELPER FUNCTIONS
# ===============================
session = requests.Session()
session.headers.update({"User-Agent": "movie-recommender/1.0"})


def safe_request(url, params=None, timeout=4):
    try:
        r = session.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id, movie_title=None):
    """Fetch poster, overview, and rating info."""
    # Try TMDB
    if movie_id:
        data = safe_request(f"https://api.themoviedb.org/3/movie/{movie_id}",
                            {"api_key": TMDB_KEY, "language": "en-US"})
        if data and "title" in data:
            imdb_id = data.get("imdb_id")
            poster = f"https://image.tmdb.org/t/p/w300{data.get('poster_path')}" if data.get("poster_path") else PLACEHOLDER_POSTER
            overview = data.get("overview", "No description available.")[:150] + "..."
            return {
                "title": data["title"],
                "overview": overview,
                "poster": poster,
                "rating": data.get("vote_average", "N/A"),
                "imdb": f"https://www.imdb.com/title/{imdb_id}" if imdb_id else "#",
                "source": "TMDB"
            }

    # Fallback OMDb
    data = safe_request("http://www.omdbapi.com/", {"apikey": OMDB_KEY, "t": movie_title})
    if data and data.get("Title"):
        poster = data.get("Poster", PLACEHOLDER_POSTER)
        overview = data.get("Plot", "No description available.")[:150] + "..."
        imdb_id = data.get("imdbID")
        return {
            "title": data.get("Title", movie_title),
            "overview": overview,
            "poster": poster,
            "rating": data.get("imdbRating", "N/A"),
            "imdb": f"https://www.imdb.com/title/{imdb_id}" if imdb_id else "#",
            "source": "OMDb"
        }

    return {
        "title": movie_title or "Unknown",
        "overview": "No information available.",
        "poster": PLACEHOLDER_POSTER,
        "rating": "N/A",
        "imdb": "#",
        "source": "None"
    }


def recommend(movie_title, genre_filter=None):
    """Recommend at least 5 movies, prioritizing genre matches but filling gaps."""
    if movie_title not in movies["original_title"].values:
        return [], []

    idx = movies[movies["original_title"] == movie_title].index[0]
    sim_scores = sorted(
        enumerate(similarity[idx]), key=lambda x: x[1], reverse=True
    )[1:50]

    rec_names, rec_ids = [], []

    for i in sim_scores:
        title = movies.iloc[i[0]]["original_title"]
        tags = str(movies.iloc[i[0]]["tags"]).lower()
        if genre_filter and genre_filter.lower() not in tags:
            continue
        rec_names.append(title)
        rec_ids.append(movies.iloc[i[0]]["id"])
        if len(rec_names) >= 5:
            break

    if len(rec_names) < 5:
        for i in sim_scores:
            title = movies.iloc[i[0]]["original_title"]
            if title not in rec_names:
                rec_names.append(title)
                rec_ids.append(movies.iloc[i[0]]["id"])
            if len(rec_names) >= 5:
                break

    return rec_names[:5], rec_ids[:5]


# ===============================
# STREAMLIT CONFIG
# ===============================
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎥", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0a0a0f;
    color: #e6e6e6;
    font-family: 'Poppins', sans-serif;
}
.title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #4169e1;
    text-shadow: 0px 0px 12px #1e3a8a;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 25px;
    color: #a3a3a3;
}
.movie-card {
    background: linear-gradient(145deg, #111111, #1a1a1f);
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    transition: all 0.3s ease-in-out;
    box-shadow: 0px 0px 15px rgba(30,58,138,0.25);
}
.movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 25px rgba(65,105,225,0.6);
}
.movie-title {
    text-align: center;
    font-weight: 600;
    font-size: 15px;
    color: #dbeafe;
    margin-top: 8px;
}
.movie-desc {
    font-size: 13px;
    color: #cbd5e1; /* brighter gray-blue for better visibility */
    text-align: justify;
    font-weight: 500; /* make it semi-bold */
    margin-top: 6px;
    line-height: 1.3em;
}
footer {visibility: hidden;}
input, textarea {
    color: black !important;
}
.stButton>button {
    background: linear-gradient(135deg, #1e3a8a, #172554);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #3b82f6, #1e40af);
    box-shadow: 0px 0px 12px rgba(59,130,246,0.6);
}
a {
    color: #3b82f6 !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3203/3203071.png", width=100)
    st.title("🎬 CineDark Recommender")
    st.markdown("Find movies that match your mood or taste 🎞️")
    st.markdown("---")
    st.info("💡 Try *Inception*, *Avatar*, or *The Dark Knight*")

    genre_filter = st.selectbox("🎭 Filter by Genre (optional):",
                                ["None", "Action", "Drama", "Comedy", "Sci-Fi", "Romance", "Thriller", "Horror"])
    if genre_filter == "None":
        genre_filter = None

# ===============================
# HEADER
# ===============================
st.markdown('<p class="title">🌌 CineDark Movie Recommendation System</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered movie companion 🍿</p>', unsafe_allow_html=True)

selected_movie = st.selectbox("🔎 Choose a movie:", movies_list)

# ===============================
# MAIN RECOMMENDER
# ===============================
if st.button("🚀 Get Recommendations"):
    with st.spinner("Finding your next cinematic gem... 🎥"):
        rec_names, rec_ids = recommend(selected_movie, genre_filter)
        with ThreadPoolExecutor() as ex:
            movie_data = list(ex.map(lambda args: fetch_movie_details(*args), zip(rec_ids, rec_names)))

    cols = st.columns(5)
    for i, data in enumerate(movie_data):
        with cols[i]:
            st.markdown(f"""
                <div class='movie-card'>
                    <img src='{data["poster"]}' style='width:100%;border-radius:8px;'>
                    <p class='movie-title'>{data["title"]}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎬 Movie Details")

    for data in movie_data:
        with st.expander(f"📽️ {data['title']}"):
            st.image(data["poster"], width=220)
            st.markdown(f"**⭐ Rating:** {data['rating']}")
            st.markdown(f"**📝 Overview:** {data['overview']}")
            if data["imdb"] != "#":
                st.markdown(f"[🔗 View on IMDb]({data['imdb']})")
            st.caption(f"Source: {data['source']}")

# ===============================
# 🎙️ CINEBOT CHAT
# ===============================
st.markdown("---")
st.subheader("🤖 CineBot — Your Movie Mood Buddy")

mood_map = {
    "sad": ("Drama", [
        "Hey, sometimes a heartfelt story heals the soul 💙",
        "Feeling blue? These emotional dramas might bring comfort 🎬"
    ]),
    "happy": ("Comedy", [
        "You’re glowing! Let’s match that with laughter 😄",
        "In a good mood? Here are some joyful comedies 🌟"
    ]),
    "angry": ("Action", [
        "Got fire inside? Let’s cool off with some wild action 🔥",
        "Channel that energy into some explosive blockbusters 💥"
    ]),
    "bored": ("Adventure", [
        "Let’s escape boredom with some epic adventures 🌍",
        "Get ready for thrilling rides and discoveries 🚀"
    ]),
    "low": ("Drama", [
        "Feeling low? Here are some inspiring dramas 💫",
        "Movies that speak to the heart 💖"
    ]),
    "demotivated": ("Adventure", [
        "You’ve got this 💪! Let these movies reignite your spirit 🔷",
        "Find motivation in these powerful stories 🔥"
    ]),
}

user_input = st.text_input("💬 Tell CineBot how you feel (e.g. 'I'm sad', 'I want something funny')")

if user_input:
    user_input_lower = user_input.lower()
    detected_mood = None
    for mood in mood_map.keys():
        if mood in user_input_lower:
            detected_mood = mood
            break

    if detected_mood:
        genre, responses = mood_map[detected_mood]
        st.markdown(f"🤖 **CineBot:** {random.choice(responses)}")

        rec_names, rec_ids = recommend(movies_list[0], genre_filter=genre)
        with ThreadPoolExecutor() as ex:
            movie_data = list(ex.map(lambda args: fetch_movie_details(*args), zip(rec_ids, rec_names)))

        cols = st.columns(5)
        for i, data in enumerate(movie_data):
            with cols[i]:
                st.image(data["poster"], use_container_width=True, caption=data["title"])
                # bold, visible movie description
                st.markdown(f"<p class='movie-desc'>{data['overview']}</p>", unsafe_allow_html=True)
    else:
        st.markdown("🤖 **CineBot:** Hmm, I couldn’t quite catch that — maybe try 'I feel sad' or 'I’m bored'?")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#94a3b8;'>✨ Built with 💙 by <b>Krishanu Mishra</b> | "
    "<a style='color:#3b82f6;' href='https://github.com/m-krishanu07/Movie_Recommender'>GitHub Repo</a></p>",
    unsafe_allow_html=True
)
