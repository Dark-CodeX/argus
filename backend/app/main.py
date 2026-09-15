from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.user import router as users_router
from app.api.routes.portfolios import router as portfolios_router
from app.api.routes.assets import router as assets_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.market_data import router as market_data_router
from app.api.routes.risk import router as risk_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Financial Risk Intelligence Platform",
    version=settings.app_version,
)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(portfolios_router)
app.include_router(assets_router)
app.include_router(transactions_router)
app.include_router(market_data_router)
app.include_router(risk_router)

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "message": f"{settings.app_name} is running",
        "version": settings.app_version,
        "stage": settings.stage,
        "codename": settings.codename,
    }