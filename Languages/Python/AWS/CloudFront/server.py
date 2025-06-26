from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the directory containing your React build (e.g., 'build' folder)
app.mount("/static", StaticFiles(directory="path/to/your/react/build"), name="static")

# Serve the index.html for your React single-page-application (SPA)
@app.get("/")
async def read_root():
    with open("path/to/your/react/build/index.html") as f:
        return f.read()
