# PersonaLab Backend API Documentation

**Base URL**: `http://localhost:8000`  
**API Prefix**: `/api/v1`

---

## 📋 Table of Contents
1. [Experiments](#experiments)
2. [Simulation](#simulation)
3. [Sharing](#sharing)
4. [Export](#export)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)

---

## Experiments

### Create Experiment
**POST** `/api/v1/experiments/`

Creates a new experiment with company context and feature description. Automatically generates personas.

**Request Body:**
```json
{
  "company_input": {
    "name": "TechCorp",
    "industry": "Software",
    "target_market": "B2B SaaS companies looking to automate workflows",
    "business_model": "B2B",
    "company_size": "Startup",
    "description": "Leading provider of workflow automation tools"
  },
  "feature_description": {
    "name": "AI-Powered Workflow Automation",
    "description": "Automatically detect and optimize repetitive workflows using machine learning",
    "value_proposition": "Reduce manual work by 70% and increase team productivity",
    "target_user": "Operations teams and process managers",
    "pricing_model": "$99/user/month",
    "implementation_complexity": "Medium",
    "competitor_comparison": "Faster than Zapier, easier than custom code"
  }
}
```

**Response:** `200 OK`
```json
{
  "experiment": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-01-30T00:00:00",
    "updated_at": "2025-01-30T00:00:00",
    "company_context": { /* CompanyContext object */ },
    "feature_description": { /* FeatureDescription object */ },
    "personas": [
      {
        "id": "persona-1",
        "name": "Sarah Chen",
        "demographics": {
          "age": 35,
          "role": "Operations Manager",
          "company_size": "Mid-Market",
          "industry": "SaaS",
          "income": "High"
        },
        "psychographics": {
          "personality_traits": ["Analytical", "Detail-oriented"],
          "values": ["Efficiency", "Innovation"],
          "motivations": ["Process improvement"],
          "pain_points": ["Manual repetitive tasks"]
        },
        "behavior_patterns": {
          "technology_adoption": "Early Adopter",
          "decision_making_style": "Data-driven",
          "risk_tolerance": "Medium",
          "information_sources": ["Industry reports", "Peer recommendations"]
        },
        "contextual_factors": {
          "current_solutions": ["Zapier", "Manual processes"],
          "budget": "High",
          "time_constraints": "Medium",
          "team_influence": "High"
        }
      }
      // ... more personas
    ],
    "simulation_results": [],
    "aggregated_insights": null,
    "is_public": false,
    "share_token": null
  },
  "status": "created",
  "message": "Experiment created successfully with 5 personas"
}
```

---

### List Experiments
**GET** `/api/v1/experiments/?skip=0&limit=20`

Retrieves a list of all experiments.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": "experiment-id-1",
    "created_at": "2025-01-30T00:00:00",
    "feature_description": { /* ... */ },
    "personas": [ /* ... */ ],
    // ... full experiment objects
  }
]
```

---

### Get Experiment
**GET** `/api/v1/experiments/{experiment_id}`

Retrieves a specific experiment by ID.

**Path Parameters:**
- `experiment_id`: UUID of the experiment

**Response:** `200 OK`
```json
{
  "experiment": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "personas": [ /* ... */ ],
    "simulation_results": [ /* ... */ ],
    "aggregated_insights": { /* ... */ }
  },
  "status": "success",
  "message": "Experiment retrieved successfully"
}
```

**Error:** `404 Not Found`
```json
{
  "detail": "Experiment not found"
}
```

---

## Simulation

### Run Simulation
**POST** `/api/v1/experiments/{experiment_id}/simulate`

Runs simulation for all personas in the experiment. Each persona evaluates the feature.

**Path Parameters:**
- `experiment_id`: UUID of the experiment

**Response:** `200 OK`
```json
{
  "experiment": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "simulation_results": [
      {
        "persona_id": "persona-1",
        "decision": "ADOPT",
        "confidence": 0.85,
        "reasoning": "This feature addresses our key pain point of manual processes...",
        "key_factors": ["automation", "efficiency", "ROI"],
        "timestamp": "2025-01-30T00:05:00",
        "model_used": "gemini-1.5-flash"
      }
    ],
    "aggregated_insights": {
      "overall_adoption_rate": 0.75,
      "confidence_interval": [0.65, 0.85],
      "adoption_by_segment": {
        "Role: Operations Manager": 0.9,
        "Company Size: Startup": 0.7,
        "Tech Adoption: Early Adopter": 0.95
      },
      "top_objections": [
        {
          "objection": "high cost",
          "frequency": 2,
          "affected_personas": ["persona-2", "persona-4"]
        }
      ],
      "key_success_factors": [
        {
          "factor": "automation",
          "importance": 0.8,
          "supporting_personas": ["persona-1", "persona-3", "persona-5"]
        }
      ],
      "recommendations": {
        "messaging": ["Emphasize ROI and time savings"],
        "target_segments": ["Early adopters in operations"],
        "feature_improvements": ["Add pricing tiers for smaller teams"]
      },
      "reasoning_patterns": [
        {
          "pattern_type": "theme",
          "description": "Common concern about cost",
          "frequency": 3,
          "example_quotes": ["Too expensive for our budget", "Need to see ROI first"],
          "affected_personas": ["persona-2", "persona-4", "persona-5"]
        }
      ]
    }
  },
  "status": "completed",
  "message": "Simulation completed for 5 personas"
}
```

---

### Fork Experiment
**POST** `/api/v1/experiments/{experiment_id}/fork`

Creates a copy of an experiment with a new feature description but same personas.

**Path Parameters:**
- `experiment_id`: UUID of the experiment to fork

**Request Body:**
```json
{
  "name": "Enhanced AI Automation with Predictive Analytics",
  "description": "Same as original but with AI-powered predictions",
  "value_proposition": "Reduce manual work by 90% with predictive insights",
  "target_user": "Operations teams and data analysts",
  "pricing_model": "$149/user/month"
}
```

**Response:** `200 OK`
```json
{
  "experiment": {
    "id": "new-experiment-id",
    "personas": [ /* same personas as original */ ],
    "feature_description": { /* new feature */ },
    "simulation_results": [],
    "aggregated_insights": null
  },
  "status": "forked",
  "message": "Experiment forked successfully. Ready for simulation."
}
```

---

## Sharing

### Share Experiment
**POST** `/api/v1/experiments/{experiment_id}/share`

Generates a shareable token for public access.

**Response:** `200 OK`
```json
{
  "share_token": "abc123xyz789...",
  "share_url": "/api/v1/experiments/shared/abc123xyz789...",
  "message": "Experiment shared successfully"
}
```

---

### Get Shared Experiment
**GET** `/api/v1/experiments/shared/{share_token}`

Retrieves a publicly shared experiment.

**Path Parameters:**
- `share_token`: The share token

**Response:** `200 OK`
```json
{
  "experiment": { /* full experiment */ },
  "status": "success",
  "message": "Shared experiment retrieved successfully"
}
```

**Error:** `404 Not Found`
```json
{
  "detail": "Shared experiment not found or access revoked"
}
```

---

### Revoke Share
**DELETE** `/api/v1/experiments/{experiment_id}/share`

Revokes public access to an experiment.

**Response:** `200 OK`
```json
{
  "message": "Sharing access revoked successfully"
}
```

---

## Export

### Export to CSV
**GET** `/api/v1/experiments/{experiment_id}/export/csv`

Exports experiment results as CSV file.

**Response:** `200 OK`
```
Content-Type: text/csv
Content-Disposition: attachment; filename=experiment_{id}.csv

