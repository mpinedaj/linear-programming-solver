import numpy as np

def solver_graphic_method(objetivo: list[float], restricciones: list[dict], maximizar: bool = True):
    
    # Se le pone no negatividad
    restricciones_completas = restricciones + [
        {"coef": [1.0, 0.0], "op": ">=", "val": 0.0},
        {"coef": [0.0, 1.0], "op": ">=", "val": 0.0}
    ]
    
    cant_restricciones = len(restricciones_completas)
    
    puntos = []
    # Mira las restricciones y despues las mete en puntos
    for i in range(cant_restricciones):
        for j in range(i + 1, cant_restricciones):
            A = np.array([restricciones_completas[i]["coef"], restricciones_completas[j]["coef"]], dtype=float)
            b = np.array([restricciones_completas[i]["val"], restricciones_completas[j]["val"]], dtype=float)

            if np.linalg.matrix_rank(A) == 2:
                pt = np.linalg.solve(A, b)
                puntos.append(pt)
    
    # Ver si los puntos de interseccion estan dentro de la region factible
    puntos_factibles = []
    for pt in puntos:
        x1, x2 = pt
        
        if x1 < 0 or x2 < 0:
            continue
        
        valid = True
        for r in restricciones_completas:
            val = r["coef"][0] * x1 + r["coef"][1] * x2
            op = r["op"]
            target = r["val"]

            if op == "<=" and val > target:
                valid = False; break
            elif op == ">=" and val < target:
                valid = False; break
            elif op == "=" and val != target:
                valid = False; break

        if valid:
            puntos_factibles.append(pt)

    puntos_factibles = np.array(puntos_factibles)
    if len(puntos_factibles) == 0:
        return None
    
    z_valores = []  
    for p in puntos_factibles:
        z = objetivo[0] * p[0] + objetivo[1] * p[1]
        z_valores.append(z)
        
    if maximizar:
        indice_optimo = np.argmax(z_valores)
    else:
        indice_optimo = np.argmin(z_valores)

    punto_optimo = puntos_factibles[indice_optimo]
    valor_z_optimo = z_valores[indice_optimo]

    return {
        "puntos_factibles": puntos_factibles,
        "punto_optimo": punto_optimo,
        "valor_optimo": valor_z_optimo,
        "restricciones": restricciones
    }