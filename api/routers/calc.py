# api/routers/calc.py
from fastapi import APIRouter
from api.schemas.calc import CalcInput, CalcOutput

router = APIRouter()

@router.post("/calc_pow", response_model=CalcOutput)
async def calc_pow(data: CalcInput):
    result = data.input ** 2
    return CalcOutput(ans=result)
