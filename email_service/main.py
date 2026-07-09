import uvicorn
from config import config

if __name__ == "__main__":
    uvicorn.run("app:app", host=config.SERVICE_HOST, port=config.SERVICE_PORT, reload=False)
