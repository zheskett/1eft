from pathlib import Path

import lark
import rich


class Parser:
    def __init__(
        self,
        grammar_file: Path = Path("src/lang_1eft/pipeline/grammar.lark"),
        verbose: bool = False,
    ) -> None:
        if verbose:
            rich.print(f"Loading grammar from {grammar_file.resolve()}")
        with grammar_file.open("r") as gf:
            grammar = gf.read()

        self.lark = lark.Lark(grammar, ambiguity="explicit", strict=True)

    def parse(self, code: str) -> lark.ParseTree:
        parsed = None
        try:
            parsed = self.lark.parse(code)
            if str(parsed).count("_ambig") > 0:
                rich.print(
                    f"[red]Ambiguities found in code:[/red] {str(parsed).count('_ambig')}"
                )
                exit(1)
        except lark.exceptions.LarkError as e:
            rich.print(f"[red]Error parsing code:[/red] {e}")
            raise e
        return parsed


if __name__ == "__main__":
    parser = Parser()
    with Path("1eft~srcs/13!1eft").open("r") as f:
        tree = parser.parse(f.read())
    rich.print(tree)
