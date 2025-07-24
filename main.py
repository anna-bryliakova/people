from fastapi import FastAPI
from routers import people
from log import log_middleware


app = FastAPI()

app_v1 = FastAPI()
app.mount("/v1", app_v1)

app.middleware("http")(log_middleware)

app_v1.include_router(people.router)
