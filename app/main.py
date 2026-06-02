from fastapi import FastAPI
from .routers import models, authentication, users, tickets, admin, internal_admin

app = FastAPI()

app.include_router(models.router)
app.include_router(users.router)
app.include_router(authentication.router)
app.include_router(tickets.router)
app.include_router(admin.router)
app.include_router(internal_admin.router)

