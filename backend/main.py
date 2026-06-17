from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import fda, analyze, report, knowledgebase, verification, chat, auth

app = FastAPI(
    title="AI Pharmacovigilance & Regulatory Intelligence System",
    description="Backend API for AI-based pharmacovigilance and regulatory intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(fda.router)
app.include_router(analyze.router)
app.include_router(report.router)
app.include_router(knowledgebase.router)
app.include_router(verification.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Welcome to the AI Pharmacovigilance System API"}
