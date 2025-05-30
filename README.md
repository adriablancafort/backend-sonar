# MySonar App Backend

Discover new schedules in the Sonar festival by swiping through activities.

This is a FastAPI backend that provides API endpoints for the MySonar mobile application, featuring activity recommendations powered by AI embeddings.

## Features

- FastAPI REST API for festival activities and tags
- AI-powered activity recommendations using embeddings
- Supabase database integration
- Automatic API documentation with Swagger/OpenAPI

## Setup

### Prerequisites

- Python (version 3.8 or higher)
- pip (Python package installer)
- Supabase account and project

### Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd backend-sonar
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables for Supabase connection

### Development

1. Start the development server:
   ```bash
   python3 -m uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

3. The interactive API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

4. Alternative API documentation (ReDoc) will be available at `http://localhost:8000/redoc`

## AI Embeddings

This application uses AI embeddings to provide intelligent activity recommendations. Before using the recommendation features, you need to generate embeddings for your data:

### Generate Embeddings

Run these scripts to generate embeddings for activities and tags:

```bash
# Generate embeddings for activities
python3 -m scripts.generate_activities_embedings

# Generate embeddings for tags
python3 -m scripts.generate_tags_embedings
```

These scripts will:
- Fetch all activities and tags from the database
- Generate AI embeddings for each item's text content
- Store the embeddings back in the database for use in recommendations
