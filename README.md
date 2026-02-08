#Employee Manager (Full-Stack Cloud Native)

ระบบจัดการพนักงานแบบครบวงจร พัฒนาด้วยสถาปัตยกรรม Cloud Native บน Google Cloud Platform (GCP) และ Firebase รองรับการทำงานแบบ Concurrency และ Infrastructure as Code

##Architecture & Technologies

โปรเจกต์นี้ประกอบด้วยเทคโนโลยีตามเกณฑ์มาตรฐาน:

- **Frontend:** HTML/JS (Deployed on **Firebase Hosting**)
- **Backend:** Python FastAPI (Async/Concurrency) (Deployed on **Cloud Run**)
- **Database:** Google Cloud **Firestore** (NoSQL)
- **Messaging:** Google Cloud **Pub/Sub** (Asynchronous Messaging)
- **Infrastructure as Code:** **Terraform**
- **Containerization:** **Docker** & **Artifact Registry**
- **CI/CD Ops:** **Cloud Build** & **Makefile**

##Project Structure

```bash
├── backend/            # Python FastAPI Source Code & Dockerfile
├── frontend/           # HTML/JS for Firebase Hosting
├── terraform/          # Infrastructure Definition (IaC)
├── Makefile            # Automation Commands
└── README.md           # Project Documentation
