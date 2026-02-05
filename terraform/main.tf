provider "google" {
  project = "employee-manager-486518"
  region  = "asia-southeast1"
}

# 1. สร้าง Database (Firestore)
resource "google_firestore_database" "database" {
  name        = "(default)"
  location_id = "asia-southeast1"
  type        = "FIRESTORE_NATIVE"
}

# 2. สร้าง Pub/Sub Topic (Category IV)
resource "google_pubsub_topic" "employee_topic" {
  name = "new-employee-topic"
}

# 3. สร้าง Cloud Run Service (Category II)
resource "google_cloud_run_service" "api" {
  name     = "employee-api"
  location = "asia-southeast1"

  template {
    spec {
      containers {
        # เราจะระบุ Image URL หลังจาก Build Docker เสร็จ
        image = "asia-southeast1-docker.pkg.dev/employee-manager-486518/employee-repo/employee-api:latest"
        env {
            name = "GCP_PROJECT_ID"
            value = "employee-manager-486518"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# เปิดให้คนทั่วไปเข้าถึง API ได้ (Public)
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output URL เพื่อเอาไปใช้ใน Frontend
output "api_url" {
  value = google_cloud_run_service.api.status[0].url
}