Persona Name,Role,Age,Decision,Confidence,Reasoning,Key Factors
Sarah Chen,Operations Manager,35,ADOPT,0.85,"This feature addresses...",automation;efficiency;ROI
...
```

---

## Data Models

### Enums

**BusinessModel**: `"B2B" | "B2C" | "B2B2C" | "Marketplace" | "SaaS" | "Other"`

**CompanySize**: `"Startup" | "SMB" | "Mid-Market" | "Enterprise"`

**ImplementationComplexity**: `"Low" | "Medium" | "High"`

**SimulationDecision**: `"ADOPT" | "REJECT" | "UNSURE"`

**TechnologyAdoption**: `"Innovator" | "Early Adopter" | "Early Majority" | "Late Majority" | "Laggard"`

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes
- `200 OK` - Success
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Example Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "company_input", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Frontend Integration Examples

### Using Fetch API
```typescript
// Create experiment
const response = await fetch('http://localhost:8000/api/v1/experiments/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    company_input: { /* ... */ },
    feature_description: { /* ... */ }
  })
});
const data = await response.json();
console.log(data.experiment.id);
```

### Using API Client (Provided)
```typescript
import { apiClient } from '@/lib/api-client';

// Create experiment
const response = await apiClient.createExperiment({
  company_input: { /* ... */ },
  feature_description: { /* ... */ }
});

// Run simulation
const results = await apiClient.runSimulation(response.experiment.id);

// Export CSV
const csvBlob = await apiClient.exportCSV(response.experiment.id);
```

---

## Interactive API Docs

FastAPI provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These allow you to test all endpoints directly in the browser.
