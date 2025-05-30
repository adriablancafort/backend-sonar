# MySonar API

**MySonar** is a Mobile Application designed to enhance the experience of Sónar Festival attendees through personalized schedule recommendations tailored to each user's musical tastes and attendance preferences.

This is a FastAPI backend that provides API endpoints for the MySonar mobile application, featuring activity recommendations powered by AI embeddings.

This repository contains the code of the Backend API. If you are interested in the frontend , check out the [Mobile App repository](https://github.com/adriablancafort/mysonar-app).

## Features

- FastAPI REST API for festival activities and tags
- AI-powered activity recommendations using embeddings
- Supabase database integration
- Automatic API documentation with Swagger/OpenAPI

## Setup

### Prerequisites

Make sure you have the following installed:

- [Python](https://www.python.org/) (version 3.8 or higher)
- [pip](https://pip.pypa.io/) (Python package installer)
- Supabase account and project

### Get Started

1. Clone the repository

   ```bash
   git clone https://github.com/adriablancafort/mysonar-api.git
   cd mysonar-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_service_role_key_here
   
   OPENAI_API_KEY=your_openai_api_key_here
   ```

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
