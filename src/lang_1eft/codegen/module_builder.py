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
        if isinstance(stmt, Return):
            ret_val = self.build_expression(builder, stmt.value)
            builder.ret(ret_val)
        else:
            error_out(f"Unknown statement: {type(stmt)}", stmt.line, stmt.column)

    def build_expression(self, builder: ir.IRBuilder, expr: Expression) -> ir.Value:
        if isinstance(expr, Literal):
            return ir.Constant(ir.IntType(32), expr.value)
        else:
            error_out(f"Unknown expression: {type(expr)}", expr.line, expr.column)
