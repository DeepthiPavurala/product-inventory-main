from typing import Any


def validate_response(model_class: type, response_json: dict[str, Any]):
    """
    Supports both Pydantic v1 and v2.
    """

    if hasattr(model_class, "model_validate"):
        return model_class.model_validate(response_json)

    return model_class.parse_obj(response_json)