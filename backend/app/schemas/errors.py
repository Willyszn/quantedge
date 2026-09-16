from app.schemas.market import CamelModel


class ErrorDetailSchema(CamelModel):
    code: str
    message: str


class ErrorResponseSchema(CamelModel):
    error: ErrorDetailSchema
