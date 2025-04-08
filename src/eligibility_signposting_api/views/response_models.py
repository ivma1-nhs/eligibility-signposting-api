from pydantic import BaseModel


class EligibilityResponse(BaseModel):
    processed_suggestions: list[dict]
