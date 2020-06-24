from fastapi import APIRouter

from api.resources import sequence

router = APIRouter()

router.include_router(sequence.router, tags=["sequence"], prefix="/sequence")
