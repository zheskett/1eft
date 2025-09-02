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
        self.module.data_layout = self.machine.target_data

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
        func = ir.Function(self.module, func_type, name=func_def.identifier.name)

        # Block containing function body
        block = func.append_basic_block(name="entry")

        builder = ir.IRBuilder(block)

        block_values: dict[str, ir.Value] = {}

        for stmt in func_def.body.statements:
            self.build_statement(builder, stmt, block_values)

        # Check for return statement
        if not builder.block.is_terminated:
            if isinstance(func_def.type, VoidType):
                builder.ret_void()
            else:
                error_out(
                    "Non-v@1d function must end with a return statement",
                    func_def.line,
                    func_def.column,
                )

    def build_statement(
        self, builder: ir.IRBuilder, stmt: Statement, block_values: dict[str, ir.Value]
    ) -> None:
        if isinstance(stmt, ExpressionStatement):
            self.build_expression(builder, stmt.expression, block_values)

        elif isinstance(stmt, Return):
            ret_val = self.build_expression(builder, stmt.value, block_values)
            builder.ret(ret_val)

        elif isinstance(stmt, VarDeclStatement):
            if stmt.identifier.name in block_values:
                error_out(
                    f"Variable '{stmt.identifier.name}' already declared",
                    stmt.identifier.line,
                    stmt.identifier.column,
                )

            value = builder.alloca(get_llvm_type(stmt.type), name=stmt.identifier.name)
            block_values[stmt.identifier.name] = value

        elif isinstance(stmt, VarAssStatement):
            if stmt.identifier.name not in block_values:
                error_out(
                    f"Variable '{stmt.identifier.name}' not declared in this scope",
                    stmt.identifier.line,
                    stmt.identifier.column,
                )

            assign_val = self.build_expression(builder, stmt.value, block_values)
            builder.store(assign_val, block_values[stmt.identifier.name])

        else:
            error_out(f"Unknown statement: {type(stmt)}", stmt.line, stmt.column)

    def build_expression(
        self, builder: ir.IRBuilder, expr: Expression, block_values: dict[str, ir.Value]
    ) -> ir.Value:
        if isinstance(expr, DecimalLiteral):
            return ir.Constant(get_llvm_type(DecimalType), expr.value)

        elif isinstance(expr, StringLiteral):
            string = create_global_string(builder.module, expr.value)
            return builder.gep(string, [ZERO, ZERO], inbounds=True)

        elif isinstance(expr, IdentifierExpr):
            if expr.identifier.name not in block_values:
                error_out(
                    f"Variable '{expr.identifier.name}' not declared in this scope",
                    expr.identifier.line,
                    expr.identifier.column,
                )
            var = block_values[expr.identifier.name]

            return builder.load(var, name=expr.identifier.name)

        elif isinstance(expr, Exec):
            func_name = expr.identifier.name
            func = None
            try:
                func = builder.module.get_global(func_name)
            except KeyError:
                func = None

            if func is None or not isinstance(func, ir.Function):
                error_out(f"Function '{func_name}' not found", expr.line, expr.column)

            if len(expr.arguments) != len(func.args):
                error_out(
                    f"Function '{func_name}' expects {len(func.args)} arguments, got {len(expr.arguments)}",
                    expr.line,
                    expr.column,
                )

            arg_values = [
                self.build_expression(builder, arg, block_values)
                for arg in expr.arguments
            ]
            return builder.call(func, arg_values, name=f"call_{func_name}")

        else:
            error_out(f"Unknown expression: {type(expr)}", expr.line, expr.column)
