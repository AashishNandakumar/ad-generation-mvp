from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ad_generation

app = FastAPI(
    title="Ad Generation MVP",
    description="API for generating ads using AI agents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ad_generation.router, prefix="/api/v1", tags=["ad-generation"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
