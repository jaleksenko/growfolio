import asyncio
from core.database import create_db_and_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users.controllers import router as users_router
from assets.controllers import router as assets_router
from watchlist.controllers import router as watchlist_router
from portfolio.controllers import router as portfolio_router

import logging

# # Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.info("🚀 FastAPI is starting...")


app = FastAPI()

### CORS CONFIGURATION ###
## Point the list of domains, which are allowed to connect
origins = [
    "http://localhost:3000",
    "http://localhost",
    ]

## Add CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the user routes
app.include_router(users_router)
app.include_router(assets_router)
app.include_router(watchlist_router)
app.include_router(portfolio_router)

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


if __name__ == "__main__":
    import uvicorn
    # import debugpy

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # debugpy.listen(("0.0.0.0", 5678))
    # debugpy.wait_for_client()
