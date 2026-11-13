"""MOVIEMANIA browse: 2000-2026 films, browse only.

Titles, posters, years, genres, cast, synopses and official trailers come from
The Movie Database (TMDB). There is no playback here: each film links out to
where it can be legally watched. The API key is read from Streamlit secrets
(TMDB_API_KEY) and is never sent to the browser.
"""
import requests
import streamlit as st

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w342"
YEAR_MIN, YEAR_MAX = 2000, 2026

st.set_page_config(page_title="MOVIEMANIA - Browse 2000-2026", layout="wide")


def api_key():
    try:
        return st.secrets["TMDB_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


def get(path, key, **params):
    r = requests.get(f"{API}{path}", params={"api_key": key, **params}, timeout=15)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=3600, show_spinner=False)
def genre_map(key):
    data = get("/genre/movie/list", key, language="en-US")
    return {g["id"]: g["name"] for g in data.get("genres", [])}


@st.cache_data(ttl=900, show_spinner=False)
def discover(key, year_from, year_to, sort, genre_id, query, page):
    if query:
        data = get("/search/movie", key, query=query, include_adult="false", language="en-US",
                   primary_release_year=None, page=page)
        results = [m for m in data.get("results", []) if year_from <= _year(m) <= year_to]
        if genre_id:
            results = [m for m in results if genre_id in m.get("genre_ids", [])]
        return results
    params = dict(
        include_adult="false", language="en-US", page=page, sort_by=sort,
        **{"primary_release_date.gte": f"{year_from}-01-01", "primary_release_date.lte": f"{year_to}-12-31"},
    )
    if genre_id:
        params["with_genres"] = genre_id
    return get("/discover/movie", key, **params).get("results", [])


@st.cache_data(ttl=86400, show_spinner=False)
def details(key, movie_id):
    return get(f"/movie/{movie_id}", key, append_to_response="credits,videos", language="en-US")


def _year(m):
    d = m.get("release_date") or ""
    return int(d[:4]) if d[:4].isdigit() else 0


def parse_movie(d, genres):
    """Turn a TMDB detail payload into the fields the page shows."""
    cast = [c["name"] for c in (d.get("credits") or {}).get("cast", [])[:3]]
    trailer = None
    for v in (d.get("videos") or {}).get("results", []):
        if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("official"):
            trailer = f"https://www.youtube.com/watch?v={v['key']}"
            break
    return {
        "id": d.get("id"),
        "title": d.get("title") or d.get("original_title") or "Untitled",
        "year": _year(d),
        "genres": [g["name"] for g in d.get("genres", [])] or [genres.get(i, "") for i in d.get("genre_ids", [])],
        "cast": cast,
        "synopsis": d.get("overview") or "No synopsis available.",
        "poster": f"{IMG}{d['poster_path']}" if d.get("poster_path") else None,
        "trailer": trailer,
        "watch": f"https://www.themoviedb.org/movie/{d.get('id')}/watch",
    }


st.markdown("<h1 style='color:#2f7bff;margin-bottom:0'>MOVIE<span style='color:inherit'>MANIA</span></h1>",
            unsafe_allow_html=True)
st.caption("Browse films from 2000 to 2026. Browse only: no playback here. Each film links to where you can legally watch it.")

key = api_key()
if not key:
    st.error("TMDB_API_KEY is not set. Add it under the app's Secrets in Streamlit Cloud, then reload.")
    st.stop()

genres = genre_map(key)
with st.sidebar:
    st.header("Filters")
    year_from, year_to = st.slider("Release years", YEAR_MIN, YEAR_MAX, (YEAR_MIN, YEAR_MAX))
    genre_name = st.selectbox("Genre", ["All"] + sorted(genres.values()))
    sort = st.selectbox("Sort by", ["popularity.desc", "vote_average.desc", "primary_release_date.desc", "primary_release_date.asc"],
                        format_func=lambda s: {"popularity.desc": "Most popular", "vote_average.desc": "Top rated",
                                               "primary_release_date.desc": "Newest", "primary_release_date.asc": "Oldest"}[s])
    query = st.text_input("Search titles")
    page = st.number_input("Page", min_value=1, max_value=20, value=1, step=1)

genre_id = next((i for i, n in genres.items() if n == genre_name), None) if genre_name != "All" else None

try:
    results = discover(key, year_from, year_to, sort, genre_id, query.strip(), int(page))
except requests.RequestException as e:
    st.error(f"Could not reach TMDB ({e}). Check the key and try again.")
    st.stop()

if not results:
    st.info("No films match these filters.")
    st.stop()

cols = st.columns(4)
for i, m in enumerate(results[:20]):
    with cols[i % 4]:
        try:
            d = parse_movie(details(key, m["id"]), genres)
        except requests.RequestException:
            continue
        if d["poster"]:
            st.image(d["poster"], use_container_width=True)
        st.subheader(f"{d['title']} ({d['year'] or 'n/a'})")
        st.write(" · ".join(d["genres"]) or "Genre not listed")
        if d["cast"]:
            st.write("Cast: " + ", ".join(d["cast"]))
        with st.expander("Synopsis"):
            st.write(d["synopsis"])
        links = []
        if d["trailer"]:
            links.append(f"[Official trailer]({d['trailer']})")
        links.append(f"[Where to watch]({d['watch']})")
        st.markdown("  ·  ".join(links))

st.caption("Data from TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.")
