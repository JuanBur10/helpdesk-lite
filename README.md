# HelpDesk Lite — API de Tickets de Soporte

Segundo plan de mejoramiento — Programación Avanzada Python Backend (FastAPI) — SENA.

## 1. ¿Qué es el proyecto?

Es el **backend** (la API) de un sistema interno de **soporte técnico**.

- Los usuarios (**técnicos** y **empleados**) se **registran** e **inician sesión**.
- Con la sesión iniciada pueden **crear tickets** (reportes de problemas, ej: "no prende el PC"), **verlos**, **actualizarlos** y **eliminarlos**.
- Solo el **creador** de un ticket puede modificarlo o eliminarlo.

No tiene pantalla: se prueba desde **Swagger**, la página de documentación que FastAPI genera sola en `/docs`.

## 2. Tecnologías

| Tecnología | Para qué |
|---|---|
| **FastAPI** | Crear la API (los endpoints) |
| **SQLAlchemy** | Manejar la base de datos con clases de Python (ORM) |
| **SQLite** | La base de datos (un solo archivo: `helpdesk.db`) |
| **Alembic** | Las **migraciones**: crear y modificar las tablas |
| **Pydantic v2** | Validar los datos que llegan |
| **OAuth2 + JWT** | El login con token |
| **passlib[bcrypt]** | Guardar las contraseñas cifradas (hash) |

## 3. Cómo ejecutarlo

En VS Code, con la terminal dentro de la carpeta `helpdesk`:

```
..\citas_medicas\venv\Scripts\python.exe -m pip install -r requirements.txt
..\citas_medicas\venv\Scripts\python.exe -m alembic upgrade head
..\citas_medicas\venv\Scripts\python.exe -m uvicorn main:app --reload
```

1. **Instala** las librerías (solo la primera vez).
2. **Crea las tablas** aplicando las migraciones de Alembic.
3. **Arranca** el servidor.

Luego abrir: **http://127.0.0.1:8000/docs**

**Empezar de cero:** parar el servidor (Ctrl+C), borrar la base con `del helpdesk.db` y repetir los pasos 2 y 3.

## 4. Archivos del proyecto

```
helpdesk/
├── main.py            → todos los endpoints (registro, login y tickets)
├── database.py        → conexión a la base de datos SQLite
├── models.py          → las tablas: users y tickets
├── schemas.py         → validaciones de los datos (Pydantic)
├── auth.py            → contraseñas, token JWT y get_current_user
├── alembic.ini        → configuración de Alembic
├── alembic/versions/
│   ├── 0001_crear_users_y_tickets.py   → Migración 1
│   └── 0002_agregar_prioridad.py       → Migración 2
└── requirements.txt   → librerías necesarias
```

### `database.py` — la conexión

- `DATABASE_URL = "sqlite:///./helpdesk.db"`: dónde está la base de datos.
- `engine`: el motor que habla con la base de datos.
- `get_db()`: abre una conexión por cada petición y la cierra al terminar.

### `models.py` — las tablas

**Tabla `users`:** id, nombre, email (único), password (cifrada), rol.

**Tabla `tickets`:** id, titulo, descripcion, estado, prioridad, owner_id.

**Relación uno a muchos (1:N):** un usuario puede tener **muchos** tickets, y cada ticket tiene **un** solo dueño. Se hace con la llave foránea:

```python
owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
```

### `schemas.py` — las validaciones

Hay schemas **separados** para entrada y salida:

| Schema | Para qué |
|---|---|
| `UserCreate` | Lo que llega al registrarse |
| `UserResponse` | Lo que se devuelve del usuario (**sin la contraseña**) |
| `TicketCreate` | Lo que llega al crear un ticket |
| `TicketUpdate` | Lo que llega al actualizar (todo opcional) |
| `TicketResponse` | Lo que se devuelve del ticket |

**Validaciones:**

