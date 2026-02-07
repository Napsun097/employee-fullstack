import firebase_admin
from firebase_admin import credentials, auth
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import firestore

# --- 1. เริ่มต้นระบบ Firebase Admin (ยามเฝ้าประตู) ---
# ใช้ try-except เพื่อกัน Error กรณีมีการ Reload App
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

app = FastAPI()
db = firestore.Client()

# --- 2. ตั้งค่า CORS (รั้วบ้าน) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://employee-manager-486518.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model ข้อมูล
class Employee(BaseModel):
    name: str
    position: str
    department: str
    salary: int

# --- 3. ฟังก์ชันตรวจสอบสิทธิ์ (Security Check) ---
async def verify_token(authorization: str = Header(...)):
    """
    ฟังก์ชันนี้จะดึง Token จาก Header 'Authorization' 
    และตรวจสอบกับ Firebase ว่าเป็นของจริงหรือไม่
    """
    try:
        # รับค่ามาในรูปแบบ "Bearer <token>" ต้องตัดคำว่า Bearer ออก
        token = authorization.split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token # ถ้าผ่าน ให้คืนค่าข้อมูล User กลับไป
    except Exception as e:
        # ถ้าไม่ผ่าน (Token ปลอม หรือ หมดอายุ) ให้ดีดออกทันที
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def read_root():
    return {"message": "Secure Employee API is running!"}

# --- 4. API Endpoints (ล็อกกุญแจเฉพาะจุดที่สำคัญ) ---

# ดึงข้อมูล (GET): อนุญาตให้ทุกคนดูได้ (หรือจะใส่ verify_token ก็ได้ถ้าอยากปิด)
@app.get("/employees/")
def get_employees():
    employees = []
    docs = db.collection("employees").stream()
    for doc in docs:
        emp = doc.to_dict()
        emp["id"] = doc.id
        employees.append(emp)
    return employees

# เพิ่มข้อมูล (POST): **ต้องมี Token**
@app.post("/employees/")
async def create_employee(emp: Employee, user=Depends(verify_token)):
    update_time, emp_ref = db.collection("employees").add(emp.dict())
    return {"id": emp_ref.id, "message": "Created successfully"}

# แก้ไขข้อมูล (PUT): **ต้องมี Token**
@app.put("/employees/{emp_id}")
async def update_employee(emp_id: str, emp: Employee, user=Depends(verify_token)):
    doc_ref = db.collection("employees").document(emp_id)
    doc_ref.set(emp.dict())
    return {"id": emp_id, "message": "Updated successfully"}

# ลบข้อมูล (DELETE): **ต้องมี Token**
@app.delete("/employees/{emp_id}")
async def delete_employee(emp_id: str, user=Depends(verify_token)):
    db.collection("employees").document(emp_id).delete()
    return {"message": "Deleted successfully"}
