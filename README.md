# MindBeat - Music Mood Analysis Platform

MindBeat analyzes your Spotify listening history to provide insights into your music-driven emotional journey.

## Features

- Spotify Authentication
- Recent Track Analysis
- Mood Tracking
- Interactive Dashboard
- Real-time Updates

## Tech Stack

- FastAPI
- Redis for Caching
- Sentry for Error Tracking
- Docker & Docker Compose
- GitHub Actions for CI/CD
- Railway.app for Deployment

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mindbeat.git
cd mindbeat
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Spotify API credentials
```

5. Run development server:
```bash
uvicorn app.main:app --reload
```

## Docker Development

```bash
docker-compose up --build
```

## Production Deployment

1. Set up Railway.app:
```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login to Railway
railway login

# Link project
railway link
```

2. Set environment variables:
```bash
cp .env.prod.example .env.prod
# Edit .env.prod with production values
```

3. Deploy:
```bash
railway up
```

## Environment Variables

Required environment variables:

- `SPOTIFY_CLIENT_ID`: Your Spotify API client ID
- `SPOTIFY_CLIENT_SECRET`: Your Spotify API client secret
- `SECRET_KEY`: Secret key for session encryption
- `SENTRY_DSN`: Sentry DSN for error tracking
- `REDIS_PASSWORD`: Redis password (in production)

## Monitoring & Scaling

- Sentry Dashboard: Monitor errors and performance
- Railway Dashboard: Monitor deployment and logs
- Redis Commander: Monitor cache performance
- Health Check: `/health` endpoint

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
