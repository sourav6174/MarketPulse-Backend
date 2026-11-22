# MarketPulse Backend

Python Flask REST API for the MarketPulse financial market tracker.

## Current Module

Indian Market Indexes.

## Technology Stack

- Python 3.12
- Flask
- Gunicorn
- yfinance
- Pandas
- Flask-CORS

## Local Installation

### 1. Create a virtual environment

python -m venv venv

### 2. Activate the environment

Windows:

venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure environment variables

Create a .env file.

FRONTEND_ORIGINS=http://127.0.0.1:5500,http://localhost:5500

### 5. Start the backend

python run.py

Local API:

http://127.0.0.1:5000

## API Endpoints

GET /api/health

GET /api/indexes

GET /api/indexes?refresh=true

GET /api/indexes/list

GET /api/indexes/nifty50

GET /api/indexes/sensex

GET /api/indexes/banknifty

GET /api/indexes/niftyit

GET /api/indexes/niftynext50

GET /api/indexes/indiavix

GET /api/indexes/niftymidcap100

GET /api/indexes/niftysmallcap100

## Deployment

The application is configured for Render.

Build command:

pip install -r requirements.txt

Start command:

gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120

Health check:

/api/health

## Data Source

Yahoo Finance through the yfinance Python library.

Data availability, delays and rate limits are controlled by Yahoo Finance.

## Important Notes

- Market data is not guaranteed to be real-time.
- Failed index requests are reported individually.
- Successful responses are cached for 60 seconds.
- The cache is in memory and resets when the application restarts.
- This application is intended for informational and educational use.