def translate_integer(value: str) -> int:
    return int(
        value[2:-2]
        .replace("@", "0")
        .replace("a", "6")
        .replace("b", "7")
        .replace("c", "8")
        .replace("d", "9")
    )
