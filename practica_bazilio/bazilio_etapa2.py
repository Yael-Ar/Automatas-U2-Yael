import sys
from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener
from BazilioLexer import BazilioLexer
from BazilioParser import BazilioParser
from BazilioVisitor import BazilioVisitor
 
class ErrorBazilio(Exception):
    """Error de sintaxis o de ejecución de un programa Bazilio."""
 
class _ListenerErrores(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ErrorBazilio(f"Error de sintaxis en la línea {line}, columna {column}: {msg}")
 
def parsear(flujo):
    lexer = BazilioLexer(flujo)
    lexer.removeErrorListeners()
    lexer.addErrorListener(_ListenerErrores())
    parser = BazilioParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(_ListenerErrores())
    return parser.programa()
 
def _div_c(a, b):
    """División entera con truncamiento hacia cero, como en C."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q
 
class InterpreteEtapa2(BazilioVisitor):
    def __init__(self, entrada=None, salida=None):
        self.variables = {}
        self._entrada = entrada if entrada is not None else sys.stdin
        self._tokens_entrada = []
        self._salida = salida if salida is not None else print
 
    def ejecutar(self, arbol):
        # En la Etapa 2 buscamos el procedimiento Main para ejecutar su bloque
        for proc in arbol.procedimiento():
            if proc.PROC_ID().getText() == "Main":
                self.visit(proc.bloque())
                return
        raise ErrorBazilio("No se encontró el procedimiento Main.")
 
    def visitBloque(self, ctx):
        for instruccion in ctx.instruccion():
            self.visit(instruccion)
 
    def visitAsignacion(self, ctx):
        valor = self.visit(ctx.expr())
        self.variables[ctx.VAR().getText()] = valor
 
    def visitLectura(self, ctx):
        self.variables[ctx.VAR().getText()] = self._leer_entero()
 
    def visitEscritura(self, ctx):
        partes = []
        for hijo in list(ctx.getChildren())[1:]:
            if hasattr(hijo, "symbol"):
                # Es un texto literal entre comillas
                partes.append(hijo.getText()[1:-1])
            else:
                # Es el resultado de evaluar una expresión
                partes.append(str(self.visit(hijo)))
        self._salida(" ".join(partes))
 
    def visitMulDiv(self, ctx):
        a = self.visit(ctx.expr(0))
        b = self.visit(ctx.expr(1))
        op = ctx.op.text
        if op == "*":
            return a * b
        if b == 0:
            raise ErrorBazilio("División por cero.")
        q = _div_c(a, b)
        return q if op == "/" else a - b * q
 
    def visitSumaResta(self, ctx):
        a = self.visit(ctx.expr(0))
        b = self.visit(ctx.expr(1))
        return a + b if ctx.op.text == "+" else a - b
 
    def visitParentesis(self, ctx):
        return self.visit(ctx.expr())
 
    def visitEntero(self, ctx):
        return int(ctx.getText())
 
    def visitVariable(self, ctx):
        nombre = ctx.getText()
        # Si la variable no ha sido asignada, por defecto vale 0
        return self.variables.get(nombre, 0)
 
    def _leer_entero(self):
        while not self._tokens_entrada:
            linea = self._entrada.readline()
            if linea == "":
                raise ErrorBazilio("Se esperaba un entero en la entrada, pero ya no hay más datos.")
            self._tokens_entrada = linea.split()
        token = self._tokens_entrada.pop(0)
        try:
            return int(token)
        except ValueError:
            raise ErrorBazilio(f"Se esperaba un entero en la entrada y se leyó «{token}».")
 
def principal(argv):
    if len(argv) < 2:
        print("Uso: python3 bazilio_etapa2.py programa.bzl")
        return 2
    try:
        arbol = parsear(FileStream(argv[1], encoding="utf-8"))
        interprete = InterpreteEtapa2()
        interprete.ejecutar(arbol)
    except ErrorBazilio as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0
 
if __name__ == "__main__":
    sys.exit(principal(sys.argv))