from fastapi import FastAPI

app = FastAPI(title="FastAPI on ECS Fargate")

@app.get("/")
def root():
    return {"message": "API funcionando en ECS con Fargate + ALB + ECR!"}

@app.get("/health")
def health():
    return {"status": "ok"}
