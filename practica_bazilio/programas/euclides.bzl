Main |:
    <w> "--- ALGORITMO DE EUCLIDES (MCD) ---"
    <w> "Ingresa el primer número:"
    <?> a
    <w> "Ingresa el segundo número:"
    <?> b
    MCD a b
:|

MCD x y |:
    while y /= 0 |:
        temp <- y
        y <- x % y
        x <- temp
    :|
    <w> "El Máximo Común Divisor es:" x
:|
