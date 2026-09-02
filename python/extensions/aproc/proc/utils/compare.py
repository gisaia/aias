def includes_case_insensitive(value: str, allowed_values: list[str]) -> bool:
    return any(s.lower() == value.lower() for s in allowed_values)
