# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GrammarParser import GrammarParser
else:
    from GrammarParser import GrammarParser

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

# This class defines a complete generic visitor for a parse tree produced by GrammarParser.
class GrammarCheckerVisitor(ParseTreeVisitor):
    ids_defined = {} # armazenar informações necessárias para cada identifier definido
    inside_what_function = ""
    connected_to_condition = [] #conecta as variaveis que podem deixar de serem constante nos elses e fors
    #normal = (tyype, array_length = -1, valor, éConstante?)
    #array = (tyype, array_length, [0:array_length] de (valor, éConstante?))

    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx:GrammarParser.FiileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx:GrammarParser.Function_definitionContext):
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()
        params = self.visit(ctx.arguments())
        self.ids_defined[name] = tyype, params
        self.inside_what_function = name

        

        self.visit(ctx.body())


        return


    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx:GrammarParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx:GrammarParser.StatementContext):
        value = None
        if ctx.RETURN() != None:
            token = ctx.RETURN().getPayload()
            tyype, value, is_constant = self.visit(ctx.expression())
            function_type, params = self.ids_defined[self.inside_what_function]
            if function_type == Type.INT and tyype == Type.FLOAT:
                print("WARNING: possible loss of information returning float expression from int function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column))
            elif function_type == Type.VOID and tyype != Type.VOID:
                print("ERROR: trying to return a non void expression from void function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column))
            elif function_type != Type.VOID and tyype == Type.VOID:
                print("ERROR: trying to return void expression from function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column))

        else:
            self.visitChildren(ctx)
        return 


    # Visit a parse tree produced by GrammarParser#if_statement.
    def visitIf_statement(self, ctx:GrammarParser.If_statementContext):
        #primeiro visito a expressao
        self.visit(ctx.expression())
        #empilho com os names das vars que podem deixar de serem constantes dentro desse if
        self.connected_to_condition.append([key for key, value in self.ids_defined.items()])
        
        #checo o corpo do if
        if ctx.body() != None:
            self.visit(ctx.body())
        elif ctx.statement() != None:
            self.visit(ctx.statement())
        
        if ctx.else_statement() != None:
            self.visit(ctx.else_statement())
        
        #desempilho as variaveis que seriam colapsadas por esse if
        self.connected_to_condition.pop()
        


    # Visit a parse tree produced by GrammarParser#else_statement.
    def visitElse_statement(self, ctx:GrammarParser.Else_statementContext):
        return self.visitChildren(ctx)
        

    # Visit a parse tree produced by GrammarParser#for_loop.
    def visitFor_loop(self, ctx:GrammarParser.For_loopContext):
        #visito o inicialiador
        self.visit(ctx.for_initializer())

        #empilho com os names das vars que podem deixar de serem constantes dentro desse for
        old_keys = [key for key, value in self.ids_defined.items()]
        self.connected_to_condition.append(old_keys)

        #visito as partes do for
        self.visit(ctx.for_step())

        self.visit(ctx.for_condition())

        if ctx.body() != None:
            self.visit(ctx.body())
        elif ctx.statement() != None:
            self.visit(ctx.statement())        

        self.connected_to_condition.pop()
        #return self.visitChildren(ctx)


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

        for i in range(len(ctx.identifier())):
            name = ctx.identifier(i).getText()
            token = ctx.identifier(i).IDENTIFIER().getPayload()

            if ctx.expression(i) != None:
                #print(ctx.expression(i).getText())
                expr_type, expr_value, expr_is_constant = self.visit(ctx.expression(i))
                if expr_type == Type.VOID or expr_type == Type.STRING:
                    print("ERROR: trying to assign '" + expr_type + "' expression to variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
                elif expr_type == Type.FLOAT and tyype == Type.INT:
                    print("WARNING: possible loss of information assigning float expression to int variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column))

                #se ele nao estiver em nenhuma função a variavel nao é constante 
                if self.inside_what_function == "":
                    expr_is_constant = False
                self.ids_defined[name] = tyype, -1, expr_value, expr_is_constant
            else:
                self.ids_defined[name] = tyype, -1, None, None # -1 means not a array, therefore no length here (vide 15 lines below)

        for i in range(len(ctx.array())):
            name = ctx.array(i).identifier().getText()
            token = ctx.array(i).identifier().IDENTIFIER().getPayload()
            expr_eltos = []

            array_length = self.visit(ctx.array(i))

            if ctx.array_literal(i) != None:
                expr_eltos = self.visit(ctx.array_literal(i))
                for j in range(len(expr_eltos)):
                    if expr_eltos[j] == Type.VOID  or expr_eltos[j] == Type.STRING:
                        print("ERROR: trying to initialize '" + expr_eltos[j] + "' expression to '" + tyype + "' array '" + name + "' at index " + str(j) + " of array literal in line " + str(token.line) + " and column " + str(token.column))
                    elif expr_eltos[j] == Type.FLOAT and tyype == Type.INT:
                        print("WARNING: possible loss of information initializing float expression to int array '" + name + "' at index " + str(j) + " of array literal in line " + str(token.line) + " and column " + str(token.column))
            else:
                for i in range(array_length):
                    expr_eltos.append(('',None,True))
            

            self.ids_defined[name] = tyype, array_length, expr_eltos
            #print(self.ids_defined[name])
        #print(self.ids_defined)
        return


    # Visit a parse tree produced by GrammarParser#variable_assignment.
    def visitVariable_assignment(self, ctx:GrammarParser.Variable_assignmentContext):
        op = ctx.OP.text
        name = None
        tyype = None
        value = None
        is_constant = None
        array_index = None
        
        params = []
        #vamos pegar os parametros da funcao, que foram declarados nos argumentos
        if self.inside_what_function != "":
            function_type, params = self.ids_defined.get( self.inside_what_function)

        if ctx.identifier() != None:
            name = ctx.identifier().getText()
            token = ctx.identifier().IDENTIFIER().getPayload()

            try:
                #checando no ids_defined
                tyype, _, value, is_constant = self.ids_defined[name]
                
            except:
                try:
                    #se nao tiver no ids_defined é pra ta nos parametros ne
                    tyype = params[name]
                    
                    is_constant = False    
                except:
                    print("ERROR: undefined variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
                    return


        else:#array
            #print(ctx.getText())
            name = ctx.array().identifier().getText()
            token = ctx.array().identifier().IDENTIFIER().getPayload()
            #print(self.ids_defined[name])
            try:
                tyype, array_length, values = self.ids_defined[name]
            except:
                print("ERROR: undefined array '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
                return
            array_index = self.visit(ctx.array())
            if array_index < 0 or array_index >= array_length:
                print("ERROR: array '" + name + "' index out of range in line " + str(token.line) + " and column " + str(token.column))
                return
            _, value, is_constant = values[array_index]


        if ctx.expression() != None:
            expr_type, expr_value, expr_is_constant = self.visit(ctx.expression())
            #print(expr_is_constant)
            #aqui é como se a gente visse a pilha dos ifs e pegava os nomes das variaveis que podem deixar de ser constantes ao serem usadas detro de uma condicao
            prior_variables = []
            try:
                prior_variables = self.connected_to_condition[-1]
            except:
                prior_variables = []

            #se tiver, xau xau constante

            if name in prior_variables:
                expr_value = None
                expr_is_constant = False

            if ctx.identifier() != None:
                if not is_constant or not expr_is_constant:
                    self.ids_defined[name] = tyype, -1, None, False
                else:
                    if op == '/=':
                        expr_value = value / expr_value
                    elif op == '*=':
                        expr_value = value * expr_value
                    elif op == '+=':
                        expr_value = value + expr_value
                    elif op == '-=':
                        expr_value = value - expr_value
                    
                    self.ids_defined[name] = tyype, -1, expr_value, expr_is_constant

            else: # array
                if not is_constant or not expr_is_constant:
                    values[array_index] = tyype, None, False
                else:
                    if op == '/=':
                        expr_value = value / expr_value
                    elif op == '*=':
                        expr_value = value * expr_value
                    elif op == '+=':
                        expr_value = value + expr_value
                    elif op == '-=':
                        expr_value = value - expr_value
                    
                    values[array_index] = tyype, expr_value, expr_is_constant
                
                #print(self.ids_defined[name])
                self.ids_defined[name] = tyype, array_length, values
                #print(self.ids_defined[name])

            if expr_type == Type.VOID or expr_type == Type.STRING:
                print("ERROR: trying to assign '" + expr_type + "' expression to variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
            elif expr_type == Type.FLOAT and tyype == Type.INT:
                print("WARNING: possible loss of information assigning float expression to int variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column))

        else:
            #aqui é a mesma coisa so que pra var++ e var-- 
            prior_variables = []
            try:
                prior_variables = self.connected_to_condition[-1]
            except:
                prior_variables = []
                #print("nothing in prior")
            
            if name in prior_variables:
                value = None
                is_constant = False
                

            if ctx.identifier() != None:
                if not is_constant:
                    self.ids_defined[name] = tyype, -1, None, False
                else:
                    if op == '++':
                        value += 1
                    elif op == '--':
                        value -= 1
                
                    self.ids_defined[name] = tyype, -1, value, is_constant

            else: # array
                if not is_constant:
                    values[array_index] = tyype, None, False
                else:
                    if op == '++':
                        value += 1
                    elif op == '--':
                        value -= 1

                    values[array_index] = tyype, value, is_constant

                self.ids_defined[name] = tyype, array_length, values
        return


    # Visit a parse tree produced by GrammarParser#expression.
    def visitExpression(self, ctx:GrammarParser.ExpressionContext):
        tyype = Type.VOID
        value = None
        is_constant = True
        function_type = None
        params = []
        #pegamos os paramentros pra checar se a variavel foi declarada nos args
        if self.inside_what_function != "":
            function_type, params = self.ids_defined.get( self.inside_what_function)
        # print(params)
        if len(ctx.expression()) == 0:

            if ctx.integer() != None:
                tyype = Type.INT
                value = int(ctx.integer().getText())

            elif ctx.floating() != None:
                tyype = Type.FLOAT
                value = float(ctx.floating().getText())

            elif ctx.string() != None:
                tyype = Type.STRING
                value = ctx.string().getText()

            elif ctx.identifier() != None:
                name = ctx.identifier().getText()
                try:
                    tyype, _, value, is_constant = self.ids_defined[name]

                except:
                    try:
                        #se n tiver no ids_defined é pra estar nos parametros né
                        tyype = params[name]
                        
                        is_constant = False
                    except:
                        token = ctx.identifier().IDENTIFIER().getPayload()
                        print("ERROR: undefined variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column))

            elif ctx.array() != None:
                name = ctx.array().identifier().getText()
                tyype, array_length = None, None
                try:
                    tyype, array_length, array_values = self.ids_defined[name]
                except:
                    token = ctx.array().identifier().IDENTIFIER().getPayload()
                    print("ERROR: undefined array '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
                array_index = self.visit(ctx.array())
                
                if array_index < 0 or array_index >= array_length:
                    print("ERROR:  array '" + name + "' index out of bounds in line " + str(token.line) + " and column " + str(token.column))
                else:
                    tyype, value, is_constant = array_values[array_index]
                #print("array index = " + str(array_index))

            elif ctx.function_call() != None:
                tyype = self.visit(ctx.function_call())

        elif len(ctx.expression()) == 1:

            if ctx.OP != None: #unary operators
                text = ctx.OP.text
                token = ctx.OP
                tyype, old_value, is_constant = self.visit(ctx.expression(0))

                #se ja nao for constante é xau xau
                if is_constant == False:
                    return tyype, None, False

                if text == '-':
                    value = -old_value
                else:
                    value = old_value
                print("line {} Expression {} {} simplified to: {}".format(str(token.line), str(text), str(old_value), str(value)))

                if tyype == Type.VOID:
                    print("ERROR: unary operator '" + text + "' used on type void in line " + str(token.line) + " and column " + str(token.column))

            else: # parentheses
                tyype, value, is_constant = self.visit(ctx.expression(0))


        elif len(ctx.expression()) == 2: # binary operators
            text = ctx.OP.text
            token = ctx.OP

            left_tyype, left_value, left_constant = self.visit(ctx.expression(0))
            right_tyype, right_value, right_constant = self.visit(ctx.expression(1))

            is_constant = left_constant and right_constant


            if left_tyype == Type.VOID or right_tyype == Type.VOID:
                print("ERROR: binary operator '" + text + "' used on type void in line " + str(token.line) + " and column " + str(token.column))

            if text == '*' or text == '/' or text == '+' or text == '-':
                if left_tyype == Type.FLOAT or right_tyype == Type.FLOAT:
                    tyype = Type.FLOAT
                else:
                    tyype = Type.INT
                # print("my type = ", tyype)
                # print(left_value, text, right_value)
                # print(ctx.getText())

            else:
                tyype = Type.INT

            #se ja nao for constante é xau xau não é pra nem se dar o trabalho
            if left_value == None or right_value == None:
                return tyype, None, False

            if text == '*':
                value = left_value * right_value
            elif text == '/':
                value = left_value / right_value
            elif text == '+':
                value = left_value + right_value
            elif text == '-':
                value = left_value - right_value
            elif text == '<':
                value = int(left_value < right_value)
            elif text == '<=':
                value = int(left_value <= right_value)
            elif text == '>':
                value = int(left_value > right_value)
            elif text == '>=':
                value = int(left_value >= right_value)
            elif text == '==':
                value = int(left_value == right_value)
            elif text == '!=':
                value = int(left_value != right_value)
            # print("final value = ", value)

            if is_constant:
                print("line {} Expression {} {} {} simplified to: {}".format(str(token.line), str(left_value), str(text), str(right_value), str(value)))

            
                
        # print("final final value = ", value)
        return tyype, value, is_constant


    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):
        tyype, length, _ = self.visit(ctx.expression())
        

        if tyype != Type.INT:
            token = ctx.identifier().IDENTIFIER().getPayload()
            print("ERROR: array expression must be an integer, but it is " + str(tyype) + " in line " + str(token.line) + " and column " + str(token.column))
        
        return length


    # Visit a parse tree produced by GrammarParser#array_literal.
    def visitArray_literal(self, ctx:GrammarParser.Array_literalContext):
        eltos = []
        for i in range(len(ctx.expression())):
            tyype, value, is_constant = self.visit(ctx.expression(i))
            eltos += [(tyype, value, is_constant)]
        return eltos


    # Visit a parse tree produced by GrammarParser#function_call.
    def visitFunction_call(self, ctx:GrammarParser.Function_callContext):
        name = ctx.identifier().getText()
        token = ctx.identifier().IDENTIFIER().getPayload()
        try:
            tyype, args = self.ids_defined[name]
            if len(args) != len(ctx.expression()):
                #for i in range(len(ctx.expression())):
                #    print(ctx.expression(i).getText())
                print("ERROR: incorrect number of parameters for function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + ". Expecting " + str(len(args)) + ", but " + str(len(ctx.expression())) + " were given")
        except:
            print("ERROR: undefined function '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
        
        #esse iter é pra ficar pegando os itens do args como se fosse uma list
        par_iter = iter(args)
        for i in range(len(ctx.expression())):
            arg_type = self.visit(ctx.expression(i))
            if i < len(args):
                if arg_type == Type.VOID:
                    print("ERROR: void expression passed as parameter " + str(i) + " of function '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
                elif arg_type == Type.FLOAT and next(par_iter) == Type.INT:
                    print("WARNING: possible loss of information converting float expression to int expression in parameter " + str(i) + " of function '" + name + "' in line " + str(token.line) + " and column " + str(token.column))
        return tyype


    # Visit a parse tree produced by GrammarParser#arguments.
    def visitArguments(self, ctx:GrammarParser.ArgumentsContext):
        #alterei para os args deixarem de serem salvos no ids_defined e serem salvos na function
        params = {}
        for i in range(len(ctx.identifier())):
            tyype = ctx.tyype(i).getText()
            name = ctx.identifier(i).getText()
            #self.ids_defined[name] = tyype, -1, None, False
            params[name] = tyype
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


    #del GrammarParser

    #def aggregateResult(self, aggregate:Type, next_result:Type):
        #return next_result if next_result != None else aggregate
