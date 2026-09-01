import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Interfaz
class LinearProgrammingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solver de Programación Lineal (Grafico y Simplex)")
        self.root.geometry("1100x700")

        # Dos columnas
        self.left_frame = ttk.Frame(self.root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self.root, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.entries_objetivo = []
        self.entries_restricciones = []

        self._build_configuration_panel()

    def _build_configuration_panel(self):
        config_group = ttk.LabelFrame(self.left_frame, text=" Configuración Inicial ", padding="10")
        config_group.pack(fill=tk.X, pady=5)

        ttk.Label(config_group, text="Variables de decisión (n):").grid(row=0, column=0, sticky=tk.W)
        self.num_vars_spin = ttk.Spinbox(config_group, from_=2, to=10, width=5)
        self.num_vars_spin.set(2)
        self.num_vars_spin.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(config_group, text="Cantidad restricciones:").grid(row=1, column=0, sticky=tk.W)
        self.num_restr_spin = ttk.Spinbox(config_group, from_=1, to=15, width=5)
        self.num_restr_spin.set(2)
        self.num_restr_spin.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(config_group, text="Generar Tabla", command=self.generar_campos).grid(row=2, column=0, columnspan=2, pady=10)

        self.inputs_frame = ttk.Frame(self.left_frame)
        self.inputs_frame.pack(fill=tk.BOTH, expand=True)

        self.generar_campos()

    def generar_campos(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        self.entries_objetivo = []
        self.entries_restricciones = []

        n_vars = int(self.num_vars_spin.get())
        n_restr = int(self.num_restr_spin.get())

        # Función Objetivo
        obj_frame = ttk.LabelFrame(self.inputs_frame, text=" Función Objetivo (Max Z) ", padding="10")
        obj_frame.pack(fill=tk.X, pady=5)

        for j in range(n_vars):
            ttk.Label(obj_frame, text=f"x{j+1}:").grid(row=0, column=j*2, padx=2)
            e = ttk.Entry(obj_frame, width=6)
            e.insert(0, "1.0")
            e.grid(row=0, column=j*2+1, padx=2)
            self.entries_objetivo.append(e)

        # Restricciones
        restr_frame = ttk.LabelFrame(self.inputs_frame, text=" Restricciones ", padding="10")
        restr_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        for i in range(n_restr):
            row_entries = []
            for j in range(n_vars):
                e = ttk.Entry(restr_frame, width=5)
                e.insert(0, "1.0")
                e.grid(row=i, column=j*2, padx=2, pady=2)
                row_entries.append(e)
                ttk.Label(restr_frame, text=f"x{j+1} +").grid(row=i, column=j*2+1)

            op_combo = ttk.Combobox(restr_frame, values=["<=", ">=", "="], width=4, state="readonly")
            op_combo.set("<=")
            op_combo.grid(row=i, column=n_vars*2, padx=2)

            val_entry = ttk.Entry(restr_frame, width=6)
            val_entry.insert(0, "10.0")
            val_entry.grid(row=i, column=n_vars*2+1, padx=2)

            self.entries_restricciones.append({
                "coefs": row_entries,
                "op": op_combo,
                "val": val_entry
            })

        # Botón Resolver
        ttk.Button(self.inputs_frame, text="🚀 Resolver Problema", command=self.resolver).pack(fill=tk.X, pady=10)

    def resolver(self):
        try:
            objetivo = [float(e.get()) for e in self.entries_objetivo]

            restricciones = []
            for r in self.entries_restricciones:
                coefs = [float(e.get()) for e in r["coefs"]]
                op = r["op"].get()
                val = float(r["val"].get())
                restricciones.append({"coef": coefs, "op": op, "val": val})

            num_vars = len(objetivo)

            for widget in self.right_frame.winfo_children():
                widget.destroy()

            # Ejecutar Simplex 
            res_simplex = solver_simplex_method(objetivo, restricciones)

            if res_simplex is None:
                messagebox.showerror("Error", "No se encontró solución factible o el problema es no acotado.")
                return

            self._mostrar_resultados_texto(res_simplex, num_vars)

            # Para dos variables se hace metodo grafico
            if num_vars == 2:
                res_grafico = solver_graphic_method(objetivo, restricciones)
                if res_grafico:
                    self._graficar_2d(res_grafico)

        except ValueError:
            messagebox.showerror("Error de Input", "Por favor ingresa valores numéricos válidos en todos los campos.")

    def _mostrar_resultados_texto(self, res_simplex, num_vars):
        output_frame = ttk.LabelFrame(self.right_frame, text=" Resultados ", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        pt_optimo = res_simplex["punto_optimo"]
        z_val = res_simplex["valor_optimo"]

        vars_str = ", ".join([f"x{i+1} = {pt_optimo[i]:.2f}" for i in range(num_vars)])
        res_text = f" Valor Óptimo (Z): {z_val:.2f}\n Variables: {vars_str}"

        lbl = ttk.Label(output_frame, text=res_text, font=("Helvetica", 11, "bold"), foreground="green")
        lbl.pack(anchor=tk.W)

    def _graficar_2d(self, res_grafico):
        fig, ax = plt.subplots(figsize=(6, 5))

        puntos = res_grafico["puntos_factibles"]
        optimo = res_grafico["punto_optimo"]
        restricciones = res_grafico["restricciones"]

        max_x = max(10, np.max(puntos[:, 0]) * 1.3)
        max_y = max(10, np.max(puntos[:, 1]) * 1.3)
        x_vals = np.linspace(0, max_x, 200)

        for r in restricciones:
            a, b_coef = r["coef"]
            c = r["val"]
            if b_coef != 0:
                y_vals = (c - a * x_vals) / b_coef
                ax.plot(x_vals, y_vals, label=f"{a}x1 + {b_coef}x2 {r['op']} {c}")
            else:
                ax.axvline(x=c / a, label=f"{a}x1 {r['op']} {c}")

        centro = np.mean(puntos, axis=0)
        angulos = np.arctan2(puntos[:, 1] - centro[1], puntos[:, 0] - centro[0])
        puntos_ordenados = puntos[np.argsort(angulos)]

        ax.fill(puntos_ordenados[:, 0], puntos_ordenados[:, 1], color='lightgreen', alpha=0.4, label='Región Factible')
        ax.scatter(puntos[:, 0], puntos[:, 1], color='blue', zorder=5)
        ax.scatter(optimo[0], optimo[1], color='red', s=100, zorder=6, label=f'Óptimo ({optimo[0]:.1f}, {optimo[1]:.1f})')

        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.set_xlabel("$x_1$")
        ax.set_ylabel("$x_2$")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

#----------------------------------------------------------------------------------------------------------------------------------------

#Funcion para el metodo grafico
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
   
#----------------------------------------------------------------------------------------------------------------------------------------  
 
# Funcion para el metodo simplex
def solver_simplex_method(objetivo: list[float], restricciones: list[dict]):
    num_vars = len(objetivo)
    num_restr = len(restricciones)

    # Crear los tableros simplex
    tabla = np.zeros((num_restr + 1, num_vars + num_restr + 1), dtype=float)

    for i, r in enumerate(restricciones):
        tabla[i, :num_vars] = r["coef"]
        tabla[i, num_vars + i] = 1.0
        tabla[i, -1] = r["val"]

    # Fila de Z
    tabla[-1, :num_vars] = [-c for c in objetivo]

    while True:
        fila_z = tabla[-1, :-1]

        if np.all(fila_z >= 0):
            break

        # Columna pivote
        col_pivote = np.argmin(fila_z)

        # Fila pivote
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

if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgrammingApp(root)
    root.mainloop()