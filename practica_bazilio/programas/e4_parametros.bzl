Main |:
    <w> "Iniciando prueba de error de parámetros..."
    ### El procedimiento Suma espera 2 parámetros (a y b), pero solo le enviamos 1 ###
    Suma 10
    <w> "Esto no debería imprimirse."
:|

Suma a b |:
    resultado <- a + b
    <w> "El resultado es:" resultado
:|
