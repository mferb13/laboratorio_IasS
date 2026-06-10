# Laboratorio IaaS - UTP
## Sistemas Operativos — Tecnología en Desarrollo de Software

## Descripción
Implementación de un entorno IaaS usando contenedores Incus con autenticación SSO, API REST protegida con JWT y base de datos distribuida.

## Tecnologías
- **Incus** — Hipervisor de contenedores del sistema
- **Docker** — Contenedor de aplicación (dentro de Incus)
- **Keycloak 26.2.4** — Autenticación SSO con JWT
- **FastAPI + Uvicorn** — API REST con CRUD
- **CockroachDB v24.1.4** — Base de datos distribuida (3 nodos)

## Arquitectura
| Contenedor | Servicio | IP | Puerto |
|---|---|---|---|
| keycloak-server | Docker + Keycloak | 10.68.32.149 | 8080 |
| backend | FastAPI + Dashboard | 10.68.32.170 | 8000 |
| db-node1 | CockroachDB Nodo 1 | 10.68.32.4 | 26257 |
| db-node2 | CockroachDB Nodo 2 | 10.68.32.229 | 26257 |
| db-node3 | CockroachDB Nodo 3 | 10.68.32.156 | 26257 |

## Acceso
- **Dashboard:** http://10.68.32.170:8000/dashboard
- **API Docs:** http://10.68.32.170:8000/docs
- **Keycloak:** http://10.68.32.149:8080
- **Usuario demo:** testuser / test123

## Flujo de autenticación
Usuario → Login Keycloak → Token JWT → FastAPI valida → CockroachDB → Respuesta

## Estructura del proyecto
- `main.py` — Código fuente FastAPI
- `register.html` — Pantalla de registro
