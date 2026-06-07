from typing import Any


def to_payload(model_or_dict: Any) -> dict[str, Any]:
    if isinstance(model_or_dict, dict):
        return model_or_dict

    if hasattr(model_or_dict, "model_dump"):
        return model_or_dict.model_dump(exclude_none=True)

    if hasattr(model_or_dict, "dict"):
        return model_or_dict.dict(exclude_none=True)

    raise TypeError(f"Unsupported payload type: {type(model_or_dict)}")