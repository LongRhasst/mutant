from fastapi import APIRouter
from .Services import run_model_service
import asyncio

router = APIRouter()

semaphore = asyncio.Semaphore(10)
@router.post("/run/", tags=["Model"])
async def run_model(SMILES: list[str]):
    async with semaphore:
        result = await run_model_service(SMILES)
        return result