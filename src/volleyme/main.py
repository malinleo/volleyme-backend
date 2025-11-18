import fastapi
from src.config import settings


app = fastapi.FastAPI(debug=settings.DEBUG)
