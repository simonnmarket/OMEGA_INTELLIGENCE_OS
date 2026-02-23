#!/usr/bin/env python3
"""
🏦 API REST MAIN - NCNT Tier-0
FastAPI application principal
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import strategies

app = FastAPI(
    title="NCNT Trading System API",
    description="Núcleo Central Neuro Transmissor - Goldman Sachs Tier-0",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(strategies.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "system": "NCNT - Núcleo Central Neuro Transmissor",
        "version": "2.0.0",
        "tier": "Goldman Sachs Tier-0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check global"""
    return {
        "status": "healthy",
        "system": "NCNT"
    }

