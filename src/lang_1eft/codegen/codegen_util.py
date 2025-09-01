import rich
import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.pipeline.ast_definitions import *


def generate_llvm_machine(triple: str) -> llvm.TargetMachine:
    target = llvm.Target.from_triple(triple)
    target_machine = target.create_target_machine(
        cpu="generic",
        features="",
        opt=0,
    )
    return target_machine


def get_llvm_type(type_node: Type) -> ir.Type:
    if isinstance(type_node, VoidType):
        return ir.VoidType()
    elif isinstance(type_node, DecimalType):
        return ir.IntType(32)
    else:
        error_out(f"Unknown type: {type(type_node)}", type_node.line, type_node.column)


def wrap_main_function(module: ir.Module) -> None:
    start_func = None
    for func in module.functions:
        if func.name == "start" and func.function_type.return_type == ir.IntType(32):
            start_func = func
            break

    if start_func is None:
        error_out("No valid 'start' function found", 1, 1)

    func_type = ir.FunctionType(ir.IntType(32), [])
    func = ir.Function(module, func_type, name="main")
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    ret_val = builder.call(start_func, [])
    builder.ret(ret_val)


def error_out(message: str, line: int, col: int) -> None:
    rich.print(f"[red]Error:[/red] {message} at {line}:{col}")
    raise NotImplementedError(message)
