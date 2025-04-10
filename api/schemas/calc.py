from pydantic import BaseModel

class CalcInput(BaseModel):
    input: int

class CalcOutput(BaseModel):
    ans: int