| Regla | Cómo se hace |
|---|---|
| Contraseña mínimo 8 caracteres | `password: str = Field(min_length=8)` |
| Correo válido | `email: EmailStr` |
| Solo estados permitidos | `Literal["abierto", "en_proceso", "cerrado"]` |
| Solo prioridades permitidas | `Literal["bajo", "medio", "alto"]` |
| Solo roles permitidos | `Literal["tecnico", "empleado"]` |

Si un dato no cumple, la API responde **422** automáticamente.

### `auth.py` — la seguridad

- `hash_password()`: cifra la contraseña con **bcrypt** antes de guardarla.
- `verify_password()`: compara la contraseña escrita en el login con la guardada.
- `create_token()`: **aquí se genera el token JWT**. Guarda el id del usuario y la hora de vencimiento (30 minutos), firmado con una clave secreta.
- `get_current_user()`: **protege los endpoints de tickets**. Lee el token, saca el id y busca al usuario. Si el token no sirve, responde **401**.

### `main.py` — los endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/auth/register` | Registrar un usuario |
| POST | `/auth/login` | Iniciar sesión, devuelve el token |
| POST | `/tickets/` | Crear un ticket |
| GET | `/tickets/` | Listar tickets (con paginación y filtro por estado) |
| GET | `/tickets/{ticket_id}` | Ver un ticket |
| PATCH | `/tickets/{ticket_id}` | Actualizar estado, descripción o prioridad |
| DELETE | `/tickets/{ticket_id}` | Eliminar un ticket |

Todos los de `/tickets` tienen `Depends(get_current_user)`, o sea que **sin token no funcionan**.

**Puntos clave:**

- **Crear ticket:** `owner_id=user.id`. El ticket queda del usuario que tiene la sesión iniciada, sin que él lo mande.
- **Paginación:** `consulta.offset(skip).limit(limit)`. `skip` dice cuántos saltar y `limit` cuántos traer.
- **Filtro por estado:** `if estado: consulta = consulta.filter(models.Ticket.estado == estado)`.
- **PATCH y DELETE** siguen 3 pasos:
  1. ¿El ticket existe? Si no → **404**.
  2. ¿El usuario es el dueño? Si no → **403**.
  3. Hace el cambio.

### Migraciones (Alembic)

Las tablas **no se crean con código**: se crean con migraciones, que son como un **historial de cambios** de la base de datos.

| Migración | Qué hace |
|---|---|
| **0001** | Crea las tablas `users` y `tickets` con la relación 1:N |
| **0002** | Modifica la tabla `tickets` para **agregar `prioridad`** (bajo, medio, alto; por defecto **medio**) |

```
alembic upgrade head     → aplica las migraciones
alembic history          → muestra la lista de migraciones
alembic downgrade 0001   → deshace la migración 2
```

## 5. Cómo probar todo en Swagger

En cada endpoint: clic en el endpoint → **Try it out** → llenar los datos → **Execute** → mirar el **Code** en "Server response".

### Paso 1. Registrar usuarios — `POST /auth/register`

Empleada:

```json
{
  "nombre": "Ana Torres",
  "email": "ana@test.com",
  "password": "12345678",
  "rol": "empleado"
}
```

Respuesta: **201**. Fíjate que no devuelve la contraseña.

Técnico:

```json
{
  "nombre": "Luis Gomez",
  "email": "luis@test.com",
  "password": "12345678",
  "rol": "tecnico"
}
```

Respuesta: **201**.

**Pruebas de error:**

| Qué mandas | Respuesta | Por qué |
|---|---|---|
| `"password": "123"` | **422** | Menos de 8 caracteres |
| `"email": "anatest.com"` | **422** | No es un correo válido |
| `"rol": "jefe"` | **422** | Rol no permitido |
| Registrar a Ana otra vez | **400** | El correo ya está registrado |

### Paso 2. Iniciar sesión

**Opción A, la recomendada: el botón Authorize.**

