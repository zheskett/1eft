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


def create_global_string(
    module: ir.Module, value: str, name: str = ".str"
) -> ir.GlobalVariable:
    # Add null terminator
    # bytearray is mutable, that is why it is used instead of bytes
    raw = bytearray(value.encode("utf-8") + b"\00")

    # Create a global string (array of characters)
    str_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(raw)), raw)

    # Use name .str to show compiler-generated
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


def add_wr1te_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%s\n", name=".fmt")

    wri1te = ir.Function(
        module,
        ir.FunctionType(ir.VoidType(), [ir.IntType(8).as_pointer()]),
        name="wr1te",
    )
    block = wri1te.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Get pointer to the first character of the format string
    fmt_ptr = builder.gep(
        fmt_str,
        [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)],
        inbounds=True,
    )
    builder.call(printf_func, [fmt_ptr, wri1te.args[0]])
    builder.ret_void()
    return wri1te


def add_wr1te1_function(module: ir.Module) -> ir.Function:
    puts_func = get_puts_function(module)
    wri1te1 = ir.Function(
        module,
        ir.FunctionType(ir.VoidType(), [ir.IntType(8).as_pointer()]),
        name="wr1te1",
    )
    block = wri1te1.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.call(puts_func, [wri1te1.args[0]])
    builder.ret_void()
    return wri1te1


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
    ret_val = builder.call(start_func, [], name="call_start")
    builder.ret(ret_val)


def error_out(message: str, line: int, col: int) -> None:
    rich.print(f"[red]Error:[/red] {message} at {line}:{col}")
    raise NotImplementedError(message)
