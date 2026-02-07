from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import firestore

# เริ่มต้นแอป
app = FastAPI()

# ตั้งค่า CORS (เพื่อให้ Frontend เรียก API ข้าม Domain ได้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ยอมรับทุกเว็บ (เพื่อความง่ายในการทดสอบ)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# เชื่อมต่อ Firestore
db = firestore.Client()

# Model ข้อมูล (ต้องตรงกับที่ Frontend ส่งมา)
class Employee(BaseModel):
    name: str
    position: str
    department: str
    salary: int

@app.get("/")
def read_root():
    return {"message": "Employee API is running!"}

# --- 1. ดึงข้อมูลทั้งหมด (Read) ---
@app.get("/employees/")
def get_employees():
    employees = []
    docs = db.collection("employees").stream()
    for doc in docs:
        emp = doc.to_dict()
        emp["id"] = doc.id
        employees.append(emp)
    return employees

# --- 2. เพิ่มข้อมูลใหม่ (Create) ---
@app.post("/employees/")
async def create_employee(emp: Employee):
    # .add() จะสร้าง ID ให้อัตโนมัติ
    update_time, emp_ref = db.collection("employees").add(emp.dict())
    return {"id": emp_ref.id, "message": "Created successfully"}

# --- 3. แก้ไขข้อมูล (Update) - [ส่วนที่เพิ่มใหม่] ---
@app.put("/employees/{emp_id}")
async def update_employee(emp_id: str, emp: Employee):
    # .set() จะเขียนทับข้อมูลเดิมตาม ID ที่ระบุ
    doc_ref = db.collection("employees").document(emp_id)
    doc_ref.set(emp.dict())
    return {"id": emp_id, "message": "Updated successfully"}

# --- 4. ลบข้อมูล (Delete) ---
@app.delete("/employees/{emp_id}")
async def delete_employee(emp_id: str):
    db.collection("employees").document(emp_id).delete()
    return {"message": "Deleted successfully"}
