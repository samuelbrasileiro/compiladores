# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
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
expr = self.visit(ctx.expression())  # visita a subárvore do nó expression e retorna o valor retornado na função "visitRegra"

for i in range(len(ctx.expression())): # para cada expressão que este nó possui...
    ident = ctx.expression(i) # ...pegue a i-ésima expressão


if ctx.FLOAT() != None: # se houver um FLOAT (em vez de INT ou VOID) neste nó (parser)
    return Type.FLOAT # retorne tipo float

ctx.identifier().getText()  # Obtém o texto contido no nó (neste caso, será obtido o nome do identifier)

token = ctx.identifier(i).IDENTIFIER().getPayload() # Obtém o token referente à uma determinada regra léxica (neste caso, IDENTIFIER)
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
    ids_defined = {} # Dicionário para armazenar as informações necessárias para cada identifier definido
    inside_what_function = "" # String que guarda a função atual que o visitor está visitando. Útil para acessar dados da função durante a visitação da árvore sintática da função.

    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx:GrammarParser.FiileContext):
        return self.visitChildren(ctx)


     # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx:GrammarParser.Function_definitionContext):
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()
        params = self.visit(ctx.arguments())
        self.ids_defined[name] = tyype, params, None
        self.inside_what_function = name
        self.visit(ctx.body())
        return


    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx:GrammarParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx:GrammarParser.StatementContext):


        return self.visitChildren(ctx)


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


    '''
    variable_definition
        : tyype (identifier ('=' expression)? | array ('=' array_literal)? ) 
                (',' (identifier ('=' expression)? |  array ('=' array_literal)) )*
        ;
    '''
    # Visit a parse tree produced by GrammarParser#variable_definition.
    def visitVariable_definition(self, ctx:GrammarParser.Variable_definitionContext):
        # aqui vamos salvar as novas ids no prog

        tyype = ctx.tyype().getText()

        attVarlist = []
        children = list(ctx.getChildren())
        
        for index in range(len(children)):
            if children[index].getText() == "=":
                attVarlist.append((children[index - 1].getText(), children[index + 1]))

        
        for i in range(len(ctx.identifier())):
            
            name = ctx.identifier(i).getText()
            token = ctx.identifier(i).IDENTIFIER().getPayload()

            self.ids_defined[name] = ((tyype, token))

            print('variable: ', name)
            print('type: ', tyype)

            for attVar in attVarlist:
                if attVar[0] == name:
                    expr = attVar[1]
                    tyype_expression = self.visitExpression(expr)
                    tyype_variable = tyype

                    print('expression value: ', expr.getText())
                    print('expression type: ', tyype_expression)
                    
                    if tyype_variable == Type.INT and tyype_expression == Type.FLOAT:
                        print("WARNING: Possible loss of information assigning float expression to int variable '{}' in line {} and column {}".format(str(name), str(token.line), str(token.column)))
                    elif (tyype_variable != tyype_expression) and not (tyype_variable == Type.FLOAT and tyype_expression == Type.INT) :
                        print("ERROR: trying to assign '{}' expression to variable '{}' in line {} and column {}".format(tyype_expression, name, str(token.line), str(token.column)))
                    
                    break

        return self.visitChildren(ctx)

    '''
    variable_assignment
	    : (identifier | array) OP=('='|'+='|'-='|'*='|'/=') expression
	    | (identifier | array) OP=('++'|'--')
	    ;
    '''
    # Visit a parse tree produced by GrammarParser#variable_assignment.
    def visitVariable_assignment(self, ctx:GrammarParser.Variable_assignmentContext):
        op = ctx.OP.text

        tyype_variable = Type.VOID

        if ctx.identifier() != None:
            
            name = ctx.identifier().getText()
            token = ctx.identifier().IDENTIFIER().getPayload()

            def_identifier = self.ids_defined.get(name)
            if def_identifier == None:
                print("ERROR: trying to assign to a non-defined variable '{}' in line {} and column {}".format(name, str(token.line), str(token.column)))
            
            elif ctx.expression() == None:
                tyype = def_identifier[0]
                if tyype != Type.INT or tyype != Type.FLOAT:
                    print("ERROR: binary operator '{}' used to variable of type '{}' in line {} and column {}".format(op, tyype, str(token.line), str(token.column)))
                
            else:    
                tyype_expression = self.visitExpression(ctx.expression())
                tyype_variable = def_identifier[0]

                if tyype_variable == Type.INT and tyype_expression == Type.FLOAT:
                    print("WARNING: Possible loss of information assigning float expression to int variable '{}' in line {} and column {}".format(str(name), str(token.line), str(token.column)))
                elif tyype_variable == tyype_expression:
                    if op != "=":
                        print("ERROR: binary operator '{}' used to variable of type '{}' in line {} and column {}".format(op, tyype_variable, str(token.line), str(token.column)))
                elif not (tyype_variable == Type.FLOAT and tyype_expression == Type.INT) :
                    print("ERROR: trying to assign '{}' expression to variable '{}' in line {} and column {}".format(tyype_expression, name, str(token.line), str(token.column)))
                

        return self.visitChildren(ctx)

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
    def visitExpression(self, ctx:GrammarParser.ExpressionContext):
        #tyype = Type.VOID

        numberOfExpressions = len(ctx.expression())

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
                print("ERROR: trying to use in expression a non-defined variable '{}' in line {} and column {}".format(name, str(token.line), str(token.column)))
                return None
            
            tyype = def_variable[0]
            return tyype

        elif ctx.array() != None:
            name = ctx.array().getText()
            tyype = self.ids_defined.get(name)

        
        elif ctx.function_call() != None:
            print("function call")
        
        elif ctx.OP() != None:
            if len(ctx.expression()) == 1:
                tyype = self.visitExpression(ctx.expression())
                if tyype == Type.INT or tyype == Type.FLOAT:
                    return tyype
                else:
                    print("erro tentou botar + ou - algo q n é string")
            elif len(ctx.expression()) == 2:
                tyype1 = self.visitExpression(ctx.expression(1))
                tyype2 = self.visitExpression(ctx.expression(2))
                #continuar aq
        elif ctx.expression() != None: #caso do parenteses
            return self.visitExpression(ctx.expression())
        return Type.VOID


    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#array_literal.
    def visitArray_literal(self, ctx:GrammarParser.Array_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#function_call.
    def visitFunction_call(self, ctx:GrammarParser.Function_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#arguments.
    def visitArguments(self, ctx:GrammarParser.ArgumentsContext):
        return self.visitChildren(ctx)


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

