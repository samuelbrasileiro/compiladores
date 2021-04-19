# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GrammarParser import GrammarParser
else:
    from GrammarParser import GrammarParser

 
import sys
err = sys.stderr.write
def printf(string, *args):
    sys.stdout.write(string % args)

import struct
import math
# Função utilizada para transformar um valor float para um valor hexadecimal 
# (o equivalente em hexadecimal dos valores dos bits de um float)
def float_to_hex(f):
    float_hex = hex(struct.unpack('<Q', struct.pack('<d', f))[0])
    if (int(float_hex[10],16) % 2 != 0):
        if (float_hex[10] == 'f'):
            float_hex = float(math.ceil(f))
        else:
            float_hex = float_hex[:10] + hex(int(float_hex[10],16) + 1)[2] + "0000000"

    else: 
        float_hex = float_hex[:11] + "0000000"
    return float_hex


# retorne Type.INT, etc para fazer checagem de tipos
class Type:
    VOID = "void"
    INT = "int"
    FLOAT = "float"
    STRING = "char *"

def llvm_type(tyype):
    if tyype == Type.VOID:
        return "void"
    if tyype == Type.INT:
        return "i32"
    if tyype == Type.FLOAT:
        return "float"
    return str(tyype)

def printAlloca(register, lltyype, align, has_tab=bool):
    lltyype = llvm_type(lltyype)
    print("{}%{} = alloca {}, align {}".format("\t" if has_tab else "", str(register), lltyype, str(align)))

def printStore(register_to_store, lltyype_to_store, register_to_be_stored, lltyype_to_be_stored, align, has_tab=False, is_constant=False):
    lltyype_to_store = llvm_type(lltyype_to_store)
    lltyype_to_be_stored = llvm_type(lltyype_to_be_stored)
    if is_constant:
        print("{}store {} {}, {}* %{}, align {}".format("\t" if has_tab else "", lltyype_to_store, str(register_to_store), lltyype_to_be_stored, str(register_to_be_stored), str(align)))
    else:
        print("{}store {} %{}, {}* %{}, align {}".format("\t" if has_tab else "", lltyype_to_store, str(register_to_store), lltyype_to_be_stored, str(register_to_be_stored), str(align)))

def printOper(ll_oper, register, lltyype, register1, register2, has_tab=bool, r1_is_constant=True, r2_is_constant=True):
    lltyype = llvm_type(lltyype)
    if not r1_is_constant:
        register1 = "%" + str(register1)
    if not r2_is_constant:
        register2 = "%" + str(register2)
    
    print("{}%{} = {} {} {}, {}".format("\t" if has_tab else "", str(register), str(ll_oper), str(lltyype), str(register1), str(register2)))

def printLoad(register_to_be_loaded, lltyype_to_be_loaded, register_to_load, lltyype_to_load, align, has_tab=False):
    lltyype_to_load = llvm_type(lltyype_to_load)
    lltyype_to_be_loaded = llvm_type(lltyype_to_be_loaded)
    print("{}%{} = load {}, {}* %{}, align {}".format("\t" if has_tab else "", str(register_to_be_loaded), lltyype_to_be_loaded, lltyype_to_load, str(register_to_load), str(align)))
    

