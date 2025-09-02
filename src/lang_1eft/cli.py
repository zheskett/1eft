from pathlib import Path
from typing import Any
from typing_extensions import Annotated

import rich
from rich.tree import Tree
import typer


from lang_1eft.pipeline.parser import Parser
from lang_1eft.pipeline.ast_constructor import ASTConstructor
from lang_1eft.pipeline.ast_definitions import *

from lang_1eft.codegen.module_builder import ModuleBuilder
from lang_1eft.codegen.file_emitter import emit_files


def compile(
    input_path: Annotated[Path, typer.Argument(help="The 1eft file to compile")],
    output_path: Annotated[
        Path, typer.Argument(help="The output executable file")
    ] = Path("1eft_out"),
    asm: Annotated[bool, typer.Option(help="Output assembly code only")] = False,
    verbose: Annotated[bool, typer.Option(help="Enable verbose output")] = False,
    build: Annotated[bool, typer.Option(help="Build the project")] = True,
    opt: Annotated[int, typer.Option(help="Optimization level (0-3)")] = 2,
) -> None:
    """
    Compile a 1eft source file to an executable.
    """
    if not input_path.exists():
        rich.print(f"[red]Error:[/red] Input file {input_path} does not exist")
        raise typer.Exit(code=1)

    if not (0 <= opt <= 3):
        rich.print(f"[red]Error:[/red] Optimization level must be between 0 and 3")
        raise typer.Exit(code=1)

    with input_path.open("r") as f:
        code = f.read()

    parser = Parser()
    parse_tree = parser.parse(code)

    # try:
    #     pydot__tree_to_png(parse_tree, str(input.with_suffix(".png")), rankdir="TB")
    # except:
    #     rich.print("[yellow]Warning:[/yellow] Could not generate parse tree image")

    ast = ASTConstructor().transform(parse_tree)
    assert isinstance(ast, Program)
    if verbose:
        rich.print(make_tree(ast))

    if build:
        module_builder = ModuleBuilder(ast, asm=asm, verbose=verbose, opt=opt)
        module_builder.build()
        assert module_builder.module is not None

        emit_files(module_builder, output_path)
        rich.print(f"[green]Success:[/green] Output written to {output_path}")


def make_tree(ast: Any) -> Tree:
    tree = Tree(
        f"{type(ast).__name__}: [yellow]{getattr(ast, 'line', '')} {getattr(ast, 'column', '')}[/yellow]"
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
    typer.run(compile)


if __name__ == "__main__":
    main()
