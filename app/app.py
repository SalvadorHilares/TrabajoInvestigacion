from fastapi import FastAPI, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuración DB SQLite
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo Students (tabla única)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class StudentCreate(BaseModel):
    name: str
    age: int

class StudentUpdate(BaseModel):
    name: str | None = None
    age: int | None = None

# Helper para serializar
def student_to_dict(s: Student):
    return {"id": s.id, "name": s.name, "age": s.age}

# FastAPI app
app = FastAPI(title="FastAPI Students API")

# Dependency DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API de estudiantes funcionando en ECS con Fargate!"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Create
@app.post("/students/", status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    student = Student(name=payload.name, age=payload.age)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student_to_dict(student)

# Read All
@app.get("/students/")
def list_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [student_to_dict(s) for s in students]

# Read One
@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student_to_dict(student)

# Update (PUT)
@app.put("/students/{student_id}")
def update_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    if payload.name is not None:
        student.name = payload.name
    if payload.age is not None:
        student.age = payload.age
    db.commit()
    db.refresh(student)
    return student_to_dict(student)

# Delete
@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(student)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
