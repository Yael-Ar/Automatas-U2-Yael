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
 
class InterpreteEtapa4(BazilioVisitor):
    def __init__(self, entrada=None, salida=None):
        self.procedimientos = {}      # nombre -> (parámetros, bloque)
        self.marcos = []              # Pila de marcos de variables locales por llamada
        self._entrada = entrada if entrada is not None else sys.stdin
        self._tokens_entrada = []
        self._salida = salida if salida is not None else print
 
    @property
    def _vars(self):
        return self.marcos[-1]
 
    def cargar(self, arbol):
        """Registra todos los procedimientos y valida nombres duplicados."""
        for proc in arbol.procedimiento():
            nombre = proc.PROC_ID().getText()
            params = [v.getText() for v in proc.VAR()]
            if nombre in self.procedimientos:
                raise ErrorBazilio(f"El procedimiento {nombre} está definido más de una vez.")
            if len(set(params)) != len(params):
                raise ErrorBazilio(f"El procedimiento {nombre} repite nombres de parámetros formales.")
            self.procedimientos[nombre] = (params, proc.bloque())
 
    def ejecutar(self, inicio="Main"):
        self._llamar(inicio, [])
 
    def _llamar(self, nombre, valores):
        """Gestiona la llamada a un procedimiento creando un nuevo marco de variables."""
        if nombre not in self.procedimientos:
            raise ErrorBazilio(f"Se llamó al procedimiento {nombre}, que no está definido.")
        params, bloque = self.procedimientos[nombre]
        if len(params) != len(valores):
            raise ErrorBazilio(f"{nombre} espera {len(params)} parámetro(s) y recibió {len(valores)}.")
        
        # Empuja un diccionario nuevo combinando parámetros y valores pasados
        self.marcos.append(dict(zip(params, valores)))
        try:
            self.visit(bloque)
        finally:
            # Asegura retirar el marco al terminar la ejecución del procedimiento
            self.marcos.pop()
 
    def visitBloque(self, ctx):
        for instruccion in ctx.instruccion():
            self.visit(instruccion)
 
    def visitAsignacion(self, ctx):
        valor = self.visit(ctx.expr())
        self._vars[ctx.VAR().getText()] = valor
 
    def visitLectura(self, ctx):
        self._vars[ctx.VAR().getText()] = self._leer_entero()
 
    def visitEscritura(self, ctx):
        partes = []
        for hijo in list(ctx.getChildren())[1:]:
            if hasattr(hijo, "symbol"):
                partes.append(hijo.getText()[1:-1])
            else:
                partes.append(str(self.visit(hijo)))
        self._salida(" ".join(partes))
 
    # ---------- NUEVO EN ETAPA 4: Invocación de Procedimientos ----------
    def visitInvocacion(self, ctx):
        valores = [self.visit(e) for e in ctx.expr()]
        self._llamar(ctx.PROC_ID().getText(), valores)
 
    def visitCondicional(self, ctx):
        bloques = ctx.bloque()
        if self._verdadero(self.visit(ctx.expr())):
            self.visit(bloques[0])
        elif len(bloques) > 1:
            self.visit(bloques[1])
 
    def visitIteracion(self, ctx):
        while self._verdadero(self.visit(ctx.expr())):
            self.visit(ctx.bloque())
 
    def visitMulDiv(self, ctx):
        a, b = self._operandos(ctx)
        op = ctx.op.text
        if op == "*":
            return a * b
        if b == 0:
            raise ErrorBazilio("División por cero.")
        q = _div_c(a, b)
        return q if op == "/" else a - b * q
 
    def visitSumaResta(self, ctx):
        a, b = self._operandos(ctx)
        return a + b if ctx.op.text == "+" else a - b
 
    def visitRelacional(self, ctx):
        a, b = self._operandos(ctx)
        op = ctx.op.text
        resultado = {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]
        return int(resultado)
 
    def visitIgualdad(self, ctx):
        a = self.visit(ctx.expr(0))
        b = self.visit(ctx.expr(1))
        op = ctx.op.text
        resultado = (a == b) if op == "=" else (a != b)
        return int(resultado)
 
    def visitParentesis(self, ctx):
        return self.visit(ctx.expr())
 
    def visitEntero(self, ctx):
        return int(ctx.getText())
 
    def visitVariable(self, ctx):
        # Busca la variable en el marco actual (cima de la pila)
        return self._vars.get(ctx.getText(), 0)
 
    @staticmethod
    def _entero(valor):
        if isinstance(valor, list):
            raise ErrorBazilio("Se esperaba un entero y se encontró una lista.")
        return valor
 
    def _operandos(self, ctx):
        izquierda = self._entero(self.visit(ctx.expr(0)))
        derecha = self._entero(self.visit(ctx.expr(1)))
        return izquierda, derecha
 
    @staticmethod
    def _verdadero(valor):
        if isinstance(valor, list):
            raise ErrorBazilio("Una condición debe ser un entero (0 es falso, otro valor es verdadero).")
        return valor != 0
 
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
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("Uso: python3 bazilio_etapa4.py programa.bzl [ProcedimientoInicial]")
        return 2
    ruta = args[0]
    inicio = args[1] if len(args) > 1 else "Main"
    try:
        arbol = parsear(FileStream(ruta, encoding="utf-8"))
        interprete = InterpreteEtapa4()
        interprete.cargar(arbol)
        interprete.ejecutar(inicio)
    except ErrorBazilio as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0
 
if __name__ == "__main__":
    sys.setrecursionlimit(200000)
    sys.exit(principal(sys.argv))