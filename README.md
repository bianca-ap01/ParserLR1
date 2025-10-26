# LR(1) Toolkit — Labs Library + Fullstack App

Generador/analizador **LR(1)** estilo “labs” (paquete `lr1`) + **aplicación full-stack** (FastAPI + Vite/React) para visualizar:

* **LR(1):** conjuntos de items/estados (closure), tablas **ACTION/GOTO**
* **Expresiones regulares → ε-NFA:** construcción de **Thompson** + ε-closure
* **DFA:** construcción por **subconjuntos** + tabla de transiciones

## Estructura del repo

```
.
├─ lr1_project/          # Paquete Python "lr1" (pip instalable, modo editable)
│  ├─ lr1/               # Código fuente de la librería
│  └─ setup.py / pyproject.toml
└─ lr1_app/
   ├─ backend/           # FastAPI (uvicorn)
   │  └─ app/main.py
   └─ frontend/          # Vite + React
      ├─ src/
      └─ index.html
```

## Requisitos

* **Python 3.10+**
* **Node.js 18+** (recomendado 20 LTS) y **npm**
* macOS / Linux / WSL / Windows (PowerShell)

> Si usas Windows puro, se recomienda PowerShell o Git Bash.

---

## ▶️ Quick Start

> Ya hay un `Makefile` en la raíz que automatiza todo.

1. **Preparar entorno y dependencias**

```bash
make setup
```

2. **Levantar todo en modo desarrollo (backend + frontend)**

```bash
make dev
```

* Backend (FastAPI) en: `http://localhost:8000`

  * Docs: `http://localhost:8000/docs` (Swagger) / `http://localhost:8000/redoc`
* Frontend (Vite) imprimirá su URL (p.ej. `http://localhost:5173`)

3. **Correr por separado (opcional)**

```bash
make backend          # solo FastAPI
make frontend         # solo Vite
```

4. **Limpiar/Reset (opcional)**

```bash
make clean-py         # borra __pycache__/egg-info/build
make clean-node       # borra caches de Vite
make reset            # ⚠️ elimina venv y node_modules
```

**Variables útiles**

* Cambiar puerto del backend:

  ```bash
  make backend PORT=8080
  make dev PORT=8080
  ```
* Exponer Vite en red local:

  ```bash
  make frontend VITE_HOST=--host
  make dev VITE_HOST=--host
  ```

---

## ¿Qué puedo hacer en la app?

* **Panel “Grammar / LR(1)”**

  * Define una gramática → genera **items LR(1)** (closure), **autómata LR(1)** y **tablas ACTION/GOTO**.
* **Panel “Regex → ε-NFA / DFA”**

  * Escribe una **expresión regular** → verás el **ε-NFA (Thompson)**, su **ε-closure**, y el **DFA por subconjuntos** + **tabla de transiciones**.

---

## 🚀 Producción local

1. **Preparar dependencias** (una sola vez):

```bash
make setup
```

2. **Levantar el backend en producción** (sin reload, con N workers):

```bash
make prod PORT=8000 WORKERS=4
```

* API: `http://localhost:8000`
* Docs: `http://localhost:8000/docs`

3. **Vista rápida del frontend compilado** (servidor estático temporal de Vite):

```bash
make preview
```

* Abre la URL que imprime Vite (p. ej., `http://localhost:4173`).

> **En producción real:** sirve `lr1_app/frontend/dist/` con Nginx/Caddy/hosting estático y deja el backend en `:8000` detrás de un reverse proxy.
> Puedes ajustar `PORT` y `WORKERS` al ejecutar `make prod`.


