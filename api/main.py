from fastapi import FastAPI
from api.routes_documents import router as doc_router
from api.routes_recipients import router as rec_router
from api.routes_forensics import router as for_router

app = FastAPI(title="PRAMAAN API", version="1.0", description="Cryptographic Attribution Prototype")

app.include_router(doc_router)
app.include_router(rec_router)
app.include_router(for_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
