Main |:
    <w> "--- TORRES DE HANÓI ---"
    <w> "Ingresa el número de discos:"
    <?> n
    Hanoi n 1 3 2
:|

Hanoi discos origen destino auxiliar |:
    if discos > 0 |:
        Hanoi discos - 1 origen auxiliar destino
        <w> "Mover disco de torre" origen "a torre" destino
        Hanoi discos - 1 auxiliar destino origen
    :|
:|
