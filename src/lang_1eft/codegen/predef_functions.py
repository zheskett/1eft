import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.pipeline.ast_definitions import *
from lang_1eft.codegen.codegen_util import *

GETD_BUFFER_SIZE = 22  # 64-bit int + sign + null terminator + 1


def wrap_main_function(module: ir.Module) -> None:
    start_func = None
    for func in module.functions:
        if (
            func.name == FUNC_PREFIX + "start"
            and func.function_type.return_type == get_llvm_type(DecimalType)
            and len(func.args) == 0
        ):
            start_func = func
            break

    if start_func is None:
        error_out("No valid 'start' function found", 1, 1)
        exit(1)

    builder = ir.IRBuilder()
    builder.position_at_start(start_func.entry_basic_block)
    time_func = get_time_function(module)
    srand_func = get_srand_function(module)

    # Auto seed random
    time_call = builder.call(time_func, [ir.Constant(VOID_PTR, None)], name="call_time")
    builder.call(
        srand_func,
        [time_call],
        name="call_srand",
    )

    func_type = ir.FunctionType(i32, [])
    func = ir.Function(module, func_type, name="main")
    block = func.append_basic_block(name="entry")
    builder.position_at_start(block)
    ret_val = builder.call(start_func, [], name="call_start")
    builder.ret(builder.trunc(ret_val, i32))


def add_all_predef_functions(module: ir.Module) -> None:
    add_wr1te_function(module)
    add_wr1te1_function(module)
    add_wr1ted_function(module)
    add_wr1teb_function(module)
    add_wr1tec_function(module)
    add_wr1tea_function(module)
    add_getd_function(module)
    add_srazd_function(module)
    add_razdd_function(module)


def add_wr1te_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%s", name=".fmt.s")

    wri1te = ir.Function(
        module,
        ir.FunctionType(
            get_llvm_type(VoidType), [get_llvm_type(PointerOf(0, 0, CharType(0, 0)))]
        ),
        name=FUNC_PREFIX + "wr1te",
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
        ir.FunctionType(
            get_llvm_type(VoidType), [get_llvm_type(PointerOf(0, 0, CharType(0, 0)))]
        ),
        name=FUNC_PREFIX + "wr1te1",
    )
    block = wri1te1.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.call(puts_func, [wri1te1.args[0]])
    builder.ret_void()
    return wri1te1


def add_wr1ted_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%ld", name=".fmt.d")

    wri1ted = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(VoidType), [get_llvm_type(DecimalType)]),
        name=FUNC_PREFIX + "wr1ted",
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


def add_wr1teb_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = module.get_global(".fmt.s")
    true_str = create_global_string(module, "true", name=".true")
    false_str = create_global_string(module, "false", name=".false")

    wri1teb = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(VoidType), [get_llvm_type(BooleanType)]),
        name=FUNC_PREFIX + "wr1teb",
    )
    block = wri1teb.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    fmt_ptr = builder.gep(
        fmt_str,
        [ZERO, ZERO],
        inbounds=True,
    )
    bool_val = wri1teb.args[0]
    true_ptr = builder.gep(true_str, [ZERO, ZERO], inbounds=True)
    false_ptr = builder.gep(false_str, [ZERO, ZERO], inbounds=True)
    printf_str = builder.select(bool_val, true_ptr, false_ptr)
    builder.call(printf_func, [fmt_ptr, printf_str])
    builder.ret_void()
    return wri1teb


def add_wr1tec_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%c", name=".fmt.c")

    wri1tec = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(VoidType), [get_llvm_type(CharType)]),
        name=FUNC_PREFIX + "wr1tec",
    )
    block = wri1tec.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    fmt_ptr = builder.gep(
        fmt_str,
        [ZERO, ZERO],
        inbounds=True,
    )
    builder.call(printf_func, [fmt_ptr, wri1tec.args[0]])
    builder.ret_void()
    return wri1tec


def add_wr1tea_function(module: ir.Module) -> ir.Function:
    printf_func = get_printf_function(module)
    fmt_str = create_global_string(module, "%p", name=".fmt.p")

    wri1tea = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(VoidType), [VOID_PTR]),
        name=FUNC_PREFIX + "wr1tea",
    )
    block = wri1tea.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    fmt_ptr = builder.gep(
        fmt_str,
        [ZERO, ZERO],
        inbounds=True,
    )
    builder.call(printf_func, [fmt_ptr, wri1tea.args[0]])
    builder.ret_void()
    functions_with_void_ptrs[wri1tea.name] = [0]
    return wri1tea


def add_getd_function(module: ir.Module) -> ir.Function:
    fgets_func = get_fgets_function(module)
    atol_func = get_atol_function(module)
    fdopen_func = get_fdopen(module)
    mode_str = create_global_string(module, "r", ".mode.r")

    getd = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(DecimalType), []),
        name=FUNC_PREFIX + "getd",
    )
    block = getd.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    mode_ptr = builder.gep(mode_str, [ZERO, ZERO], inbounds=True)
    stdin_FILEptr = builder.call(fdopen_func, [ZERO, mode_ptr])

    buf = builder.alloca(ir.ArrayType(i8, GETD_BUFFER_SIZE), name="getdbuf")
    buf_ptr = builder.gep(buf, [ZERO, ZERO], inbounds=True)

    result = builder.call(
        fgets_func, [buf_ptr, ir.Constant(i32, GETD_BUFFER_SIZE), stdin_FILEptr]
    )

    cond = builder.icmp_unsigned("!=", result, ir.Constant(i8ptr, None))
    builder.ret(
        builder.select(
            cond,
            builder.call(atol_func, [buf_ptr]),
            ir.Constant(get_llvm_type(DecimalType), 0),
        )
    )
    return getd


def add_srazd_function(module: ir.Module) -> ir.Function:
    srand_func = get_srand_function(module)

    srazd = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(VoidType), [get_llvm_type(DecimalType)]),
        name=FUNC_PREFIX + "srazd",
    )
    block = srazd.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.call(srand_func, [builder.trunc(srazd.args[0], i32)])
    builder.ret_void()
    return srazd


def add_razdd_function(module: ir.Module) -> ir.Function:
    rand_func = get_rand_function(module)

    razdd = ir.Function(
        module,
        ir.FunctionType(get_llvm_type(DecimalType), []),
        name=FUNC_PREFIX + "razdd",
    )
    block = razdd.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    rand_block_size = ir.Constant(i32, 0x7FFF)
    rand_blocks = [
        builder.zext(builder.and_(builder.call(rand_func, []), rand_block_size), i64)
        for _ in range(5)
    ]

    builder.ret(
        builder.or_(
            builder.shl(rand_blocks[0], ir.Constant(i64, 48)),
            builder.or_(
                builder.shl(rand_blocks[1], ir.Constant(i64, 35)),
                builder.or_(
                    builder.shl(rand_blocks[2], ir.Constant(i64, 22)),
                    builder.or_(
                        builder.shl(rand_blocks[3], ir.Constant(i64, 9)),
                        builder.lshr(rand_blocks[4], ir.Constant(i64, 4)),
                    ),
                ),
            ),
        )
    )

    return razdd
