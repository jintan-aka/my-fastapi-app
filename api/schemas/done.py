from pydantic import BaseModel, ConfigDict  # ← 追加！

class DoneResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)  # ✅ これがv2スタイル！
