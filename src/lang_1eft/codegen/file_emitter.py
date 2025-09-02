from pathlib import Path
import subprocess

import rich
import llvmlite.binding as llvm

from lang_1eft.codegen.module_builder import ModuleBuilder


def parse_asm(asm: str) -> llvm.ModuleRef:
    mod = llvm.parse_assembly(asm)
    mod.verify()
    return mod


def optimize(llvm_ir: llvm.ModuleRef, module_builder: ModuleBuilder) -> None:
    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = module_builder.opt

    pm = llvm.ModulePassManager()
    fpm = llvm.FunctionPassManager(llvm_ir)

    pmb.populate(pm)
    pmb.populate(fpm)

    fpm.initialize()
    for func in llvm_ir.functions:
        fpm.run(func)
    fpm.finalize()

    pm.run(llvm_ir)

    if module_builder.verbose:
        rich.print("LLVM IR:")
        rich.print(llvm_ir)


def emit_files(module_builder: ModuleBuilder, output_path: Path) -> None:
    assert module_builder.module is not None
    llvm_ir = parse_asm(str(module_builder.module))

    optimize(llvm_ir, module_builder)

    # Make sure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if module_builder.asm:
        output_path.with_suffix(".s").write_text(
            module_builder.machine.emit_assembly(llvm_ir)
        )
        rich.print(
            f"[green]Success:[/green] Output written to {output_path.with_suffix('.s')}"
        )
    else:
        output_path.with_suffix(".o").write_bytes(
            module_builder.machine.emit_object(llvm_ir)
        )
        link_files(output_path)
        remove_linked_object(output_path)
        rich.print(f"[green]Success:[/green] Output written to {output_path}")


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
