from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PyLegifranceBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_by_name=True,
        validate_by_alias=True,
    )
