# System Architecture

This project follows a microservice + AI agent architecture.

Layers:

1. API Layer
2. Service Layer
3. Domain Layer
4. Infrastructure Layer

## Responsibilities

API
- request validation
- authentication
- response formatting

Services
- business logic
- orchestration

Domain
- entities
- business rules

Infrastructure
- database
- messaging
- external APIs

## Rules

API must not contain business logic.
Domain models must be framework independent.