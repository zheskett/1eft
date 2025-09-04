import typer
import rich
import re
from typing_extensions import Annotated
from pathlib import Path


def split_statements(line: str) -> list[str]:
    parts: list[str] = []
    buf = ""
    in_string = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "`":
            in_string = not in_string
            buf += ch
        elif ch == "$" and not in_string:
            buf += ch
            parts.append(buf)
            buf = ""
        elif ch == "!" and not in_string:
            buf += ch
            if i + 1 < len(line) and line[i + 1] == "s":
                buf += "s"
                i += 1
                parts.append(buf)
                buf = ""
        elif ch == "%" and not in_string:
            buf += ch
            if i + 1 < len(line) and line[i + 1] == "s":
                buf += "s"
                i += 1
                parts.append(buf)
                buf = ""
        else:
            buf += ch
        i += 1

    parts.append(buf)
    return parts


# In each line of the 1eft file, we should add whitespace at the end of each line so that word wrap makes it look the the one line is multiple lines
def main(
    files: Annotated[list[Path], typer.Argument(help="The files to process")],
    suffix: Annotated[
        str,
        typer.Option(
            help="The suffix to add to end of file",
        ),
    ] = "",
    wrap: Annotated[
        int,
        typer.Option(
            help="The length to wrap lines at",
        ),
    ] = 120,
) -> None:
    for file in files:
        if not file.exists():
            rich.print(f"[red]File {file} does not exist[/red]")
            continue

        with open(file, "r") as f:
            lines = f.readlines()

        final = ""
        indent = 0
        use_indent = 0
        for line in lines:
            line = line.strip()
            statements = split_statements(line)
            for state in statements:
                statement = state.strip()
                indent -= 2 * statement.count("!s")
                use_indent = min(indent, wrap - 4)
                final += (" " * use_indent) + statement
                remainder = (len(statement) + use_indent) % wrap
                remaining = wrap - remainder
                final += " " * max(remaining, 0)

                indent += 2 * statement.count("%s")
                use_indent = min(indent, wrap - 4)

        with open(file.with_suffix(suffix), "w") as f:
            f.write(final)


if __name__ == "__main__":
    typer.run(main)
