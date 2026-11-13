# MOVIEMANIA Browse (2000–2026)

A browse-only film catalogue for releases from 2000 to 2026. It shows posters, years, genres, cast, synopses and official trailers, and links each film to where it can be legally watched.

**This app does not stream or play films.** Browsing is limited to metadata and links.

## Why it's built this way

- **Scope:** most films from 2000 to 2026 are still under copyright, so the app shows information about them and sends viewers to licensed services rather than hosting them.
- **Key handling:** the TMDB API key is read from server-side secrets and sent only to TMDB as a query parameter. It never appears in the browser or the repository.
- **Efficiency:** search results are cached for 15 minutes and film details for a day, which keeps requests to TMDB low.

## What it does

- Filters by release year (2000–2026), genre, sort order and title search
- Shows poster, year, genres, top-three cast and a synopsis for each film
- Links to an official YouTube trailer when TMDB lists one
- Links to TMDB's "Where to watch" page for legal viewing options

## Tech

- Python, Streamlit, `requests`
- The Movie Database (TMDB) API
- Tests: offline parsing checks, and a Streamlit flow test that runs against a stubbed TMDB

## Status

| Area | Status | Notes |
|---|---|---|
| Parsing (trailer, cast, poster, links) | Tested | Offline checks pass |
| Filters, search and layout | Tested (mocked) | Run with a stubbed TMDB |
| Live TMDB responses | Not yet tested | Needs an API key and a machine that can reach TMDB |
| Public hosting | Not yet set up | Needs a host and the key set as an environment variable |

## Run it locally

1. Install the requirements:
   `pip install -r requirements.txt`
2. Create `.streamlit/secrets.toml` in this folder:
   `TMDB_API_KEY = "your-key-here"`
3. Start the app:
   `streamlit run app.py`

Add `.streamlit/secrets.toml` to `.gitignore`. Never commit it.

## Deploy to a public host

Set `TMDB_API_KEY` as an environment variable on the host, then start the app with:

`streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

## Limits

- The page shows the first 20 films per page of results. Pagination controls are on the roadmap.
- Trailers appear only where TMDB lists an official YouTube trailer.
- "Where to watch" availability and pricing depend on the viewer's country.

## Roadmap

- Run a live check against TMDB and fix any response issues
- Deploy to a public host with the key in the environment
- Add a country setting so "where to watch" matches the viewer's region
- Add pagination controls

## Attribution and legal

Data from [The Movie Database (TMDB)](https://www.themoviedb.org). This product uses the TMDB API but is not endorsed or certified by TMDB. Check TMDB's terms of use and attribution rules before publishing the app.

Before showing any film publicly, check its rights in your country. Browse metadata is not a licence to show or stream a film.

## Files

- `app.py`: the Streamlit app
- `requirements.txt`: Python dependencies
- `README.md`: this file
- `overview.html`: project overview page