1. Clic en **Authorize** (el candado, arriba a la derecha).
2. **username:** `ana@test.com` (aquí va el **correo**).
3. **password:** `12345678`.
4. Lo demás **vacío** → clic en **Authorize** → **Close**.

El candado queda cerrado: ya tienes sesión, y Swagger manda el token solo en cada petición.

**Opción B: el endpoint `POST /auth/login`.** Sirve para mostrar el token que se genera.

- **grant_type:** vacío
- **username:** `ana@test.com`
- **password:** `12345678`
- **scope, client_id, client_secret:** vacíos

Respuesta: **200**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Con la contraseña mala → **401**.

**Importante:** si escribes algo en `grant_type` (como el correo), sale **422**. Ese campo va vacío.

### Paso 3. Crear tickets — `POST /tickets/`

(Con la sesión de Ana iniciada.)

```json
{
  "titulo": "No prende el PC",
  "descripcion": "El computador de recepción no enciende",
  "prioridad": "alto"
}
```

Respuesta: **201**:

```json
{
  "id": 1,
  "titulo": "No prende el PC",
  "descripcion": "El computador de recepción no enciende",
  "estado": "abierto",
  "prioridad": "alto",
  "owner_id": 1
}
```

- `owner_id` es 1 (Ana): se asignó **automáticamente** con el token.
- `estado` arranca en `abierto`.

Otro ticket, **sin prioridad**:

```json
{
  "titulo": "Impresora",
  "descripcion": "No imprime"
}
```

Respuesta: **201**, con `"prioridad": "medio"`, que es el valor por defecto.

**Prueba de error:** `"prioridad": "urgente"` → **422**, porque no es un valor permitido.

### Paso 4. Listar tickets — `GET /tickets/`

| Qué llenas | Resultado |
|---|---|
| Nada | Todos los tickets (máximo 10) |
| `limit` = `1` | Solo 1 ticket (**paginación**) |
| `skip` = `1`, `limit` = `1` | El segundo ticket |
| `estado` = `abierto` | Solo los abiertos (**filtro**) |
| `estado` = `cerrado` | Solo los cerrados (vacío si no hay) |

### Paso 5. Ver un ticket — `GET /tickets/{ticket_id}`

- `ticket_id` = `1` → **200**, el detalle.
- `ticket_id` = `99` → **404**, "Ticket no encontrado".

### Paso 6. Actualizar — `PATCH /tickets/{ticket_id}`

`ticket_id` = `1`:

```json
{
  "estado": "en_proceso"
}
```

Respuesta: **200**. Solo cambió el estado; la prioridad sigue en `alto`. Eso es una **actualización parcial**.

Otros ejemplos:

```json
{ "prioridad": "bajo" }
```

```json
{ "descripcion": "Ya enciende pero se reinicia" }
```

**Prueba de error:** `{ "estado": "resuelto" }` → **422**, estado no permitido.

### Paso 7. Probar que otro usuario NO puede modificar (403)

1. **Authorize** → **Logout**.
2. **Authorize** otra vez con **username:** `luis@test.com`, **password:** `12345678`.
3. `PATCH /tickets/{ticket_id}` con `ticket_id` = `1` y `{ "estado": "cerrado" }` → **403**, "No puedes modificar este ticket".
4. `DELETE /tickets/{ticket_id}` con `ticket_id` = `1` → **403**, "No puedes eliminar este ticket".

### Paso 8. Eliminar como dueña — `DELETE /tickets/{ticket_id}`

1. **Authorize** → **Logout** → entrar otra vez como **ana@test.com**.
2. `DELETE /tickets/{ticket_id}` con `ticket_id` = `1` → **200**, "Ticket eliminado".
3. `GET /tickets/{ticket_id}` con `1` → **404**, porque ya no existe.

### Paso 9. Sin sesión (401)

**Authorize** → **Logout**, y luego `GET /tickets/` → **401**. Todos los endpoints de tickets están protegidos.

