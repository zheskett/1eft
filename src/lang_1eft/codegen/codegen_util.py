import rich
import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.pipeline.ast_definitions import *

TYPE_MAP: dict[Type, ir.Type] = {
    VoidType: ir.VoidType,
    DecimalType: ir.IntType(32),
}

ZERO: ir.Constant = ir.Constant(ir.IntType(32), 0)

string_numbers: dict[str, int] = {}


def generate_llvm_machine(triple: str) -> llvm.TargetMachine:
    target = llvm.Target.from_triple(triple)
    target_machine = target.create_target_machine(
        cpu="generic",
        features="",
        opt=0,
    )
    return target_machine


def get_llvm_type(type_node: Type) -> ir.Type:
    ir_type = TYPE_MAP.get(type(type_node))
    if ir_type is not None:
        return ir_type()
    else:
        error_out(f"Unknown type: {type(type_node)}", type_node.line, type_node.column)


def create_global_string(
    module: ir.Module, value: str, name: str = ".str", allow_dup=True
) -> ir.GlobalVariable:
    # Add null terminator
    # bytearray is mutable, that is why it is used instead of bytes
    raw = bytearray(value.encode("utf-8") + b"\00")

    # Create a global string (array of characters)
    str_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(raw)), raw)

    if allow_dup and name in string_numbers:
        string_numbers[name] += 1
        name = f"{name}.{string_numbers[name]}"
    elif allow_dup:
        string_numbers[name] = 0

    global_str = ir.GlobalVariable(module, str_const.type, name=name)
    global_str.linkage = "internal"
    global_str.global_constant = True

    # Set global_string to be initialized to str_const
    global_str.initializer = str_const
    return global_str


def get_puts_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("puts")
    except KeyError:
        puts_type = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()])
        puts_func = ir.Function(module, puts_type, name="puts")
        return puts_func


def get_printf_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("printf")
    except KeyError:
        printf_type = ir.FunctionType(
            ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True
        )
        printf_func = ir.Function(module, printf_type, name="printf")
        return printf_func


def error_out(message: str, line: int, col: int) -> None:
    rich.print(f"[red]Error:[/red] {message} at {line}:{col}")
    raise NotImplementedError(message)
