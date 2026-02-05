PROJECT_ID=employee-manager-486518
REGION=asia-southeast1
REPO_NAME=employee-repo
IMAGE_NAME=$(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/employee-api

docker-push:
	gcloud builds submit --tag $(IMAGE_NAME) ./backend

infra-deploy:
	cd terraform && terraform init && terraform apply -auto-approve

deploy-all: docker-push infra-deploy
	@echo "Deployment Complete!"
