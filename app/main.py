from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(title='Excel Analysis API')

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=['*']

)

app.include_router(router)


@app.get("/")
def home():
    return {" message": "Excel Analysis API is running"}
