from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.books import router as books_router
from backend.app.routes.user_books import router as user_books_router



app = FastAPI(
    title="ShelfD API",
    description="Backend API for ShelfD",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the ShelfD API"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "shelfd-api",
    }

app.include_router(books_router)
app.include_router(user_books_router)