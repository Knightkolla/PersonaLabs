# AI Persona Validator

A playground system for experimenting with persona-based feature validation using AI-generated synthetic personas.

## Overview

The AI Persona Validator allows users to input company context and feature ideas, then generates synthetic personas and simulates their reactions using LLMs to provide insights about potential adoption rates and user objections.

## Architecture

- **Backend**: Python FastAPI with SQLite database
- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **LLM Integration**: OpenAI/Anthropic APIs for persona generation and simulation
- **Testing**: Property-based testing with Hypothesis (Python) and fast-check (TypeScript)

## Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── models.py       # Pydantic data models
│   │   ├── database.py     # Database configuration
│   │   ├── routers/        # API route handlers
│   │   └── services/       # Business logic services
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── services/      # API client services
│   │   ├── types/         # TypeScript type definitions
│   │   └── tests/         # Frontend tests
│   └── package.json       # Node.js dependencies
└── README.md
```

## Getting Started

### Backend Setup

1. Create and activate Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the backend:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Environment Variables

Create a `.env` file in the backend directory with:

```
DATABASE_URL=sqlite:///./ai_persona_validator.db
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000
```

## Features

- **Company Context Processing**: Extract and enrich company information
- **Persona Generation**: Create diverse synthetic personas based on company context
- **Feature Simulation**: Simulate persona reactions to feature descriptions
- **Insights Aggregation**: Analyze results and provide recommendations
- **Web Interface**: Clean, intuitive interface for managing experiments
- **Experiment Management**: Save, load, and share experiments

## API Endpoints

- `POST /api/v1/experiments/` - Create new experiment
- `GET /api/v1/experiments/{id}` - Get experiment by ID
- `POST /api/v1/experiments/{id}/simulate` - Run simulation for experiment

## Contributing

This is a playground system designed for experimentation with persona-based validation. The codebase includes comprehensive property-based tests to ensure correctness of core functionality.