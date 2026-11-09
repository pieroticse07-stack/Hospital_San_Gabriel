# Hospital San Gabriel — Módulo de Almacén y Farmacia

Proyecto universitario del Hospital San Gabriel. La rama de trabajo solicitada es `Almerco`; el checkout local donde se aplicaron estos cambios aparece como `Almerco-`. El módulo administra el catálogo de productos e insumos, las categorías hospitalarias y las entradas de inventario por lote, conservando el historial de movimientos.

## Arquitectura

- **Backend:** Python 3.14, FastAPI y Pydantic, organizado por capas bajo `backend/src/backend/`. El flujo es `apis → services → repositories`; los routers HTTP no contienen SQL y los servicios concentran reglas de negocio. No se usa ORM.
- **Persistencia:** SQL Server mediante `pyodbc`. `repositories/almacen_repository.py` concentra el acceso a datos y todas las escrituras de almacén llaman procedimientos almacenados. Los SPs gestionan transacciones SQL con `BEGIN TRANSACTION`, `COMMIT` y `ROLLBACK`.
- **Frontend:** Angular 22 standalone. Signal Forms (`@angular/forms/signals`) enlaza modelos reactivos, validaciones y estados de error visibles. Bootstrap 5 proporciona navegación, formularios, tablas responsivas, alertas y presentación adaptable.
- **Comunicación:** el frontend usa `frontend/src/environments/environment.ts` para la URL de la API (por defecto `http://localhost:8000`). FastAPI habilita CORS para localhost:4200.

## Avance de requerimientos

### RF01 — Gestión de productos

- Alta, listado y edición de productos con código, nombre, descripción, categoría, precio y stock mínimo.
- Código único en SQL Server; precio unitario y stock mínimo deben ser mayores a cero, validados en formulario, esquema Pydantic y restricciones/SP.
- Búsqueda por código o nombre y filtro por categoría.
- El stock actual se calcula desde los lotes. Se advierte visualmente cuando queda bajo el mínimo.
- Desactivación lógica mediante `Estado = 0`; no se elimina producto ni historial.

### RF02 — Gestión de categorías

- Alta y listado de categorías con nombre y descripción.
- El script carga inicialmente Medicamentos, Material médico, Laboratorio y Limpieza hospitalaria.
- Los productos se relacionan mediante clave foránea; solo categorías activas se ofrecen para nuevos productos.

### RF03 — Registro de entradas

- Registro de producto, cantidad positiva, motivo (compras, donaciones o devoluciones), número de lote, vencimiento futuro y observación opcional.
- El procedimiento `usp_Entrada_Registrar` bloquea el producto/lote durante la operación, crea el lote o suma a un lote existente compatible, y registra el movimiento de historial en una misma transacción.
- Un error en la operación ejecuta rollback y no deja stock e historial desincronizados.
- La pantalla lista entradas registradas y actualiza el stock al confirmar una entrada.

## Estructura relevante

```text
backend/src/backend/
  apis/almacen.py
  schemas/almacen.py
  services/almacen_service.py
  repositories/almacen_repository.py
  config.py, errors.py, main.py
frontend/src/app/
  components/almacen/almacen.component.ts
  interfaces/almacen.ts
  services/almacen.service.ts
  app.config.ts, app.routes.ts
script_hospital.sql
```

## Base de datos SQL Server

El archivo raíz `script_hospital.sql` crea (si no existen) la base `HospitalSanGabriel`, las tablas `Categorias`, `Productos`, `Lotes` e `HistorialMovimientos`, carga categorías iniciales y define los procedimientos de escritura. Es idempotente en las tablas existentes y no las elimina.

1. Instala/inicia SQL Server (Developer/Express o una instancia institucional) y habilita conexiones TCP/IP si aplica. Asegura permisos para crear base de datos, tablas y procedimientos.
2. Abre `script_hospital.sql` en SQL Server Management Studio o Azure Data Studio y ejecútalo conectado a una instancia con permisos de creación. También puede ejecutarse con `sqlcmd -S <servidor> -E -i script_hospital.sql` para autenticación integrada.
3. Comprueba que `HospitalSanGabriel` contiene las cuatro tablas, las cuatro categorías iniciales y los SP `usp_Categoria_Crear`, `usp_Producto_Crear`, `usp_Producto_Actualizar`, `usp_Producto_Desactivar` y `usp_Entrada_Registrar`.
4. Instala el driver ODBC de SQL Server compatible con el valor `DB_DRIVER` configurado para Python.
5. Crea `backend/.env` (no se versiona) con credenciales de la instancia:

```dotenv
DB_SERVER=localhost
DB_NAME=HospitalSanGabriel
DB_USER=usuario_sql
DB_PASSWORD=contraseña
DB_DRIVER=ODBC Driver 17 for SQL Server
CORS_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
```

Para autenticación de Windows, el esquema de conexión actual también requiere usuario y contraseña SQL; adapta `config.py` para autenticación integrada si tu instancia solo permite esa modalidad. No guardes credenciales reales en Git.

## Ejecución del backend

Requiere Python 3.14, `uv`, driver ODBC y SQL Server disponible. Desde la raíz:

```powershell
cd backend
uv sync
uv run uvicorn backend.main:app --reload
```

La API queda en `http://localhost:8000`; documentación interactiva en `http://localhost:8000/docs` y estado de conexión en `http://localhost:8000/health`.

Endpoints nuevos:

| Método | Ruta | Uso |
| --- | --- | --- |
| GET / POST | `/categorias` | Listar / registrar categorías |
| GET / POST | `/productos` | Listar con `categoria_id`, `busqueda`, `incluir_inactivos` / crear |
| PUT / DELETE | `/productos/{producto_id}` | Editar / desactivar lógicamente |
| GET / POST | `/entradas` | Consultar historial / registrar entrada |

## Ejecución del frontend

Requiere Node.js y npm compatibles con Angular 22. En otra terminal:

```powershell
cd frontend
npm install
npx ng serve
```

Abre `http://localhost:4200`. La pantalla inicial permite cambiar entre Productos, Categorías y Registro de entradas. Las operaciones necesitan que el backend y SQL Server estén activos.

## Validaciones y manejo de errores

Los formularios Signal Forms muestran errores en pantalla y bloquean envíos inválidos. Pydantic vuelve a validar el payload en el backend y SQL Server aplica claves foráneas, unicidad, checks y SP transaccionales como última garantía. Errores de validación se responden como HTTP 422, conflictos de alta como 409 y errores de base de datos como 503.
