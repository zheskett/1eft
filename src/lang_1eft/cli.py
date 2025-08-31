from pathlib import Path

from typing import Any
import rich
from rich.tree import Tree
import typer
from lark.tree import pydot__tree_to_png

from lang_1eft.pipeline.parser import Parser
from lang_1eft.pipeline.ast_constructor import ASTConstructor
from lang_1eft.pipeline.ast_definitions import *

app = typer.Typer()


@app.command(help="Run a 1eft source file")
def run():
    rich.print("[yellow]Warning:[/yellow] Run functionality not yet implemented")


@app.command(help="Compile a 1eft source file to an output file")
def compile(input: Path, output: Path = Path("1eft.out")) -> None:
    if not input.exists():
        rich.print(f"[red]Error:[/red] Input file {input} does not exist")
        raise typer.Exit(code=1)

    with input.open("r") as f:
        code = f.read()

    parser = Parser()
    parse_tree = parser.parse(code)

    try:
        pydot__tree_to_png(parse_tree, str(input.with_suffix(".png")), rankdir="TB")
    except:
        rich.print("[yellow]Warning:[/yellow] Could not generate parse tree image")

    ast = ASTConstructor().transform(parse_tree)
    assert isinstance(ast, Program)
    rich.print(make_tree(ast))


def make_tree(ast: Any) -> Tree:
    tree = Tree(
        f"{type(ast).__name__}: [i]{getattr(ast, 'line', '')} {getattr(ast, 'column', '')}[/i]"
    )
    if isinstance(ast, ASTNode):
        for field, value in ast.__dict__.items():
            if field in ("line", "column"):
                continue
            if isinstance(value, list):
                for item in value:
                    tree.add(make_tree(item))
            else:
                tree.add(make_tree(value))
    else:
        tree.add(f"[red]{repr(ast)}[/red]")
    return tree


def main():
    app()


if __name__ == "__main__":
    main()
