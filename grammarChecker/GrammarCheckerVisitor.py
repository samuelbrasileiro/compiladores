# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
from typing import OrderedDict
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GrammarParser import GrammarParser
else:
    from GrammarParser import GrammarParser

# This class defines a complete generic visitor for a parse tree produced by GrammarParser.

'''
COMO RESGATAR INFORMAÇÕES DA ÁRVORE

Observe o seu Grammar.g4. Cada regra sintática gera uma função com o nome corespondente no Visitor e na ordem em que está na gramática.

Se for utilizar sua gramática do projeto 1, por causa de conflitos com Python, substitua as regras file por fiile e type por tyype. Use prints temporários para ver se está no caminho certo.
"make tree" agora desenha a árvore sintática, se quiser vê-la para qualquer input, enquanto "make" roda este visitor sobre o a árvore gerada a partir de Grammar.g4 alimentada pelo input.

Exemplos:

# Obs.: Os exemplos abaixo utilizam nós 'expression', mas servem apra qualquer tipo de nó

self.visitChildren(ctx) # visita todos os filhos do nó atual
# visita a subárvore do nó expression e retorna o valor retornado na função "visitRegra"
expr = self.visit(ctx.expression())

# para cada expressão que este nó possui...
for i in range(len(ctx.expression())):
    ident = ctx.expression(i) # ...pegue a i-ésima expressão


if ctx.FLOAT() != None: # se houver um FLOAT (em vez de INT ou VOID) neste nó (parser)
    return Type.FLOAT # retorne tipo float

# Obtém o texto contido no nó (neste caso, será obtido o nome do identifier)
ctx.identifier().getText()

# Obtém o token referente à uma determinada regra léxica (neste caso, IDENTIFIER)
token = ctx.identifier(i).IDENTIFIER().getPayload()
token.line      # variável com a linha do token
token.column    # variável com a coluna do token
'''


# Dica: Retorne Type.INT, Type.FLOAT, etc. Nos nós e subnós das expressões para fazer a checagem de tipos enquanto percorre a expressão.
class Type:
    VOID = "void"
    INT = "int"
    FLOAT = "float"
    STRING = "char *"


