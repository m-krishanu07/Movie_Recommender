
# 🎬 CineDark — AI-Powered Movie Recommendation System  

![App Banner](https://github.com/m-krishanu07/Movie_Recommender/blob/main/Screenshot%202025-11-06%20233545.png)

> **CineDark** is a sleek and intelligent **Movie Recommendation System** built using **Python**, **Streamlit**, and **Machine Learning**.  
> It uses a **content-based filtering** approach (TF-IDF + Cosine Similarity) to recommend movies similar to the one you love — complete with posters, overviews, and ratings fetched via APIs.  
![App Screenshot](https://github.com/m-krishanu07/Movie_Recommender/blob/main/Screenshot%202025-11-06%20233618.png)
---

## 🧠 Project Overview  

This project has two main components:  

1. **Model Building (`model.ipynb`)**  
   - Handles dataset preprocessing, cleaning, and vectorization using TF-IDF.  
   - Generates and saves trained model files (`movies.pkl`, `similarity.pkl`) for fast inference.  

2. **Web Application (`app.py`)**  
   - Interactive front-end built with **Streamlit**.  
   - Allows users to select any movie and instantly get 5 most similar movie recommendations.  
   - Displays posters and brief movie info via **TMDB API** integration.  

---
![More](https://github.com/m-krishanu07/Movie_Recommender/blob/main/Screenshot%202025-11-06%20233653.png)
## ⚙️ Approach & Methodology  

### 🧩 1. **Data Source**  
Dataset used from Kaggle:  
[TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)  
Includes information like:
- Movie title, ID, and overview  
- Genres, keywords, cast, crew, etc.  

---

### 🧹 2. **Data Preprocessing (in `model.ipynb`)**  

#### Steps Performed:

| Step | Description |
|------|--------------|
| **1️⃣ Merging Datasets** | Merged `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` on `id`. |
| **2️⃣ Cleaning Data** | Removed unwanted columns such as budget, homepage, production companies, etc. |
| **3️⃣ Parsing Complex Columns** | Converted JSON-like text fields (`genres`, `keywords`, `cast`, `crew`) into Python lists using `ast.literal_eval`. |
| **4️⃣ Feature Engineering** | Extracted useful info: top 3 cast members and director names. |
| **5️⃣ Creating Tags Column** | Combined text from overview, genres, keywords, cast, and crew into a single "tags" feature. |
| **6️⃣ Text Normalization** | Lowercased and stemmed all words to avoid duplicates (e.g., “love”, “loving” → “love”). |
| **7️⃣ TF-IDF Vectorization** | Converted the tags column into a numerical matrix using `TfidfVectorizer(max_features=5000, stop_words='english')`. |
| **8️⃣ Cosine Similarity** | Measured pairwise similarity between all movies. |
| **9️⃣ Model Saving** | Saved `movies.pkl` and `similarity.pkl` using `pickle` for later use in the web app. |

---

### 🧮 3. **Recommendation Logic**  

When a user selects a movie:
1. The system retrieves its index from the `movies.pkl` DataFrame.  
2. It looks up the cosine similarity scores from `similarity.pkl`.  
3. It sorts the scores and fetches the top 5 most similar movies.  
4. The movie posters and metadata are fetched via **TMDB API**.  

---

## 💻 How to Run the Project  

### 🔹 Step 1: Clone the Repository  
```bash
git clone https://github.com/m-krishanu07/Movie_Recommender.git
cd Movie_Recommender
