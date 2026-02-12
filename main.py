from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import router

app = FastAPI(title="NeuralGarage Video API")

app.include_router(router, prefix="/api")

# Serve minimal frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
	import uvicorn

	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)