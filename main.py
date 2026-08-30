import uvicorn
from config import Settings

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=Settings().APP_PORT, reload=True)
