Main |:
    <w> "--- TORRES DE HANÓI MUSICAL ---"
    <w> "Interpretando resolución con 3 discos..."
    HanoiMusical 3 C4 G4 E4
:|

HanoiMusical discos origen destino auxiliar |:
    if discos > 0 |:
        HanoiMusical discos - 1 origen auxiliar destino
        ### Combinamos el origen con el nivel del disco para variar la nota en cada paso ###
        (:) origen + discos * 2
        HanoiMusical discos - 1 auxiliar destino origen
    :|
:|