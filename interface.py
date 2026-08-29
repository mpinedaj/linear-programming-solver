import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simplexSolver import solver_simplex_method
from graphicSolver import solver_graphic_method

class LinearProgrammingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solver de Programación Lineal (Gráfico y Simplex)")
        self.root.geometry("1100x700")

        # Contenedor principal con dos columnas
        self.left_frame = ttk.Frame(self.root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self.root, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.entries_objetivo = []
        self.entries_restricciones = []

        self._build_configuration_panel()

    def _build_configuration_panel(self):
        # Panel de Configuración
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

        # Contenedor dinámico de inputs
        self.inputs_frame = ttk.Frame(self.left_frame)
        self.inputs_frame.pack(fill=tk.BOTH, expand=True)

        self.generar_campos()

    def generar_campos(self):
        # Limpiar inputs previos
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        self.entries_objetivo = []
        self.entries_restricciones = []

        n_vars = int(self.num_vars_spin.get())
        n_restr = int(self.num_restr_spin.get())

        # 1. Función Objetivo
        obj_frame = ttk.LabelFrame(self.inputs_frame, text=" Función Objetivo (Max Z) ", padding="10")
        obj_frame.pack(fill=tk.X, pady=5)

        for j in range(n_vars):
            ttk.Label(obj_frame, text=f"x{j+1}:").grid(row=0, column=j*2, padx=2)
            e = ttk.Entry(obj_frame, width=6)
            e.insert(0, "1.0")
            e.grid(row=0, column=j*2+1, padx=2)
            self.entries_objetivo.append(e)

        # 2. Restricciones
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
            # Extraer función objetivo
            objetivo = [float(e.get()) for e in self.entries_objetivo]

            # Extraer restricciones
            restricciones = []
            for r in self.entries_restricciones:
                coefs = [float(e.get()) for e in r["coefs"]]
                op = r["op"].get()
                val = float(r["val"].get())
                restricciones.append({"coef": coefs, "op": op, "val": val})

            num_vars = len(objetivo)

            # Limpiar panel de resultados
            for widget in self.right_frame.winfo_children():
                widget.destroy()

            # Ejecutar Simplex (Funciona para N variables)
            res_simplex = solver_simplex_method(objetivo, restricciones)

            if res_simplex is None:
                messagebox.showerror("Error", "No se encontró solución factible o el problema es no acotado.")
                return

            self._mostrar_resultados_texto(res_simplex, num_vars)

            # Si son 2 variables, ejecutar y graficar Método Gráfico
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

        # Dibuja rectas
        for r in restricciones:
            a, b_coef = r["coef"]
            c = r["val"]
            if b_coef != 0:
                y_vals = (c - a * x_vals) / b_coef
                ax.plot(x_vals, y_vals, label=f"{a}x1 + {b_coef}x2 {r['op']} {c}")
            else:
                ax.axvline(x=c / a, label=f"{a}x1 {r['op']} {c}")

        # Polígono de región factible
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

        # Incrustar gráfico de Matplotlib dentro del Frame de Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgrammingApp(root)
    root.mainloop()