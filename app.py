from flask import Flask, request, jsonify, send_file
import sqlite3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
DB = "movies.db"
TMDB_BASE_URL = "https://tmdb-api.muvimapp.workers.dev"

# Configure requests session with retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def db():
    return sqlite3.connect(DB)

def init_db():
    with db() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY,
                tmdb_id INTEGER NOT NULL,
                imdb_id TEXT,
                title TEXT NOT NULL,
                year INTEGER,
                media_type TEXT,
                poster_path TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tmdb_id, media_type)
            )
        """)
init_db()

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/add-page")
def add_page():
    return send_file("add.html")

@app.route("/library")
def library():
    return send_file("library.html")

@app.route("/search/tmdb")
def search_tmdb():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    
    try:
        # Search both movies and TV shows
        results = []
        
        # Get movies
        movies = session.get(f"{TMDB_BASE_URL}/search/movie", params={"query": q}, timeout=10)
        if movies.ok:
            for m in movies.json().get("results", [])[:3]:
                m["media_type"] = "movie"
                results.append(m)
        
        # Get TV shows
        tv = session.get(f"{TMDB_BASE_URL}/search/tv", params={"query": q}, timeout=10)
        if tv.ok:
            for t in tv.json().get("results", [])[:3]:
                t["media_type"] = "tv"
                results.append(t)
        
        # Sort by popularity and return top 5
        results.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        return jsonify(results[:5])
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection failed"}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"API error: {e.response.status_code}"}), 502
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return jsonify({"error": "Search failed"}), 500

@app.route("/add", methods=["POST"])
def add():
    d = request.json
    
    # Validate required fields
    if not d or not all(k in d for k in ["tmdb_id", "title", "media_type"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if d["media_type"] not in ["movie", "tv"]:
        return jsonify({"error": "Invalid media_type"}), 400
    
    try:
        # Fetch external IDs with timeout and error handling
        ext_response = session.get(
            f"{TMDB_BASE_URL}/{d['media_type']}/{d['tmdb_id']}/external_ids",
            timeout=10
        )
        ext_response.raise_for_status()
        ext = ext_response.json()
        
        # Insert into database
        with db() as c:
            c.execute(
                "INSERT OR IGNORE INTO media (tmdb_id, imdb_id, title, year, media_type, poster_path) VALUES (?, ?, ?, ?, ?, ?)",
                (d["tmdb_id"], ext.get("imdb_id"), d["title"], d.get("year"), d["media_type"], d.get("poster_path"))
            )
        return jsonify({"ok": 1})
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection failed"}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"API error: {e.response.status_code}"}), 502
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Add error: {str(e)}")
        return jsonify({"error": "Failed to add"}), 500

@app.route("/search/local")
def search_local():
    try:
        q = request.args.get("q", "").strip()
        page = int(request.args.get("page", 1))
        offset = (page - 1) * 20
        
        with db() as c:
            rows = c.execute(
                "SELECT id, title, year, poster_path, imdb_id, media_type, tmdb_id FROM media WHERE title LIKE ? ORDER BY added_at DESC LIMIT 20 OFFSET ?",
                (f"%{q}%", offset)
            ).fetchall()
        return jsonify(rows)
    except ValueError:
        return jsonify({"error": "Invalid page number"}), 400
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Search local error: {str(e)}")
        return jsonify({"error": "Search failed"}), 500

@app.route("/delete/<int:media_id>", methods=["DELETE"])
def delete_media(media_id):
    try:
        with db() as c:
            result = c.execute("DELETE FROM media WHERE id = ?", (media_id,))
            if result.rowcount == 0:
                return jsonify({"error": "Media not found"}), 404
        return jsonify({"ok": 1})
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        return jsonify({"error": "Failed to delete"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
