from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, businesses, customers, invoices, users, pdf, admin, roles, user_roles, subscriptions
from .core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(businesses.router)
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(pdf.router)
app.include_router(admin.router)
app.include_router(roles.router)
app.include_router(user_roles.router)
app.include_router(subscriptions.router)

@app.get("/")
async def root():
    return {"message": "Welcome to E-Invoice Builder Supabase API"}
