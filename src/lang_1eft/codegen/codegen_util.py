import rich
import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.pipeline.ast_definitions import *


i8 = ir.IntType(8)
i32 = ir.IntType(32)
i1 = ir.IntType(1)
i64 = ir.IntType(64)
i8ptr = i8.as_pointer()

ZERO: ir.Constant = ir.Constant(i32, 0)

# For things like FILE*
VOID_PTR = i8ptr


string_numbers: dict[str, int] = {}


def generate_llvm_machine(triple: str, opt: int) -> llvm.TargetMachine:
    target = llvm.Target.from_triple(triple)
    target_machine = target.create_target_machine(
        cpu="generic",
        features="",
        opt=2,
    )
    return target_machine


def get_llvm_type(type_node: Type | type[Type], do_raise: bool = False) -> ir.Type:
    ir_type = None

    if isinstance(type_node, VoidType) or type_node is VoidType:
        ir_type = ir.VoidType()
    elif isinstance(type_node, DecimalType) or type_node is DecimalType:
        ir_type = i32
    elif isinstance(type_node, BooleanType) or type_node is BooleanType:
        ir_type = ir.IntType(1)
    elif isinstance(type_node, StrPtrType) or type_node is StrPtrType:
        ir_type = i8ptr
    else:
        if isinstance(type_node, Type):
            error_out(
                f"Unknown type: {type(type_node)}",
                type_node.line,
                type_node.column,
                do_raise,
            )
            exit(1)
        else:
            error_out(f"Unknown type: {type_node}", 1, 1, do_raise)
            exit(1)

    return ir_type


def safe_ir_type(value: ir.Value, line=1, col=1, do_raise=False) -> ir.Type:
    try:
        return getattr(value, "type")
    except AttributeError:
        error_out(f"Value has no type: {value}", line, col, do_raise)
        exit(1)


def verify_ir_type(
    value: ir.Value, expected_type: ir.Type, line=1, col=1, do_raise=False
) -> None:
    ir_type = safe_ir_type(value, line, col, do_raise)
    if ir_type != expected_type:
        error_out(f"Expected type {expected_type}, got {ir_type}", line, col, do_raise)
        exit(1)


def create_global_string(
    module: ir.Module, value: str, name: str = ".str", allow_dup=True
) -> ir.GlobalVariable:
    # Add null terminator
    # bytearray is mutable, that is why it is used instead of bytes
    raw = bytearray(value.encode("utf-8") + b"\00")

    # Create a global string (array of characters)
    str_const = ir.Constant(ir.ArrayType(i8, len(raw)), raw)

    if allow_dup and name in string_numbers:
        string_numbers[name] += 1
        name = f"{name}.{string_numbers[name]}"
    elif allow_dup:
        string_numbers[name] = 0

    global_str = ir.GlobalVariable(module, str_const.type, name=name)
    global_str.linkage = "internal"
    global_str.global_constant = True

    # Set global_string to be initialized to str_const
    global_str.initializer = str_const  # type: ignore
    return global_str


def get_puts_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("puts")
    except KeyError:
        puts_type = ir.FunctionType(i32, [i8ptr])
        puts_func = ir.Function(module, puts_type, name="puts")
        return puts_func


def get_printf_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("printf")
    except KeyError:
        printf_type = ir.FunctionType(i32, [i8ptr], var_arg=True)
        printf_func = ir.Function(module, printf_type, name="printf")
        return printf_func


def get_fgets_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("fgets")
    except KeyError:
        fgets_type = ir.FunctionType(
            i8ptr,
            [
                i8ptr,
                i32,
                VOID_PTR,
            ],
        )
        fgets_func = ir.Function(module, fgets_type, name="fgets")
        return fgets_func


def get_fdopen(module: ir.Module):
    try:
        return module.get_global("fdopen")
    except KeyError:
        return ir.Function(
            module,
            ir.FunctionType(
                VOID_PTR,
                [i32, i8ptr],
            ),
            name="fdopen",
        )


def get_atoi_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("atoi")
    except KeyError:
        atoi_type = ir.FunctionType(
            i32,
            [i8ptr],
        )
        atoi_func = ir.Function(module, atoi_type, name="atoi")
        return atoi_func


def get_rand_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("rand")
    except KeyError:
        rand_type = ir.FunctionType(
            i32,
            [],
        )
        rand_func = ir.Function(module, rand_type, name="rand")
        return rand_func


def get_srand_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("srand")
    except KeyError:
        srand_type = ir.FunctionType(
            ir.VoidType(),
            [i32],
        )
        srand_func = ir.Function(module, srand_type, name="srand")
        return srand_func


def get_time_function(module: ir.Module) -> ir.Function:
    try:
        return module.get_global("time")
    except KeyError:
        time_type = ir.FunctionType(
            i32,
            [VOID_PTR],
        )
        time_func = ir.Function(module, time_type, name="time")
        return time_func


def error_out(message: str, line: int, col: int, do_raise: bool = False) -> None:
    rich.print(f"[red]Error:[/red] {message} at {line}:{col}")
    if do_raise:
        raise NotImplementedError(message)
