from pathlib import Path
import subprocess

import rich
import llvmlite.binding as llvm

from lang_1eft.codegen.module_builder import ModuleBuilder


def emit_files(module_builder: ModuleBuilder, output_path: Path) -> None:
    assert module_builder.module is not None
    llvm_ir = llvm.parse_assembly(str(module_builder.module))
    llvm_ir.verify()

    # Make sure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if module_builder.asm:
        output_path.with_suffix(".s").write_text(
            module_builder.machine.emit_assembly(llvm_ir)
        )
    else:
        output_path.with_suffix(".o").write_bytes(
            module_builder.machine.emit_object(llvm_ir)
        )
        link_files(output_path)
        remove_linked_object(output_path)


def link_files(out_path: Path) -> None:
    linker = "cc"
    args = [
        linker,
        "-o",
        str(out_path.with_suffix("")),
        str(out_path.with_suffix(".o")),
    ]

    subprocess.run(args, check=True)


def remove_linked_object(out_path: Path) -> None:
    try:
        out_path.with_suffix(".o").unlink()
    except Exception as e:
        rich.print(f"[yellow]Warning:[/yellow] Could not remove object file: {e}")
