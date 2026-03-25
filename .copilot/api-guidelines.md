# API Guidelines

Framework: aws Strands a2 (FastAPI)

## Endpoints

Use REST conventions.

GET /product
GET /product/{id}
POST /product
PUT /product/{id}
DELETE /product/{id}

## Response Format

{
  "status": "success",
  "data": {},
  "error": null
}

## Validation

Use Pydantic models.