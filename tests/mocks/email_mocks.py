from typing import Any


class EmailMock:
    def __init__(self, return_value: bool = False) -> None:
        self.return_value = return_value
        self.calls: list[Any] = []

    def notify_if_low_stock(self, product: Any) -> bool:
        self.calls.append(product)
        return self.return_value

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def was_called_once(self) -> bool:
        return self.call_count == 1

    def was_not_called(self) -> bool:
        return self.call_count == 0