# This class defines a complete generic visitor for a parse tree produced by GrammarParser.
class GrammarCheckerVisitor(ParseTreeVisitor):
    ids_defined = {} # armazenar informações necessárias para cada identifier definido
    inside_what_function = ""
    next_ir_register = 0


    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx:GrammarParser.FiileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx:GrammarParser.Function_definitionContext):
        self.next_ir_register = 0
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()

        params = self.visit(ctx.arguments())

        cte_value = None
        ir_register = None

        params_tyypes = [self.ids_defined[name][0] for name in params]

        self.ids_defined[name] = tyype, params_tyypes, cte_value, ir_register
        self.inside_what_function = name
        self.next_ir_register = len(params) + 1

        params_text = ""

        for index in range(len(params_tyypes)):
            if index > 0:
                params_text += ", "
            
            params_text += "{} %{}".format(llvm_type(params_tyypes[index]), index)

        print("define {} @{}({})".format(llvm_type(tyype), name, params_text) + "{")
        
        for index in range(len(params)):
            printAlloca(params[index], llvm_type(params_tyypes[index]), 4, True)
            printStore(index, llvm_type(params_tyypes[index]), params[index], llvm_type(params_tyypes[index]), 4, True)


        self.visit(ctx.body())

        print("}")

        return


    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx:GrammarParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx:GrammarParser.StatementContext):
        if ctx.RETURN() != None:
            token = ctx.RETURN().getPayload()
            function_type, params, cte_value, ir_register = self.ids_defined[self.inside_what_function]
            if ctx.expression() != None:
                tyype, cte_value, ir_register = self.visit(ctx.expression())

                if function_type == Type.INT and tyype == Type.FLOAT:
                    err("WARNING: possible loss of information returning float expression from int function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                elif function_type != Type.VOID and tyype == Type.VOID:
                    err("ERROR: trying to return void expression from function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif function_type == Type.VOID and tyype != Type.VOID:
                    err("ERROR: trying to return a non void expression from void function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
            elif function_type != Type.VOID:
                err("ERROR: trying to return void expression from function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)



        else:
            self.visitChildren(ctx)
        return


    # Visit a parse tree produced by GrammarParser#if_statement.
    def visitIf_statement(self, ctx:GrammarParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#else_statement.
    def visitElse_statement(self, ctx:GrammarParser.Else_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_loop.
    def visitFor_loop(self, ctx:GrammarParser.For_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_initializer.
    def visitFor_initializer(self, ctx:GrammarParser.For_initializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_condition.
    def visitFor_condition(self, ctx:GrammarParser.For_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_step.
    def visitFor_step(self, ctx:GrammarParser.For_stepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#variable_definition.
    def visitVariable_definition(self, ctx:GrammarParser.Variable_definitionContext):
        tyype = ctx.tyype().getText()
        llvm_tyype = llvm_type(tyype)
        ir_register = None
        is_inside = self.inside_what_function != ""
        # identifiers
        for i in range(len(ctx.identifier())):
            name = ctx.identifier(i).getText()

            token = ctx.identifier(i).IDENTIFIER().getPayload()
            printAlloca(name, llvm_tyype, 4, is_inside)

            if ctx.expression(i) != None:
                expr_type, cte_value, ir_register = self.visit(ctx.expression(i))
                llvm_expr_type = llvm_type(expr_type)
               
                if expr_type == Type.VOID:
                    err("ERROR: trying to assign void expression to variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif expr_type == Type.FLOAT and tyype == Type.INT:
                    err("WARNING: possible loss of information assigning float expression to int variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")

                
                if cte_value != None:
                    cte_value_str = str(cte_value)
                    if expr_type == Type.FLOAT:
                        cte_value_str = float_to_hex(float(cte_value))
                        
                    printStore(cte_value_str, llvm_tyype, name, llvm_expr_type, 4, is_inside, True)
           
            else:
                # unitialized variables now get value 0
                cte_value = 0
                ir_register = None
            self.ids_defined[name] = tyype, -1, cte_value, ir_register # -1 means not a array, therefore no length here (vide 15 lines below)

        # arrays
        for i in range(len(ctx.array())):
            name = ctx.array(i).identifier().getText()
            token = ctx.array(i).identifier().IDENTIFIER().getPayload()

            array_length, _ = self.visit(ctx.array(i))
            if ctx.array_literal(i) != None:
                expr_types, cte_values_array, ir_registers_array = self.visit(ctx.array_literal(i))
                for j in range(len(expr_types)):
                    if expr_types[j] == Type.VOID:
                        err("ERROR: trying to initialize void expression to array '" + name + "' at index " + str(j) + " of array literal in line " + str(token.line) + " and column " + str(token.column) + "\n")
                        exit(-1)
                    elif expr_types[j] == Type.FLOAT and tyype == Type.INT:
                        err("WARNING: possible loss of information initializing float expression to int array '" + name + "' at index " + str(j) + " of array literal in line " + str(token.line) + " and column " + str(token.column) + "\n")
            else:
                # unitialized variables now get value 0
                cte_values_array = [0] * array_length
                ir_registers_array = [None] * array_length
            self.ids_defined[name] = tyype, array_length, cte_values_array, ir_registers_array

        return


    # Visit a parse tree produced by GrammarParser#variable_assignment.
    def visitVariable_assignment(self, ctx:GrammarParser.Variable_assignmentContext):
        op = ctx.OP.text
        llvm_op = ""
        name = None
        tyype = None
        cte_value = None
        ir_register = None
        is_inside = self.inside_what_function != ""

        # identifier assignment
        if ctx.identifier() != None:
            name = ctx.identifier().getText()
            llvm_name = "%" + name


            token = ctx.identifier().IDENTIFIER().getPayload()

            try:
                tyype, _, cte_value, ir_register = self.ids_defined[name]
                
            except:
                err("ERROR: undefined variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)
                return

        # array assignment
        else:
            name = ctx.array().identifier().getText()
            token = ctx.array().identifier().IDENTIFIER().getPayload()
            try:
                tyype, array_length, cte_values_array, ir_registers_array = self.ids_defined[name]
            except:
                err("ERROR: undefined array '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)
            array_index_cte, array_index_ir = self.visit(ctx.array())
            if array_index_cte == None:
                cte_value = None
            else:
                if array_index_cte < 0 or array_index_cte >= array_length:
                    err("ERROR: array '" + name + "' index out of range in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                else:
                    cte_value = cte_values_array[array_index_cte]
                    ir_register = ir_registers_array[array_index_cte]


        if op == '++' or op == '--':
            printLoad(self.next_ir_register, tyype, name, tyype, 4, is_inside)

            self.next_ir_register += 1

            if cte_value != None:
                if op == '++':
                    cte_value += 1

                elif op == '--':
                    cte_value -= 1

            else:
                cte_value = None

            if op == '++':
                if (tyype == Type.FLOAT):
                    llvm_op = "fadd"
                else:
                    
                    llvm_op = "add"

            elif op == '--':

                if (tyype == Type.FLOAT):
                    llvm_op = "fsub"
                else:
                    llvm_op = "sub"
            one_value = 1
            if tyype == Type.FLOAT:
                one_value = float_to_hex(float(one_value))
            
            llvm_tyype = llvm_type(tyype)
            printOper(llvm_op, self.next_ir_register, llvm_tyype, self.next_ir_register - 1, one_value, is_inside, False, True)

            printStore(self.next_ir_register, llvm_tyype, name, llvm_tyype, 4, is_inside, False)

            self.next_ir_register += 1
        
        else:
            expr_type, expr_cte_value, expr_ir_register = self.visit(ctx.expression())
            llvm_expr_type = llvm_type(expr_type)
            llvm_tyype = llvm_type(tyype)
            if expr_type == Type.VOID:
                err("ERROR: trying to assign void expression to variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)
            elif expr_type == Type.FLOAT and tyype == Type.INT:
                err("WARNING: possible loss of information assigning float expression to int variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")

            if op == '=':
                cte_value = expr_cte_value
            if cte_value != None:
                

                if op == '+=':
                    cte_value += expr_cte_value
                    
                    if (tyype == Type.FLOAT):
                        llvm_op = "fadd"
                    else:
                        llvm_op = "add"

                elif op == '-=':
                    cte_value -= expr_cte_value

                    if (tyype == Type.FLOAT):
                        llvm_op = "fsub"
                    else:
                        llvm_op = "sub"

                elif op == '*=':
                    cte_value *= expr_cte_value

                    if (tyype == Type.FLOAT):
                        llvm_op = "fmul"
                    else:
                        llvm_op = "mul"

                elif op == '/=':
                    cte_value /= expr_cte_value

                    if (tyype == Type.INT):
                        llvm_op = "sdiv"
                    elif (tyype == Type.FLOAT):
                        llvm_op = "fdiv"
                    else:
                        llvm_op = "udiv"

                expr_cte_value_str = str(expr_cte_value)
                if (tyype == Type.FLOAT):
                    expr_cte_value_str = float_to_hex(float(expr_cte_value))

                if op != '=':

                    printLoad(self.next_ir_register, tyype, name, tyype, 4, is_inside)
                    self.next_ir_register += 1
                    printOper(llvm_op, self.next_ir_register, llvm_tyype, self.next_ir_register - 1, expr_cte_value, is_inside, False, True)
                    
                    printStore(self.next_ir_register, llvm_expr_type, name, llvm_tyype, 4, is_inside, False)
                    self.next_ir_register += 1
                else:
                    printStore(expr_cte_value_str, llvm_expr_type, name, llvm_tyype, 4, is_inside, True)
                

        if ctx.identifier() != None:
            self.ids_defined[name] = tyype, -1, cte_value, ir_register
        else: # array
            if array_index_cte != None:
                cte_values_array[array_index_cte] = cte_value
                ir_registers_array[array_index_cte] = ir_register
            self.ids_defined[name] = tyype, array_length, cte_values_array, ir_registers_array

        return


    # Visit a parse tree produced by GrammarParser#expression.
    def visitExpression(self, ctx:GrammarParser.ExpressionContext):
        tyype = Type.VOID
        llvm_tyype = llvm_type(tyype)
        cte_value = None
        ir_register = None

        if len(ctx.expression()) == 0:

            if ctx.integer() != None:
                tyype = Type.INT
                cte_value = int(ctx.integer().getText())

            elif ctx.floating() != None:
                tyype = Type.FLOAT
                cte_value = float(ctx.floating().getText())

            elif ctx.string() != None:
                tyype = Type.STRING

            elif ctx.identifier() != None:
                name = ctx.identifier().getText()
                try:
                    tyype, _, cte_value, ir_register = self.ids_defined[name]
                except:
                    token = ctx.identifier().IDENTIFIER().getPayload()
                    err("ERROR: undefined variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)

            elif ctx.array() != None:
                name = ctx.array().identifier().getText()
                try:
                    tyype, array_length, cte_values_array, ir_registers_array = self.ids_defined[name]
                except:
                    token = ctx.array().identifier().IDENTIFIER().getPayload()
                    err("ERROR: undefined array '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)

                array_index_cte, array_index_ir = self.visit(ctx.array())
                if array_index_cte != None:
                    if array_index_cte < 0 or array_index_cte >= array_length:
                        err("ERROR:  array '" + name + "' index out of bounds in line " + str(token.line) + " and column " + str(token.column) + "\n")
                        exit(-1)
                    else:
                        cte_value = cte_values_array[array_index_cte]
                        ir_register = ir_registers_array[array_index_cte]

            elif ctx.function_call() != None:
                tyype, cte_value, ir_register = self.visit(ctx.function_call())

        elif len(ctx.expression()) == 1:

            if ctx.OP != None: #unary operators
                text = ctx.OP.text
                token = ctx.OP
                tyype, cte_value, ir_register = self.visit(ctx.expression(0))
                if tyype == Type.VOID:
                    err("ERROR: unary operator '" + text + "' used on type void in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif cte_value != None:
                    if text == '-':
                        cte_value = -cte_value

            else: # parentheses
                tyype, cte_value, ir_register = self.visit(ctx.expression(0))


        elif len(ctx.expression()) == 2: # binary operators
            text = ctx.OP.text
            token = ctx.OP
            left_type, left_cte_value, left_ir_register = self.visit(ctx.expression(0))
            right_type, right_cte_value, right_ir_register = self.visit(ctx.expression(1))
            if left_type == Type.VOID or right_type == Type.VOID:
                err("ERROR: binary operator '" + text + "' used on type void in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)

            if text == '*' or text == '/' or text == '+' or text == '-':
                if left_type == Type.FLOAT or right_type == Type.FLOAT:
                    tyype = Type.FLOAT
                else:
                    tyype = Type.INT

                if left_cte_value != None and right_cte_value != None:
                    if text == '*':
                        cte_value = left_cte_value * right_cte_value
                    elif text == '/':
                        cte_value = left_cte_value / right_cte_value
                    elif text == '+':
                        cte_value = left_cte_value + right_cte_value
                    elif text == '-':
                        cte_value = left_cte_value - right_cte_value
                else:
                    cte_value = None
            else:
                tyype = Type.INT
                if left_cte_value != None and right_cte_value != None:
                    if text == '<':
                        if left_cte_value < right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '>':
                        if left_cte_value > right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '==':
                        if left_cte_value == right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '!=':
                        if left_cte_value != right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '<=':
                        if left_cte_value <= right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '>=':
                        if left_cte_value >= right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                else:
                    cte_value = None

        return tyype, cte_value, ir_register


    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):
        tyype, cte_value, ir_register = self.visit(ctx.expression())
        if tyype != Type.INT:
            token = ctx.identifier().IDENTIFIER().getPayload()
            err("ERROR: array expression must be an integer, but it is " + str(tyype) + " in line " + str(token.line) + " and column " + str(token.column) + "\n")
            exit(-1)
        return cte_value, ir_register


    # Visit a parse tree produced by GrammarParser#array_literal.
    def visitArray_literal(self, ctx:GrammarParser.Array_literalContext):
        types_array = []
        cte_values_array = []
        ir_registers_array = []
        for i in range(len(ctx.expression())):
            tyype, cte_value, ir_register = self.visit(ctx.expression(i))
            types_array += [tyype]
            cte_values_array += [cte_value]
            ir_registers_array += [ir_register]
        return types_array, cte_values_array, ir_registers_array


    # Visit a parse tree produced by GrammarParser#function_call.
    def visitFunction_call(self, ctx:GrammarParser.Function_callContext):
        name = ctx.identifier().getText()
        token = ctx.identifier().IDENTIFIER().getPayload()
        try:
            tyype, args, cte_value, ir_register = self.ids_defined[name]
            if len(args) != len(ctx.expression()):
                err("ERROR: incorrect number of parameters for function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + ". Expecting " + str(len(args)) + ", but " + str(len(ctx.expression())) + " were given" + "\n")
                exit(-1)
        except:
            err("ERROR: undefined function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
            exit(-1)

        for i in range(len(ctx.expression())):
            arg_type, arg_cte_value, arg_ir_register = self.visit(ctx.expression(i))
            if i < len(args):
                if arg_type == Type.VOID:
                    err("ERROR: void expression passed as parameter " + str(i) + " of function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif arg_type == Type.FLOAT and args[i] == Type.INT:
                    err("WARNING: possible loss of information converting float expression to int expression in parameter " + str(i) + " of function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
        return tyype, cte_value, ir_register


    # Visit a parse tree produced by GrammarParser#arguments.
    def visitArguments(self, ctx:GrammarParser.ArgumentsContext):
        params = []
        cte_value = None
        for i in range(len(ctx.identifier())):
            tyype = ctx.tyype(i).getText()
            name = ctx.identifier(i).getText()
            ir_register = i
            self.ids_defined[name] = tyype, -1, cte_value, ir_register
            params += [name]
        return params


    # Visit a parse tree produced by GrammarParser#tyype.
    def visitTyype(self, ctx:GrammarParser.TyypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#integer.
    def visitInteger(self, ctx:GrammarParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#floating.
    def visitFloating(self, ctx:GrammarParser.FloatingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#string.
    def visitString(self, ctx:GrammarParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#identifier.
    def visitIdentifier(self, ctx:GrammarParser.IdentifierContext):
        return self.visitChildren(ctx)


# warning: the use of uninitialized variables is not being warned!