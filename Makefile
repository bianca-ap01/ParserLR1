# ===========================
# LR(1) Toolkit – Makefile
# ===========================

# --- Configurables ---
PYTHON      ?= python3

# Usa venv activo si existe; si no, .venv en la raíz
VENV_DIR    ?= $(if $(VIRTUAL_ENV),$(VIRTUAL_ENV),.venv)
VENV_BIN    := $(abspath $(VENV_DIR))/bin
PY          := $(VENV_BIN)/python
PIP         := $(VENV_BIN)/pip
UVICORN     := $(VENV_BIN)/uvicorn

BACKEND_DIR := lr1_app/backend
FRONTEND_DIR:= lr1_app/frontend

PORT        ?= 8000
VITE_HOST   ?=
WORKERS     ?= 2
ENV         ?= production

venv:
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo ">>> Usando venv activo: $$VIRTUAL_ENV"; \
	else \
		echo ">>> Creando venv en $(VENV_DIR)"; \
		mkdir -p "$(VENV_DIR)"; \
		$(PYTHON) -m venv "$(VENV_DIR)"; \
	fi
	@echo ">>> Python en: $(PY)"

# 👇 OJO: sin cd, y sin comillas alrededor de $(PIP)
install-lib: venv
	@echo ">>> Instalando paquete lr1 (editable)"
	$(PIP) install -e lr1_project

## help: muestra esta ayuda
help:
	@grep -E '(^[a-zA-Z0-9/_-]+:)|(^## )' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS=":|## "}; /^[^#].*:/ {printf "\033[36m%-24s\033[0m %s\n", $$1, $$3} /^## /{print substr($$0,4)}'

## setup: crea venv e instala el paquete lr1 en editable + deps de backend y frontend
setup: venv install-lib install-backend install-frontend

## install-backend: instala dependencias del backend
install-backend: venv
	@echo ">>> Instalando requirements del backend"
	"$(PIP)" install -r "$(BACKEND_DIR)/requirements.txt"

## install-frontend: instala dependencias del frontend (npm)
install-frontend:
	@echo ">>> Instalando deps de frontend"
	cd "$(FRONTEND_DIR)" && npm install

## backend: levanta FastAPI (uvicorn --reload)
backend:
	@echo ">>> Backend en http://localhost:$(PORT)"
	cd "$(BACKEND_DIR)" && "$(UVICORN)" app.main:app --host 0.0.0.0 --port "$(PORT)" --reload

## frontend: levanta Vite (npm run dev)
frontend:
	cd "$(FRONTEND_DIR)" && npm run dev $(VITE_HOST)

## dev: backend + frontend en paralelo (modo desarrollo)
dev:
	set -euo pipefail
	echo ">>> Iniciando backend (http://localhost:$(PORT)) y frontend (Vite imprimirá su URL)..."
	trap 'jobs -p | xargs -r kill' INT TERM EXIT
	( cd "$(BACKEND_DIR)"  && "$(UVICORN)" app.main:app --host 0.0.0.0 --port "$(PORT)" --reload ) &
	( cd "$(FRONTEND_DIR)" && npm run dev $(VITE_HOST) ) &
	wait -n

## urls: imprime URLs útiles
urls:
	@echo "Backend  -> http://localhost:$(PORT)"
	@echo "Frontend -> (Vite mostrará su URL al iniciar: normalmente http://localhost:5173)"

# ---------- Producción ----------
## build-frontend: compila frontend a lr1_app/frontend/dist
build-frontend:
	@echo ">>> Compilando frontend (Vite build)"
	cd "$(FRONTEND_DIR)" && npm run build

## preview: sirve el build estático localmente (no prod real)
preview:
	cd "$(FRONTEND_DIR)" && npm run preview

## prod: corre SOLO el backend en modo producción (sin reload, con WORKERS). Sirve el build estático por separado (nginx/preview)
prod: venv install-backend build-frontend
	@echo ">>> Iniciando backend en modo producción (PORT=$(PORT), WORKERS=$(WORKERS))"
	cd "$(BACKEND_DIR)" && ENV="$(ENV)" "$(UVICORN)" app.main:app --host 0.0.0.0 --port "$(PORT)" --workers "$(WORKERS)"

## prod-all: backend producción + preview estático del frontend (útil para demo local)
prod-all: prod
	@echo ">>> (en otra terminal) ejecuta: make preview"
	@echo ">>> Esto sirve el build estático en un puerto temporal y el backend en $(PORT)."

# ---------- Limpieza ----------
## clean-py: borra artefactos Python (build/egg-info/__pycache__)
clean-py:
	@echo ">>> Limpiando artefactos Python"
	find lr1_project -type d -name "__pycache__" -prune -exec rm -rf {} + || true
	find lr1_project -maxdepth 1 -type d -name "*.egg-info" -prune -exec rm -rf {} + || true
	rm -rf lr1_project/build lr1_project/dist

## clean-node: borra caches básicos del frontend (no borra node_modules)
clean-node:
	@echo ">>> Limpiando caches de frontend"
	cd "$(FRONTEND_DIR)" && rm -rf .vite .cache 2>/dev/null || true

## reset: elimina venv y node_modules (⚠️ operación destructiva)
reset:
	@echo ">>> Eliminando venv y node_modules (⚠️)"
	rm -rf "$(VENV_DIR)"
	cd "$(FRONTEND_DIR)" && rm -rf node_modules

.PHONY: help setup venv install-lib install-backend install-frontend backend frontend dev urls \
	build-frontend preview prod prod-all \
	clean-py clean-node reset