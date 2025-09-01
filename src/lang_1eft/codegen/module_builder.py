import llvmlite.binding as llvm
import llvmlite.ir as ir

from lang_1eft.codegen.codegen_util import *
from lang_1eft.pipeline.ast_definitions import *


class ModuleBuilder:
    def __init__(
        self,
        ast: Program,
        asm: bool = False,
        verbose: bool = False,
        triple: str | None = None,
    ) -> None:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.ast = ast
        self.asm = asm
        self.verbose = verbose
        self.triple = triple if triple is not None else llvm.get_default_triple()
        self.machine = generate_llvm_machine(self.triple)

        self.module = None

    def build(self) -> None:
        self.module = ir.Module(name="1eft_module")
        self.module.triple = self.triple
        self.module.data_layout = self.machine.target_data

        add_wr1te_function(self.module)
        add_wr1te1_function(self.module)
        for func in self.ast.functions:
            self.build_function(func)

        wrap_main_function(self.module)

    def build_function(self, func_def: FunctionDef) -> None:
        assert self.module is not None
        func_type = ir.FunctionType(get_llvm_type(func_def.type), [])
        func = ir.Function(self.module, func_type, name=func_def.identifier.name)

        # Block containing function body
        block = func.append_basic_block(name="entry")

        builder = ir.IRBuilder(block)
        for stmt in func_def.body.statements:
            self.build_statement(builder, stmt)

        # Check for return statement
        if not builder.block.is_terminated:
            if isinstance(func_def.type, VoidType):
                builder.ret_void()
            else:
                error_out(
                    "Non-v@!d function must end with a return statement",
                    func_def.line,
                    func_def.column,
                )

    def build_statement(self, builder: ir.IRBuilder, stmt: Statement) -> None:
        if isinstance(stmt, ExpressionStatement):
            self.build_expression(builder, stmt.expression)

        elif isinstance(stmt, Return):
            ret_val = self.build_expression(builder, stmt.value)
            builder.ret(ret_val)
        else:
            error_out(f"Unknown statement: {type(stmt)}", stmt.line, stmt.column)

    def build_expression(self, builder: ir.IRBuilder, expr: Expression) -> ir.Value:
        if isinstance(expr, DecimalLiteral):
            return ir.Constant(ir.IntType(32), expr.value)
        elif isinstance(expr, StringLiteral):
            string = create_global_string(builder.module, expr.value)
            return builder.gep(
                string,
                [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)],
                inbounds=True,
            )

        elif isinstance(expr, Identifier):
            error_out(f"Not implemented: Identifiers", expr.line, expr.column)

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

            arg_values = [self.build_expression(builder, arg) for arg in expr.arguments]
            print(arg_values)
            return builder.call(func, arg_values, name=f"call_{func_name}")

        elif isinstance(expr, VarDeclStatement):
            error_out(f"Not implemented: Variable Declarations", expr.line, expr.column)

        else:
            error_out(f"Unknown expression: {type(expr)}", expr.line, expr.column)
