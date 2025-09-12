from typing import cast
import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.codegen.codegen_util import *
from lang_1eft.codegen.predef_functions import *
from lang_1eft.pipeline.ast_definitions import *


class ModuleBuilder:
    def __init__(
        self,
        ast: Program,
        asm: bool = False,
        verbose: bool = False,
        triple: str | None = None,
        opt: int = 2,
    ) -> None:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.ast = ast
        self.asm = asm
        self.verbose = verbose
        self.triple = triple if triple is not None else llvm.get_default_triple()
        self.opt = opt
        self.machine = generate_llvm_machine(self.triple, self.opt)

        self.module = None

    def build(self) -> None:
        self.module = ir.Module(name="1eft_module")
        self.module.triple = self.triple
        self.module.data_layout = str(self.machine.target_data)

        add_all_predef_functions(self.module)
        for func in self.ast.functions:
            self.build_function(func)

        wrap_main_function(self.module)

    def build_function(self, func_def: FunctionDef) -> None:
        assert self.module is not None
        func_type = ir.FunctionType(
            get_llvm_type(func_def.type),
            [get_llvm_type(p.type) for p in func_def.parameters],
        )
        func = ir.Function(
            self.module, func_type, name=FUNC_PREFIX + func_def.identifier.name
        )

        # Block containing function body
        block = func.append_basic_block(name="entry")

        builder = ir.IRBuilder(block)

        block_values: dict[str, ir.Value] = {}

        # Set function parameters
        for i, param in enumerate(func_def.parameters):
            param_var = builder.alloca(
                get_llvm_type(param.type), name=param.identifier.name
            )
            block_values[param.identifier.name] = param_var
            builder.store(func.args[i], param_var)

        # Build function body
        for stmt in func_def.body.statements:
            self.build_statement(builder, stmt, block_values)

        # Check for return statement
        if not (cast(ir.Block, builder.block).is_terminated):
            if isinstance(func_def.type, VoidType):
                builder.ret_void()
            else:
                error_out(
                    "Non-v@1d function must end with a return statement",
                    func_def.line,
                    func_def.column,
                    self.verbose,
                )
                exit(1)

    def build_statement(
        self, builder: ir.IRBuilder, stmt: Statement, block_values: dict[str, ir.Value]
    ) -> None:
        # DCE
        if cast(ir.Block, builder.block).is_terminated:
            return

        if isinstance(stmt, ExpressionStatement):
            self.build_expression(builder, stmt.expression, block_values)

        elif isinstance(stmt, Return):
            if stmt.value is None:
                builder.ret_void()
            else:
                ret_val = self.build_expression(builder, stmt.value, block_values)
                builder.ret(ret_val)

        elif isinstance(stmt, NoOp):
            pass

        elif isinstance(stmt, VarDeclStatement):
            if stmt.identifier.name in block_values:
                error_out(
                    f"Variable '{stmt.identifier.name}' already declared",
                    stmt.identifier.line,
                    stmt.identifier.column,
                    self.verbose,
                )
                exit(1)

            value = builder.alloca(get_llvm_type(stmt.type), name=stmt.identifier.name)
            block_values[stmt.identifier.name] = value

        elif isinstance(stmt, VarAssStatement):
            ass_var = None
            if isinstance(stmt.lhs, DerefExpr):
                # Dont dereference because we assign to the pointer
                ass_var = self.build_expression(builder, stmt.lhs.value, block_values)

            elif isinstance(stmt.lhs, Identifier):
                if stmt.lhs.name not in block_values:
                    error_out(
                        f"Variable '{stmt.lhs.name}' not declared in this scope",
                        stmt.lhs.line,
                        stmt.lhs.column,
                        self.verbose,
                    )
                    exit(1)
                ass_var = block_values[stmt.lhs.name]

            rich.print(ass_var)

            if ass_var is None:
                error_out(
                    f"Variable assignment failed",
                    stmt.lhs.line,
                    stmt.lhs.column,
                    self.verbose,
                )
                exit(1)

            rich.print(stmt.rhs)
            assign_val = self.build_expression(builder, stmt.rhs, block_values)
            rich.print(assign_val)

            # We check if pointer to char because alloca is stored as a pointer
            if safe_ir_type(assign_val) == i8ptr and safe_ir_type(ass_var) == i8ptr:
                # Get first character of string
                assign_val = builder.load(assign_val)

            rich.print(assign_val)
            builder.store(assign_val, ass_var)

        elif isinstance(stmt, IfStatement):

            def build_elseif(
                builder: ir.IRBuilder,
                if_stmt: IfStatement,
                index: int,
                block_values: dict[str, ir.Value],
            ) -> None:
                elseif = if_stmt.else_ifs[index]
                condition = self.build_expression(
                    builder, elseif.condition, block_values
                )
                verify_ir_type(
                    condition,
                    get_llvm_type(BooleanType),
                    elseif.condition.line,
                    elseif.condition.column,
                    self.verbose,
                )

                # This is the last elseif and there is no else
                if index + 1 >= len(if_stmt.else_ifs) and if_stmt.else_body is None:
                    with builder.if_then(condition):
                        scope = block_values.copy()
                        for statement in elseif.body.statements:
                            self.build_statement(builder, statement, scope)
                    return

                with builder.if_else(condition) as (then, otherwise):
                    with then:
                        scope = block_values.copy()
                        for statement in elseif.body.statements:
                            self.build_statement(builder, statement, scope)
                    with otherwise:
                        # Next statement is an elseif
                        if index + 1 < len(if_stmt.else_ifs):
                            build_elseif(builder, if_stmt, index + 1, block_values)

                        elif if_stmt.else_body is not None:
                            scope = block_values.copy()
                            for statement in if_stmt.else_body.statements:
                                self.build_statement(builder, statement, scope)

                        else:
                            error_out("Unreachable state reached", 1, 1, self.verbose)
                            exit(1)

            condition = self.build_expression(builder, stmt.condition, block_values)
            verify_ir_type(
                condition,
                get_llvm_type(BooleanType),
                stmt.condition.line,
                stmt.condition.column,
                self.verbose,
            )

            if stmt.else_body is None and len(stmt.else_ifs) == 0:
                with builder.if_then(condition):
                    scope = block_values.copy()
                    for statement in stmt.body.statements:
                        self.build_statement(builder, statement, scope)

            else:
                with builder.if_else(condition) as (then, otherwise):
                    with then:
                        scope = block_values.copy()
                        for statement in stmt.body.statements:
                            self.build_statement(builder, statement, scope)
                    with otherwise:
                        if len(stmt.else_ifs) > 0:
                            build_elseif(builder, stmt, 0, block_values)

                        elif stmt.else_body is not None:
                            scope = block_values.copy()
                            for statement in stmt.else_body.statements:
                                self.build_statement(builder, statement, scope)

                        else:
                            error_out("Unreachable state reached", 1, 1, self.verbose)
                            exit(1)

        elif isinstance(stmt, AsStatement):
            this_func: ir.Function = builder.function
            loop_cond_bb: ir.Block = this_func.append_basic_block("ascond")
            loop_bb: ir.Block = this_func.append_basic_block("asloop")
            loop_end_bb: ir.Block = this_func.append_basic_block("asend")

            builder.branch(loop_cond_bb)
            builder.position_at_start(loop_cond_bb)
            condition = self.build_expression(builder, stmt.condition, block_values)
            verify_ir_type(
                condition,
                get_llvm_type(BooleanType),
                stmt.condition.line,
                stmt.condition.column,
                self.verbose,
            )
            builder.cbranch(condition, loop_bb, loop_end_bb)

            builder.position_at_start(loop_bb)
            scope = block_values.copy()
            for statement in stmt.body.statements:
                self.build_statement(builder, statement, scope)
            builder.branch(loop_cond_bb)

            builder.position_at_start(loop_end_bb)

        else:
            error_out(
                f"Unknown statement: {type(stmt)}", stmt.line, stmt.column, self.verbose
            )
            exit(1)

    def build_expression(
        self, builder: ir.IRBuilder, expr: Expression, block_values: dict[str, ir.Value]
    ) -> ir.Value:
        if isinstance(expr, DecimalLiteral):
            return ir.Constant(get_llvm_type(DecimalType), expr.value)

        elif isinstance(expr, StringLiteral):
            string = create_global_string(builder.module, expr.value)
            return builder.gep(string, [ZERO, ZERO], inbounds=True)

        elif isinstance(expr, BooleanLiteral):
            return ir.Constant(get_llvm_type(BooleanType), expr.value)

        elif isinstance(expr, IdentifierExpr):
            if expr.identifier.name not in block_values:
                error_out(
                    f"Variable '{expr.identifier.name}' not declared in this scope",
                    expr.identifier.line,
                    expr.identifier.column,
                    self.verbose,
                )
                exit(1)
            var = block_values[expr.identifier.name]

            return builder.load(var, name=expr.identifier.name)

        elif isinstance(expr, AddressOfExpr):
            if expr.identifier.name not in block_values:
                error_out(
                    f"Variable '{expr.identifier.name}' not declared in this scope",
                    expr.identifier.line,
                    expr.identifier.column,
                    self.verbose,
                )
                exit(1)
            return block_values[expr.identifier.name]

        elif isinstance(expr, DerefExpr):
            value = self.build_expression(builder, expr.value, block_values)
            if not safe_ir_type(value).is_pointer:
                error_out(
                    "Cannot dereference non-pointer type",
                    expr.line,
                    expr.column,
                    self.verbose,
                )
                exit(1)
            return builder.load(value, name=".dereftmp")

        elif isinstance(expr, ExecExpr):
            func_name = expr.identifier.name
            call_func_name = FUNC_PREFIX + func_name
            try:
                func = builder.module.get_global(call_func_name)
            except KeyError:
                error_out(
                    f"Function '{func_name}' not found",
                    expr.line,
                    expr.column,
                    self.verbose,
                )
                exit(1)

            if not isinstance(func, ir.Function):
                error_out(
                    f"'{func_name}' is not a function",
                    expr.line,
                    expr.column,
                    self.verbose,
                )
                exit(1)

            if len(expr.arguments) != len(func.args):
                error_out(
                    f"Function '{func_name}' expects {len(func.args)} arguments, got {len(expr.arguments)}",
                    expr.line,
                    expr.column,
                    self.verbose,
                )
                exit(1)

            # Bit cast arguments that need to be void pointers
            cast_list = []
            if call_func_name in functions_with_void_ptrs:
                cast_list = functions_with_void_ptrs[call_func_name]
            arg_values = []
            for i, arg in enumerate(expr.arguments):
                val = self.build_expression(builder, arg, block_values)
                if i in cast_list:
                    val = builder.bitcast(val, VOID_PTR, name=".voidptrcast")
                arg_values.append(val)

            return builder.call(func, arg_values, name=f"call_{call_func_name}")

        elif isinstance(expr, RevExpr):
            value = self.build_expression(builder, expr.value, block_values)
            verify_ir_type(
                value, get_llvm_type(BooleanType), expr.line, expr.column, self.verbose
            )
            return cast(ir.Instruction, builder.not_(value, name=".revtmp"))

        elif isinstance(expr, OrExpr):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            verify_ir_type(
                lhs, get_llvm_type(BooleanType), expr.line, expr.column, self.verbose
            )
            verify_ir_type(
                rhs, get_llvm_type(BooleanType), expr.line, expr.column, self.verbose
            )
            return cast(ir.Instruction, builder.or_(lhs, rhs, name=".ortmp"))

        elif isinstance(expr, AndExpr):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            verify_ir_type(
                lhs, get_llvm_type(BooleanType), expr.line, expr.column, self.verbose
            )
            verify_ir_type(
                rhs, get_llvm_type(BooleanType), expr.line, expr.column, self.verbose
            )
            return cast(ir.Instruction, builder.and_(lhs, rhs, name=".andtmp"))

        elif isinstance(expr, CmpExpression):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            if (
                isinstance(expr, GreaterThanEqualExpr)
                or isinstance(expr, LessThanEqualExpr)
                or isinstance(expr, GreaterThanExpr)
                or isinstance(expr, LessThanExpr)
            ):
                verify_ir_type(
                    lhs,
                    get_llvm_type(DecimalType),
                    expr.line,
                    expr.column,
                    self.verbose,
                )
                verify_ir_type(
                    rhs,
                    get_llvm_type(DecimalType),
                    expr.line,
                    expr.column,
                    self.verbose,
                )
            else:
                # Types must be the same, and not string types
                if not (safe_ir_type(lhs) == safe_ir_type(rhs)):
                    error_out(
                        f"Cannot compare {safe_ir_type(lhs)} and {safe_ir_type(rhs)}",
                        expr.line,
                        expr.column,
                        self.verbose,
                    )
                    exit(1)
            return builder.icmp_signed(expr.ir_icmp, lhs, rhs, name=f".cmptmp")

        elif isinstance(expr, AddExpr) or isinstance(expr, SubExpr):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            rich.print(safe_ir_type(lhs))
            rich.print(safe_ir_type(rhs))
            if safe_ir_type(lhs).is_pointer or (
                safe_ir_type(rhs).is_pointer and isinstance(expr, AddExpr)
            ):
                # Pointer arithmetic

                if safe_ir_type(lhs).is_pointer and safe_ir_type(rhs).is_pointer:
                    error_out(
                        "Cannot add or subtract two pointer types",
                        expr.line,
                        expr.column,
                        self.verbose,
                    )
                    exit(1)

                if safe_ir_type(rhs).is_pointer and isinstance(expr, AddExpr):
                    lhs, rhs = rhs, lhs

                verify_ir_type(
                    rhs,
                    get_llvm_type(DecimalType),
                    expr.line,
                    expr.column,
                    self.verbose,
                )

                return builder.gep(
                    lhs,
                    [
                        (
                            rhs
                            if isinstance(expr, AddExpr)
                            else builder.neg(rhs, name=".negtemp")
                        )
                    ],
                    inbounds=True,
                    name=".ptrarithtmp",
                )

            else:
                verify_ir_type(
                    lhs,
                    get_llvm_type(DecimalType),
                    expr.line,
                    expr.column,
                    self.verbose,
                )
                verify_ir_type(
                    rhs,
                    get_llvm_type(DecimalType),
                    expr.line,
                    expr.column,
                    self.verbose,
                )

            if isinstance(expr, AddExpr):
                return cast(ir.Instruction, builder.add(lhs, rhs, name=".addtmp"))

            return cast(ir.Instruction, builder.sub(lhs, rhs, name=".subtmp"))

        elif isinstance(expr, MulExpr):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            verify_ir_type(
                lhs, get_llvm_type(DecimalType), expr.line, expr.column, self.verbose
            )
            verify_ir_type(
                rhs, get_llvm_type(DecimalType), expr.line, expr.column, self.verbose
            )
            return cast(ir.Instruction, builder.mul(lhs, rhs, name=".multmp"))

        elif isinstance(expr, DivExpr):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            verify_ir_type(
                lhs, get_llvm_type(DecimalType), expr.line, expr.column, self.verbose
            )
            verify_ir_type(
                rhs, get_llvm_type(DecimalType), expr.line, expr.column, self.verbose
            )
            return cast(ir.Instruction, builder.sdiv(lhs, rhs, name=".divtmp"))

        elif isinstance(expr, ModExpr):
            lhs = self.build_expression(builder, expr.lhs, block_values)
            rhs = self.build_expression(builder, expr.rhs, block_values)
            verify_ir_type(
                lhs, get_llvm_type(DecimalType), expr.line, expr.column, self.verbose
            )
            verify_ir_type(
                rhs, get_llvm_type(DecimalType), expr.line, expr.column, self.verbose
            )
            return cast(ir.Instruction, builder.srem(lhs, rhs, name=".modtmp"))

        else:
            error_out(
                f"Unknown expression: {type(expr)}",
                expr.line,
                expr.column,
                self.verbose,
            )
            exit(1)
