"""
Meatcraft Voice Ordering Backend — FastAPI Application Entry Point.

Configures:
- CORS middleware
- Logging
- Database table creation on startup
- All API routers
"""
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection

# Import routers
from app.routers import auth, cart, order, payment, pos, rightside, webhook

# ── Settings ──
settings = get_settings()

# ── Logging Configuration ──
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
# Silence verbose third-party loggers
logging.getLogger("pymongo").setLevel(logging.WARNING)

logger = logging.getLogger("meatcraft")

# ── FastAPI App ──
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Voice-based restaurant ordering backend for Meatcraft. "
        "Integrates with Twilio, Ultravox, Razorpay, and Petpooja POS."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup Event ──
@app.on_event("startup")
async def on_startup():
    """Initialize MongoDB connection on startup."""
    logger.info("Starting Meatcraft backend...")
    logger.info(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")

    # Connect MongoDB
    await connect_to_mongo()
    logger.info("MongoDB connected successfully ✓")


# ── Shutdown Event ──
@app.on_event("shutdown")
async def on_shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down Meatcraft backend...")
    await close_mongo_connection()


# ── Register Routers ──
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(cart.router, prefix="/api", tags=["Cart"])
app.include_router(order.router, prefix="/api", tags=["Orders"])
app.include_router(payment.router, prefix="/api", tags=["Payments"])
app.include_router(pos.router, prefix="/api", tags=["POS"])
app.include_router(rightside.router, prefix="/api", tags=["Rightside"])
app.include_router(webhook.router, prefix="/webhook", tags=["Webhooks"])


# ── Health Check ──
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
