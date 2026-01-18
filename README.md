# Movie Database Manager

A lightweight movie and TV series database manager with TMDB integration. Track your watched movies and series with a clean, mobile-friendly interface.

## Features

- Search movies and TV series from TMDB
- Manage your personal library
- Delete entries from your database
- Direct links to IMDb and TMDB
- Mobile-friendly responsive design
- Fast and lightweight

## Quick Install (Termux)

```bash
curl -fsSL https://raw.githubusercontent.com/rift-rogue/movie-db/main/install.sh | bash
```

Or clone and run manually:

```bash
git clone https://github.com/rift-rogue/movie-db.git
cd movie-db
chmod +x install.sh
./install.sh
```

## Manual Installation

1. Install Python and required packages:
```bash
pkg update && pkg upgrade
pkg install python
pip install flask requests
```

2. Run the app:
```bash
python app.py
```

3. Open in browser: `http://127.0.0.1:8000`

## Usage

- **Home**: Navigate between Add and Library pages
- **Add**: Search and add movies/series to your library
- **Library**: Browse, search, and manage your collection

## Tech Stack

- Backend: Python Flask
- Database: SQLite
- API: TMDB (via Cloudflare Worker proxy)
- Frontend: Vanilla HTML/CSS/JavaScript

## Requirements

- Python 3.x
- Flask
- Requests

## License

MIT
