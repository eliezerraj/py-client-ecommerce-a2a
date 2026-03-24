# Define environment variables
export VERSION=0.1
export ACCOUNT=aws:999999999
export APP_NAME=py-client-ecommerce-a2a.localhost
export MODEL_ID=arn:aws:bedrock:us-east-2:908671954593:inference-profile/us.amazon.nova-pro-v1:0
export REGION=us-east-2
export SESSION_ID=py-client-ecommerce-a2a-session-001

# agent py-inventory-a2a
export URL_AGENT_REGISTER_00=http://127.0.0.1:8000
# agent py-cart-a2a
export URL_AGENT_REGISTER_01=http://127.0.0.1:8001
# agent py-stat-a2a
export URL_AGENT_REGISTER_02=http://127.0.0.1:8100
# agent py-kmeans-a2a
export URL_AGENT_REGISTER_03=http://127.0.0.1:8101

export OTEL_EXPORTER_OTLP_ENDPOINT=http://pi-home-01.architecture.caradhras.io:4318/v1/traces
export LOG_LEVEL=INFO
export OTEL_STDOUT_LOG_GROUP=True
export LOG_GROUP=/mnt/c/Eliezer/log/py-client-ecommerce-a2a.log

# Default target
all: env activate run

# Show environment variables
env:
	@echo "Current Environment Variables:"
	@echo "VERSION=$(VERSION)"
	@echo "APP_NAME=$(APP_NAME)"
activate:
	@echo "Activate venv..."
	@bash -c "source ../.venv/bin/activate"

# Run the Python application
run:
	@echo "Running application with environment variables..."
	@bash -c "source ../.venv/bin/activate && python main.py"
    
.PHONY: all env run