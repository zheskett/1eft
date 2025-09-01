import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.pipeline.ast_definitions import *
from lang_1eft.codegen.codegen_util import *


def wrap_main_function(module: ir.Module) -> None:
    start_func = None
    for func in module.functions:
        if (
            func.name == "start"
            and func.function_type.return_type == TYPE_MAP[DecimalType]
            and len(func.args) == 0
        ):
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


def add_all_predef_functions(module: ir.Module) -> None:
    add_wr1te_function(module)
    add_wr1te1_function(module)
    add_wr1ted_function(module)


def add_wr1te_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%s", name=".fmt.s")

    wri1te = ir.Function(
        module,
        ir.FunctionType(TYPE_MAP[VoidType], [ir.IntType(8).as_pointer()]),
        name="wr1te",
    )
    block = wri1te.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Get pointer to the first character of the format string
    fmt_ptr = builder.gep(fmt_str, [ZERO, ZERO], inbounds=True)
    builder.call(printf_func, [fmt_ptr, wri1te.args[0]])
    builder.ret_void()
    return wri1te


def add_wr1te1_function(module: ir.Module) -> ir.Function:
    puts_func = get_puts_function(module)
    wri1te1 = ir.Function(
        module,
        ir.FunctionType(TYPE_MAP[VoidType], [ir.IntType(8).as_pointer()]),
        name="wr1te1",
    )
    block = wri1te1.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.call(puts_func, [wri1te1.args[0]])
    builder.ret_void()
    return wri1te1


def add_wr1ted_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%d", name=".fmt.d")

    wri1ted = ir.Function(
        module,
        ir.FunctionType(TYPE_MAP[VoidType], [TYPE_MAP[DecimalType]]),
        name="wr1ted",
    )
    block = wri1ted.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    fmt_ptr = builder.gep(
        fmt_str,
        [ZERO, ZERO],
        inbounds=True,
    )
    builder.call(printf_func, [fmt_ptr, wri1ted.args[0]])
    builder.ret_void()
    return wri1ted
