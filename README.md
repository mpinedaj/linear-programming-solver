# Linear Programming Solver (Simplex & Graphical Method)

A Python desktop application designed to solve and visualize **Linear Programming (LP)** optimization problems. It features an implementation of the **Tabular Simplex Algorithm** for $N$-dimensional problems and a dynamic **Graphical Method** renderer for 2-variable problems.

---

## Key Features

* **Tabular Simplex Algorithm:** Solves maximization problems with multiple decision variables and constraints.
* **Interactive 2D Graphical Method:** Visualizes constraint lines, boundary intersection points, and the shaded convex feasible region using `matplotlib`.
* **Dynamic GUI:** Built with `tkinter`, enabling users to configure any number of decision variables and constraints on the fly.
* **Optimal Point Highlighting:** Instantly identifies and displays the optimal solution vector and maximum target value ($Z$).

---

## Tech Stack

* **Python 3.x**
* **NumPy:** Linear algebra operations, matrix manipulation for Simplex tableaux, and system solving.
* **Matplotlib:** Graphical rendering of 2D geometry and feasible regions.
* **Tkinter / ttk:** Cross-platform GUI framework.

---

## Prerequisites

Ensure you have Python 3.8 or higher installed. Install the required dependencies using pip:

```bash
pip install numpy matplotlib
```

---

## Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/linear-programming-solver.git
   cd linear-programming-solver
   ```

2. **Run the application:**
   ```bash
   python interface.py
   ```

---

## Usage

1. **Initial Setup:** Enter the number of decision variables ($n$) and constraints, then click **Generar Tabla** (Generate Table).
2. **Input Parameters:** Define the Objective Function coefficients ($Z$) and constraint matrix parameters along with operators (`<=`, `>=`, `=`).
3. **Solve:** Click **Resolver Problema** (Solve Problem). 
   * For $n \ge 2$, the optimal values for all variables and maximum $Z$ will be computed via the **Simplex Method** and shown in the results panel.
   * For $n = 2$, an interactive chart will render, highlighting the **Feasible Region** in green and the **Optimal Point** in red.
