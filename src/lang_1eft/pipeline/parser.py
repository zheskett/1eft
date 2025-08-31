from pathlib import Path

import lark
import rich


class Parser:
    def __init__(
        self, grammar_file: Path = Path("src/lang_1eft/pipeline/grammar.lark")
    ) -> None:
        print(f"Loading grammar from {grammar_file.resolve()}")
        with grammar_file.open("r") as gf:
            grammar = gf.read()

        self.lark = lark.Lark(grammar, ambiguity="explicit")

    def parse(self, code: str) -> lark.ParseTree:
        parsed = None
        try:
            parsed = self.lark.parse(code)
        except lark.exceptions.LarkError as e:
            rich.print(f"[red]Error parsing code:[/red] {e}")
            raise e
        return parsed


if __name__ == "__main__":
    parser = Parser()
    with Path("1eft~srcs/1!1eft").open("r") as f:
        tree = parser.parse(f.read())
    rich.print(tree)
