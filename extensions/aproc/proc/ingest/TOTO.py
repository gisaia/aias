from typing import List, TypeVar

T = TypeVar("T")


def first(container: List[T]) -> T:
    print(container)
    return "a"  # mypy raises: Incompatible return value type (got "str", expected "T")


if __name__ == "__main__":
    list_one: List[str] = ["a", "b", "c"]
    print(first(list_one))
