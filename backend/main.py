from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import firestore, pubsub_v1
import os
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตทุกเว็บ (เพื่อให้ง่ายต่อการ dev)
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก Method (GET, POST, etc.)
    allow_headers=["*"],  # อนุญาตทุก Header
)

# ตั้งค่า Google Cloud Project ID
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TOPIC_ID = "new-employee-topic"

# Connect Services
db = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


# Model สำหรับรับค่า
class Employee(BaseModel):
    name: str
    position: str
    department: str
    salary: int


# --- Category I: Concurrency & Async ---
# ใช้ async def เพื่อรองรับ Request พร้อมกันได้จำนวนมาก
@app.post("/employees/")
async def create_employee(emp: Employee):
    try:
        # 1. Save to Firestore
        doc_ref = db.collection("employees").document()
        emp_data = emp.dict()
        doc_ref.set(emp_data)

        # 2. --- Category IV: Pub/Sub ---
        # ส่งข้อมูลเข้า Queue เพื่อไปประมวลผลต่อ (เช่น ส่งเมล/คำนวณเงิน)
        # การทำแบบนี้ทำให้ระบบไม่ค้าง (Non-blocking)
        data_str = f"New employee created: {emp.name}".encode("utf-8")
        future = publisher.publish(topic_path, data_str)
        print(f"Published message ID: {future.result()}")

        return {"id": doc_ref.id, "message": "Saved and queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employees/")
async def get_employees():
    # ดึงข้อมูลมาแสดง
    users_ref = db.collection("employees")
    docs = users_ref.stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


@app.delete("/employees/{emp_id}")
async def delete_employee(emp_id: str):
    try:
        # อ้างอิงถึงเอกสาร (Document) ตาม ID ที่ส่งมา
        doc_ref = db.collection("employees").document(emp_id)

        # ทำการลบ
        doc_ref.delete()

        return {"message": f"Employee {emp_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