class GrammarCheckerVisitor(ParseTreeVisitor):
    # Dicionário para armazenar as informações necessárias para cada identifier definido
    ids_defined = {}
    # String que guarda a função atual que o visitor está visitando. Útil para acessar dados da função durante a visitação da árvore sintática da função.
    inside_what_function = ""

    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx: GrammarParser.FiileContext):
        return self.visitChildren(ctx)

     # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx: GrammarParser.Function_definitionContext):
        token = ctx.identifier().IDENTIFIER().getPayload()
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()

        params = self.visit(ctx.arguments())

        self.ids_defined[name] = tyype, params, token.line

        self.inside_what_function = name
        self.visit(ctx.body())
        return

    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx: GrammarParser.BodyContext):

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx: GrammarParser.StatementContext):

        funcType = self.ids_defined[self.inside_what_function][0]

        if(ctx.RETURN()):
            token = ctx.RETURN().getPayload()

            if funcType == 'void':
                if ctx.expression() != None:
                    print("ERROR: unexpected non-void return value in void function '{}' in line {} and column {}".format(
                        self.inside_what_function, str(token.line), str(token.column)))
                    
            else:
                if ctx.expression() == None:
                    print("ERROR: unexpected void return value (expected {}) in function '{}' in line {} and column {}".format(
                        funcType, self.inside_what_function, token.line, token.column))
                    

                else:
                    returnType = self.visit(ctx.expression())
                    #print("return: "+returnType)
                    token = ctx.RETURN().getPayload()
                    if returnType != funcType:
                        if returnType == Type.FLOAT and funcType == Type.INT:
                            print("WARNING: possible loss of information returning 'float' expression from 'int' function '{}' in line {} and column {}".format(self.inside_what_function, token.line, token.column))
                        elif not (funcType == Type.FLOAT and returnType == Type.INT):
                            print("ERROR: wrong return type in function '{}' (given {}, expected {}) in line {} and column {}".format(
                            self.inside_what_function, returnType, funcType, token.line, token.column))
                        return None
        
        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#if_statement.
    def visitIf_statement(self, ctx: GrammarParser.If_statementContext):

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#else_statement.
    def visitElse_statement(self, ctx: GrammarParser.Else_statementContext):

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#for_loop.
    def visitFor_loop(self, ctx: GrammarParser.For_loopContext):

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#for_initializer.
    def visitFor_initializer(self, ctx: GrammarParser.For_initializerContext):

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#for_condition.
    def visitFor_condition(self, ctx: GrammarParser.For_conditionContext):

        return self.visitChildren(ctx)

    # Visit a parse tree produced by GrammarParser#for_step.
    def visitFor_step(self, ctx: GrammarParser.For_stepContext):

        return self.visitChildren(ctx)

    '''
    variable_definition
        : tyype (identifier ('=' expression)? | array ('=' array_literal)? )
                (',' (identifier ('=' expression)? |  array ('=' array_literal)) )*
        ;
    '''
    # Visit a parse tree produced by GrammarParser#variable_definition.

    def visitVariable_definition(self, ctx: GrammarParser.Variable_definitionContext):
        tyype = ctx.tyype().getText()

        #attVarList serve para associar os valores que tem =
        attVarlist = []
        children = list(ctx.getChildren())
        
        for index in range(len(children)):
            if children[index].getText() == "=":
                attVarlist.append(
                    (children[index - 1], children[index + 1]))

        #checando os arrays
        for i in range(len(ctx.array())):
            array = ctx.array(i)
            arrayID = array.identifier().getText()
            token = array.identifier().IDENTIFIER().getPayload()
            
            self.ids_defined[arrayID] = tyype, None
            for attVar in attVarlist:
                self.visit(attVar[0])
                numberOfEltos = len(attVar[1].expression())
                index = self.ids_defined[arrayID][1]
                if index != None:
                    if numberOfEltos != index:
                        print("ERROR: incorret number of expressions assigned to array {} (given {}, expected {}) in line {} and column {}".format(arrayID, numberOfEltos, index, token.line, token.column))
                for i in range(numberOfEltos):
                    expr = attVar[1].expression(i)
                    exprType = self.visit(expr)
                    if exprType != tyype:
                        if exprType == Type.FLOAT and tyype == Type.INT:
                            print("WARNING: possible loss of information initializing 'float' expression to 'int' array '{}' at index {} of array literal in line {} and column {}".format(arrayID, i, token.line, token.column))
                        elif not (tyype == Type.FLOAT and exprType == Type.INT):
                            print("ERROR: trying to initialize '{}' expression to '{}' array '{}' at index {} of array literal in line {} and column {}".format(exprType, tyype, arrayID, i, token.line, token.column))

        #checando os normais
        for i in range(len(ctx.identifier())):
            name = ctx.identifier(i).getText()
            token = ctx.identifier(i).IDENTIFIER().getPayload()
            self.ids_defined[name] = ((tyype, token))
        
            for attVar in attVarlist:
                
                if attVar[0].getText() == name:
                    expr = attVar[1]
                    tyype_expression = self.visitExpression(expr)
                    tyype_variable = tyype

                    #print('expression value: ', expr.getText())
                    #print('expression type: ', tyype_expression)
                    
                    if tyype_expression == None:
                        break

                    if tyype_variable == Type.INT and tyype_expression == Type.FLOAT:
                        print("WARNING: possible loss of information assigning float expression to int variable '{}' in line {} and column {}".format(
                            str(name), str(token.line), str(token.column)))
                    elif (tyype_variable != tyype_expression) and not (tyype_variable == Type.FLOAT and tyype_expression == Type.INT):
                        print("ERROR: trying to assign '{}' expression to variable '{}' in line {} and column {}".format(
                            tyype_expression, name, str(token.line), str(token.column)))
                    # elif(tyype_expression == Type.VOID):

                    break


    '''
    variable_assignment
	    : (identifier | array) OP=('='|'+='|'-='|'*='|'/=') expression
	    | (identifier | array) OP=('++'|'--')
	    ;
    '''
    # Visit a parse tree produced by GrammarParser#variable_assignment.

    def visitVariable_assignment(self, ctx: GrammarParser.Variable_assignmentContext):
        op = ctx.OP.text
        #print("assignment: "+ ctx.getText())
        tyype_variable = Type.VOID
        
        if ctx.identifier() != None:

            name = ctx.identifier().getText()
            #print(name)
            token = ctx.identifier().IDENTIFIER().getPayload()

            def_identifier = self.ids_defined.get(name)
            
            if def_identifier == None:
                print("ERROR: trying to assign to a non-defined variable '{}' in line {} and column {}".format(
                    name, str(token.line), str(token.column)))

            elif ctx.expression() == None:
                tyype = def_identifier[0]
                if tyype != Type.INT and tyype != Type.FLOAT:
                    print("ERROR: binary operator '{}' used to variable of type '{}' in line {} and column {}".format(
                        op, tyype, str(token.line), str(token.column)))

            else:
                tyype_expression = self.visitExpression(ctx.expression())
                tyype_variable = def_identifier[0]
                if ctx.expression().array() != None:
                    self.visit(ctx.expression().array())

                if tyype_expression == None:
                    return None

                if tyype_variable == Type.INT and tyype_expression == Type.FLOAT:
                    print("WARNING: possible loss of information assigning float expression to int variable '{}' in line {} and column {}".format(
                        str(name), str(token.line), str(token.column)))
                elif tyype_variable == tyype_expression:
                    if tyype_variable != Type.FLOAT and tyype_variable != Type.INT:
                        print("ERROR: binary operator '{}' used to variable of type '{}' in line {} and column {}".format(
                                op, tyype_variable, str(token.line), str(token.column)))
                elif not (tyype_variable == Type.FLOAT and tyype_expression == Type.INT):
                    print("ERROR: trying to assign '{}' expression to variable '{}' in line {} and column {}".format(
                        tyype_expression, name, str(token.line), str(token.column)))
        
    '''
    expression
        : integer
        | floating
        | string
        | function_call
        | identifier
        | array
        | OP=('-'|'+') expression
        | expression OP=('*'|'/') expression
        | expression OP=('+'|'-') expression
        | expression OP=('<'|'>'|'<='|'>='|'=='|'!=') expression
        | '(' expression ')'
        ;
    '''
    # Visit a parse tree produced by GrammarParser#expression.

    def visitExpression(self, ctx: GrammarParser.ExpressionContext):
        # tyype = Type.VOID
        
        #print("expression: "+ctx.getText())
        

        if len(ctx.expression()) == 0:
            if ctx.integer() != None:
                return Type.INT

            elif ctx.string() != None:
                return Type.STRING

            elif ctx.floating() != None:
                return Type.FLOAT

            elif ctx.identifier() != None:
                name = ctx.identifier().getText()
                token = ctx.identifier().IDENTIFIER().getPayload()

                def_variable = self.ids_defined.get(name)

                if def_variable == None:
                    print("ERROR: trying to use a non-defined variable '{}' in expression in line {} and column {}".format(
                        name, str(token.line), str(token.column)))
                    return None

                tyype = def_variable[0]
                return tyype

            elif ctx.array() != None:
                name = ctx.array().identifier().getText()
                tyype = None
                token = ctx.array().identifier().IDENTIFIER().getPayload()
                givenIndex = ctx.array().expression().getText()

                if(self.ids_defined.get(name) == None):
                    print("ERROR: undefined array '{}' in line {} and column {}".format(
                        name, str(token.line), str(token.column)))
                    if givenIndex != None:
                        print("ERROR: array '{}' index out of bounds in line {} and column {}".format(name, token.line, token.column))                     

                if(self.ids_defined.get(name) != None):
                    tyype = self.ids_defined[name][0]
                    indexType = self.visit(ctx.array().expression())
                    if (indexType != Type.INT) or (int(givenIndex) >= self.ids_defined.get(name)[1]):
                        print(tyype)
                        print("ERROR: array '{}' index out of bounds in line {} and column {}".format(name, token.line, token.column))
                    
                return tyype
                
            elif ctx.function_call() != None:
                return self.visit(ctx.function_call())

        elif len(ctx.expression()) == 1:
            if ctx.OP == None:
                # caso do parenteses
                return self.visitExpression(ctx.expression(0))
            op = ctx.OP.text
            token = ctx.OP.getTokenSource()
            tyype = self.visitExpression(ctx.expression(0))
            if tyype == None:
                return None

            if tyype == Type.INT or tyype == Type.FLOAT:
                return tyype
            elif tyype == Type.VOID:
                return("ERROR: trying to use '{}' operator in variable of type void, in line {} and column {}".format(op,
                    str(token.line), str(token.column)))
            else:
                print("ERROR: trying to use '{}' operator in variable of type '{}', in line {} and column {}".format(
                        op, tyype, str(token.line), str(token.column)))
                return None
        elif len(ctx.expression()) == 2:
            token = ctx.OP.getTokenSource()
            op = ctx.OP.text
            tyype1 = self.visitExpression(ctx.expression(0))
            tyype2 = self.visitExpression(ctx.expression(1))

            if tyype1 == None or tyype2 == None:
                return None

            if (tyype1 == Type.FLOAT or tyype1 == Type.INT) and (tyype2 == Type.FLOAT or tyype2 == Type.INT):
                if tyype1 == tyype2:
                    return tyype1
                else:
                    return Type.FLOAT
            else:
                print("ERROR: trying to use '{}' operator between variables of types '{}' and '{}', in line {} and column {}".format(
                        op, tyype1, tyype2, str(token.line), str(token.column)))
                return None
        
        return Type.VOID


    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):

        expType = self.visit(ctx.expression())
        
        if expType != Type.INT:
            token = ctx.identifier().IDENTIFIER().getPayload()
            print("ERROR: array expession must be of type int (given {}) in line {} and column {}".format(expType, token.line, token.column))
            return 0
        else:
            arrayID = ctx.identifier().getText()
            self.ids_defined[arrayID] = self.ids_defined[arrayID][0], int(ctx.expression().getText())
            return ctx.expression()


    # Visit a parse tree produced by GrammarParser#array_literal.
    def visitArray_literal(self, ctx:GrammarParser.Array_literalContext):

        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#function_call.
    def visitFunction_call(self, ctx:GrammarParser.Function_callContext):
    
        functionName = ctx.identifier().getText()

        token = ctx.identifier().IDENTIFIER().getPayload()
        passedArgs = len(ctx.expression())
        funcType = ""

        if self.ids_defined.get(functionName) != None:
            funcType = self.ids_defined[functionName][0]

            funcArgs = self.ids_defined[functionName][1]

            if passedArgs != len(funcArgs):
                print("ERROR: wrong number of arguments for function {} (given {}, expected {}) in line {} column {}".format(functionName, passedArgs, len(funcArgs), token.line, token.column))

            else:
                for i in range(passedArgs):
                    expType = self.visitExpression(ctx.expression(i))
                    argType = funcArgs[i][1]

                    if argType == expType:
                        continue
                    else:

                        if argType == Type.INT and expType == Type.FLOAT:
                            print("WARNING: possible loss of information converting float expression to int expression in parameter {} of function '{}' in line {} and column {}".format(
                                    i, str(functionName), str(token.line), str(token.column)))
                        elif not (argType == Type.FLOAT and expType == Type.INT):
                            print("ERROR: wrong type of arguments (expected {}, passed {}) in line {} and column {}".format(argType, expType, token.line, token.column))
                        
        else:
            print("ERROR: trying to call a non-defined function {} in line {} and column {}".format(functionName, token.line, token.column)) 

        return funcType


    # Visit a parse tree produced by GrammarParser#arguments.
    def visitArguments(self, ctx:GrammarParser.ArgumentsContext):

        numberOfArgs = len(ctx.identifier())
        args = []
        for i in range(numberOfArgs):
            identifier = ctx.identifier(i).getText()
            tyype = ctx.tyype(i).getText()
            self.ids_defined[identifier] = tyype, None
            args.append((identifier, tyype))

        return args


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