## 6. Códigos de respuesta

| Código | Significa | Cuándo sale |
|---|---|---|
| **200** | OK | Login, listar, ver, actualizar, eliminar |
| **201** | Creado | Registrar usuario, crear ticket |
| **400** | Petición incorrecta | Correo ya registrado |
| **401** | No autenticado | Sin token, token vencido, login malo |
| **403** | Prohibido | Modificar o eliminar un ticket que no es tuyo |
| **404** | No encontrado | Ticket que no existe |
| **422** | Datos inválidos | Contraseña corta, correo malo, estado o prioridad no permitidos |

## 7. Guion para sustentar (3 minutos)

> "Mi proyecto es HelpDesk Lite, una API de soporte técnico hecha con FastAPI. Los usuarios, que pueden ser técnicos o empleados, se registran e inician sesión, y con la sesión iniciada gestionan tickets de soporte.
>
> Para la base de datos uso SQLAlchemy con SQLite. Las tablas no las creo con código: las creo con **migraciones de Alembic**. La primera migración crea las tablas `users` y `tickets` con una relación uno a muchos, porque un usuario puede tener muchos tickets; eso se hace con la llave foránea `owner_id`. La segunda migración modifica la tabla `tickets` para agregar el campo prioridad, con valores bajo, medio y alto, y por defecto medio.
>
> Para validar uso **Pydantic**, con schemas separados para crear, actualizar y responder. Valido que la contraseña tenga mínimo 8 caracteres, que el correo sea válido con `EmailStr`, y con `Literal` solo acepto los estados y prioridades permitidos. Si algo está mal, responde 422.
>
> Para la seguridad uso **OAuth2 con JWT**. La contraseña se guarda cifrada con bcrypt. Al iniciar sesión se genera un token que dura 30 minutos, y la dependencia `get_current_user` protege todos los endpoints de tickets: sin token responde 401.
>
> En los tickets, al crear uno se asocia automáticamente al usuario del token. El listado tiene paginación con `skip` y `limit` y un filtro opcional por estado. Si un ticket no existe responde 404, y solo el creador puede modificarlo o eliminarlo; si otro usuario lo intenta, responde 403."

Después, mostrar en Swagger los pasos 1 al 9.

## 8. Preguntas que te pueden hacer

**¿Dónde se genera el token?**
En `auth.py`, en la función `create_token()`. Se llama en el login (`main.py`).

**¿Cómo se protegen los endpoints?**
Con `Depends(get_current_user)`. Esa función lee el token y devuelve el usuario; si no hay token o no sirve, responde 401.

**¿Cómo se guarda la contraseña?**
Cifrada con bcrypt (`hash_password`). En el login no se descifra: se compara con `verify_password`.

**¿Qué es una migración?**
Un archivo que guarda un cambio en la base de datos, como un historial. Con `alembic upgrade head` se aplican todas en orden.

**¿Por qué la migración 2 usa `batch_alter_table`?**
Porque SQLite no permite modificar tablas directamente, y Alembic hace el cambio en "lote" para que funcione.

**¿Qué es la relación 1:N?**
Uno a muchos: un usuario tiene muchos tickets, y cada ticket es de un solo usuario. Se hace con `owner_id`, la llave foránea a `users.id`.

**¿Qué es la paginación?**
Traer los datos por partes. `skip` es cuántos saltar y `limit` cuántos traer. Ej: `skip=10&limit=10` trae la segunda página.

**¿Diferencia entre PATCH y PUT?**
PATCH actualiza **solo una parte** (por ejemplo, solo el estado). PUT reemplaza todo el registro.

**¿Por qué el `owner_id` no se manda al crear el ticket?**
Porque se toma del token. Así nadie puede crear tickets a nombre de otro.

**¿Diferencia entre 401 y 403?**
401 es "no sé quién eres" (no hay token). 403 es "sé quién eres, pero no tienes permiso" (el ticket no es tuyo).
