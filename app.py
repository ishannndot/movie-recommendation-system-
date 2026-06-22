import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie
from requests.utils import quote
from dotenv import load_dotenv
import os

# ------------------ Load Environment Variables ------------------
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# ------------------ Lottie Helper ------------------
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# Movie Animation
lottie_movie = load_lottieurl(
    "https://assets6.lottiefiles.com/packages/lf20_touohxv0.json"
)

# ------------------ Poster Functions ------------------
@st.cache_data
def get_poster_by_id(movie_id):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={API_KEY}&language=en-US"
    )

    try:
        data = requests.get(url).json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w200{poster_path}"

    except:
        pass

    return None


@st.cache_data
def get_poster_by_title(title):
    search_url = (
        f"https://api.themoviedb.org/3/search/movie"
        f"?api_key={API_KEY}&query={quote(title)}"
    )

    try:
        data = requests.get(search_url).json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")

            if poster_path:
                return f"https://image.tmdb.org/t/p/w200{poster_path}"

    except:
        pass

    return None


# ------------------ Recommendation Function ------------------
def recommend(movie):
    movie_idx = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_idx]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        movie_id = movies.iloc[i[0]].movie_id

        poster_url = get_poster_by_id(movie_id)

        if not poster_url:
            poster_url = get_poster_by_title(title)

        recommended_movies.append(title)
        recommended_posters.append(poster_url if poster_url else "")

    return recommended_movies, recommended_posters


# ------------------ Load Data ------------------
movies = pd.read_csv("final_movies.csv")
similarity = pd.read_csv("final_similarity.csv").values

# ------------------ UI ------------------
st.markdown(
    "<h1 style='font-size:50px;text-align:center'>🎬 Movie Recommendation System</h1>",
    unsafe_allow_html=True
)

# Lottie Animation
if lottie_movie:
    st_lottie(lottie_movie, height=250, key="movie_animation")

# Movie Selector
option = st.selectbox(
    "Select a movie you like:",
    movies["title"].values
)

# Recommendation Button
if st.button("Recommend"):
    movies_list, posters = recommend(option)

    cols = st.columns(5)

    for col, title, poster in zip(cols, movies_list, posters):
        col.markdown(
            f"<h4 style='text-align:center'>{title}</h4>",
            unsafe_allow_html=True
        )

        if poster:
            col.image(poster, width=150)
        else:
            col.markdown(
                "<p style='text-align:center'>No poster available</p>",
                unsafe_allow_html=True
            )