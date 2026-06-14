from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.api import query, ingest, documents, feedback, sessions
from app.core.config import settings
from app.utils.logger import setup_logger
from app.auth.jwt_auth import create_access_token
from datetime import timedelta

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    setup_logger()

# Token generation route for testing
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Mock user auth
    if form_data.username == "admin" and form_data.password == "admin":
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
