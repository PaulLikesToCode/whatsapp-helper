IMAGE_NAME = whatsapp-helper
TAG = latest
FULL_IMAGE = $(IMAGE_NAME):$(TAG)
NODE_IMAGE = $(IMAGE_NAME)-node:$(TAG)

.PHONY: build run push clean

# Build the Docker image
build:
	docker build -t $(FULL_IMAGE) .

# Run the Docker image interactively
run:
	docker run --rm -it $(FULL_IMAGE)

# Push the Docker image to the registry (assumes logged in)
push:
	docker push $(FULL_IMAGE)

# Remove the local Docker image
clean:
	docker rmi -f $(FULL_IMAGE)

# Build the Docker image just for the node application
build-node:
	docker build -f Dockerfile.node -t $(NODE_IMAGE) .

