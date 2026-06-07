from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Generic, TypeVar
from urllib.parse import urlencode

try:
    from pydantic import TypeAdapter
except ImportError:
    TypeAdapter = None


T = TypeVar("T")


class ApiResponse(Generic[T]):
    def __init__(
        self,
        status_code: int,
        body: bytes,
        response_model: type[T] | Any | None = None,
    ) -> None:
        self.status_code = status_code
        self._body = body
        self.text = body.decode("utf-8", errors="replace")
        self.response_model = response_model
        self.data: T | None = self._validate_response()

    def json(self) -> Any:
        if not self.text:
            return None

        return json.loads(self.text)

    def _validate_response(self) -> T | None:
        if self.response_model is None:
            return None

        response_json = self.json()

        if hasattr(self.response_model, "model_validate"):
            return self.response_model.model_validate(response_json)

        if hasattr(self.response_model, "parse_obj"):
            return self.response_model.parse_obj(response_json)

        if TypeAdapter is not None:
            return TypeAdapter(self.response_model).validate_python(response_json)

        return response_json


class RequestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        response_model: type[T] | Any | None = None,
    ) -> ApiResponse[T]:
        url = f"{self.base_url}{path}"

        if params:
            clean_params = {
                key: value
                for key, value in params.items()
                if value is not None
            }

            query_string = urlencode(clean_params)

            if query_string:
                url = f"{url}?{query_string}"

        data = None
        headers = {"Content-Type": "application/json"}

        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return ApiResponse(
                    status_code=response.status,
                    body=response.read(),
                    response_model=response_model,
                )

        except urllib.error.HTTPError as exc:
            return ApiResponse(
                status_code=exc.code,
                body=exc.read(),
                response_model=response_model,
            )

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        response_model: type[T] | Any | None = None,
    ) -> ApiResponse[T]:
        return self._request(
            method="GET",
            path=path,
            params=params,
            response_model=response_model,
        )

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        response_model: type[T] | Any | None = None,
    ) -> ApiResponse[T]:
        return self._request(
            method="POST",
            path=path,
            json_body=json,
            response_model=response_model,
        )

    def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        response_model: type[T] | Any | None = None,
    ) -> ApiResponse[T]:
        return self._request(
            method="PATCH",
            path=path,
            json_body=json,
            response_model=response_model,
        )

    def delete(
        self,
        path: str,
        response_model: type[T] | Any | None = None,
    ) -> ApiResponse[T]:
        return self._request(
            method="DELETE",
            path=path,
            response_model=response_model,
        )