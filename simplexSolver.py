import numpy as np

def solver_simplex_method(objetivo: list[float], restricciones: list[dict]):
    num_vars = len(objetivo)
    num_restr = len(restricciones)

    # Crear los tableros simplex
    tabla = np.zeros((num_restr + 1, num_vars + num_restr + 1), dtype=float)

    # Llenar la tabla
    for i, r in enumerate(restricciones):
        tabla[i, :num_vars] = r["coef"]
        tabla[i, num_vars + i] = 1.0
        tabla[i, -1] = r["val"]

    # Fila de Z
    tabla[-1, :num_vars] = [-c for c in objetivo]

    while True:
        fila_z = tabla[-1, :-1]

        # Si en la fila de Z no hay negativos, entonces para
        if np.all(fila_z >= 0):
            break

        # Columna pivote, o sea la variable que entra
        col_pivote = np.argmin(fila_z)

        # Fila pivote, o sea la variable que sale
        col_valores = tabla[:-1, col_pivote]
        lados_derechos = tabla[:-1, -1]

        cocientes = []
        for i in range(num_restr):
            if col_valores[i] > 0:
                cocientes.append(lados_derechos[i] / col_valores[i])
            else:
                cocientes.append(np.inf) 

        fila_pivote = np.argmin(cocientes)

        if cocientes[fila_pivote] == np.inf:
            return None

        elemento_pivote = tabla[fila_pivote, col_pivote]
        tabla[fila_pivote, :] /= elemento_pivote 

        for i in range(len(tabla)):
            if i != fila_pivote:
                factor = tabla[i, col_pivote]
                tabla[i, :] -= factor * tabla[fila_pivote, :]

    solucion_vars = np.zeros(num_vars)
    
    for j in range(num_vars):
        columna = tabla[:, j]
        if np.count_nonzero(columna == 1) == 1 and np.count_nonzero(columna == 0) == len(columna) - 1:
            fila_uno = np.where(columna == 1)[0][0]
            if fila_uno < num_restr:
                solucion_vars[j] = tabla[fila_uno, -1]

    valor_z_optimo = tabla[-1, -1]

    return {
        "punto_optimo": solucion_vars,
        "valor_optimo": valor_z_optimo,
        "tabla_final": tabla
    }