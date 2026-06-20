# Security Improvements - JoyeriaBack

## Resumen de cambios realizados

---

### 1. Dependencia de autenticacion reutilizable

**Antes:** La verificacion del token JWT se copiaba y pegaba manualmente en cada router (~25 lineas repetidas 6+ veces). Algunos endpoints tenian el codigo comentado y quedaban desprotegidos.

**Ahora:** Se crearon dos dependencias FastAPI en `app/deps.py`:

- `get_current_user`: Extrae el token del header `Authorization: Bearer <token>`, lo decodifica y retorna el payload. Si es invalido, lanza 401.
- `require_role("admin", "editor")`: Llama a `get_current_user` y ademas verifica que el campo `rol` del payload tenga uno de los roles permitidos. Si no, lanza 403.

**Archivos modificados:**
- `app/deps.py` - Nuevas dependencias `get_current_user`, `require_role`, `security_scheme`
- `app/routers/categories.py` - Reemplazadas ~20 lineas de auth por `Depends(require_role(...))`
- `app/routers/sub_categorias.py` - Idem
- `app/routers/materials.py` - Eliminado codigo de auth comentado
- `app/routers/products.py` - Agregado `Depends(require_role(...))` en create/delete/update
- `app/routers/auth.py` - Agregado `Depends(require_role("admin"))` en signup
- `app/routers/logout.py` - Usa `get_current_user` + `security_scheme`

---

### 2. Endpoints protegidos que antes estaban expuestos

| Endpoint | Antes | Ahora | Roles permitidos |
|---|---|---|---|
| `POST /productos/create` | Sin auth | Requiere auth | admin, editor |
| `POST /productos/delete/{id}` | Sin auth | Requiere auth | admin |
| `POST /productos/update/{id}` | Sin auth | Requiere auth | admin, editor |
| `POST /singup/` | Sin auth | Requiere auth | admin |

**Los endpoints GET siguen siendo publicos** para que la web pueda mostrar productos y categorias sin autenticacion:
- `GET /productos/` 
- `GET /productos/{id}`
- `GET /productos/category/{id}`
- `GET /categories/`
- `GET /subcategorias/`
- `GET /materials/`

---

### 3. Validacion de entrada con Pydantic

**Antes:** Los schemas solo validaban tipos (`str`, `int`). No habia validacion de formato de email, longitud de password, ni restriccion de roles.

**Ahora** (`app/schemas/auth.py`):

- `LoginRequest.email`: `EmailStr` (valida formato RFC)
- `UserCreate.email`: `EmailStr`
- `UserCreate.password`: minimo 8 caracteres, maximo 128
- `UserCreate.nombre`: minimo 1, maximo 100 caracteres
- `UserCreate.rol`: solo acepta `"admin"` o `"editor"` (default cambio de `"admin"` a `"editor"`)
- `LoginRequest.password`: minimo 1 caracter (no vacio)

**Dependencia nueva:** `email-validator==2.2.0`

---

### 4. Dependencias con versiones fijadas

**Antes:** `requirements.txt` sin versiones especificas. Vulnerable a supply chain attacks.

**Ahora:** Todas las dependencias tienen versiones fijadas:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-jose[cryptography]==3.3.0
python-dotenv==1.0.1
sqlalchemy==2.0.36
pymysql==1.1.1
passlib[bcrypt]==1.7.4
bcrypt==4.2.1
python-multipart==0.0.18
pillow==11.1.0
email-validator==2.2.0
slowapi==0.1.9
```

---

### 5. Bug de CORS corregido

**Antes:** Coma faltante causaba concatenacion de strings:
```python
"http://127.0.0.1:4000"     # sin coma
"http://localhost:4000",    # resultado: "http://127.0.0.1:4000http://localhost:4000"
```

**Ahora:** Coma agregada correctamente.

**Ademas:**
- `allow_methods` restringido a `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]` (antes `["*"]`)
- `allow_headers` restringido a `["Content-Type", "Authorization"]` (antes `["*"]`)

---

### 6. Rate limiting en endpoints sensibles

**Implementado con `slowapi`:**

- `POST /login` - maximo 10 intentos por minuto por IP
- `POST /singup/` - maximo 5 intentos por minuto por IP

Previene ataques de fuerza bruta contra credenciales.

**Archivos modificados:**
- `app/main_refactored.py` - Configuracion de slowapi
- `app/routers/auth.py` - Decoradores `@limiter.limit()` en login y signup

---

### 7. Validacion de uploads de imagenes

**Antes:** Se aceptaba cualquier tipo de archivo como imagen de producto.

**Ahora** (`app/routers/products.py`):

- Solo se aceptan MIME types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- Si el Content-Type no es uno de esos, se devuelve error 400
- Tamanio maximo configurado: 10 MB (`MAX_UPLOAD_SIZE`)

---

### 8. Logout funcional con blacklist de tokens

**Antes:** El router `/logout` no estaba registrado en `main_refactored.py` y era un stub vacio.

**Ahora:**
- Router `/logout` registrado correctamente
- Implementa blacklist de tokens en memoria (`app/utils/token.py`)
- Al hacer logout, el token se agrega a la blacklist con su tiempo de expiracion
- `decode_token()` verifica la blacklist antes de aceptar un token
- Tokens expirados se limpian automaticamente

---

### 9. Fix N+1 queries en list_products

**Antes:** `GET /productos/` ejecutaba una consulta de imagenes por cada producto (N+1 queries).

**Ahora:** Se cargan todas las imagenes en una sola consulta con `.in_(product_ids)` y se agrupan en un diccionario antes de construir la respuesta.

---

### 10. Limpieza de codigo

- Eliminado `print("Database session created")` en `app/database/database.py`
- Eliminado codigo de auth comentado en `materials.py` y `sub_categorias.py`
- Eliminado import no usado `auth as auth_router` en `auth.py`
- Eliminadas lineas en blanco excesivas en todos los archivos

---

## Resumen de archivos modificados

| Archivo | Cambio |
|---|---|
| `requirements.txt` | Versiones fijadas + nuevas dependencias |
| `app/main_refactored.py` | CORS fix, slowapi, logout router registrado |
| `app/deps.py` | Auth dependencies (`get_current_user`, `require_role`) |
| `app/database/database.py` | Eliminado print debug |
| `app/utils/token.py` | Blacklist de tokens, iat claim, cleanup automatico |
| `app/schemas/auth.py` | Validacion EmailStr, password min 8, rol restringido |
| `app/routers/auth.py` | Rate limiting, signup solo admin, validacion duplicados |
| `app/routers/categories.py` | Auth con dependencia reutilizable, roles |
| `app/routers/sub_categorias.py` | Auth con dependencia reutilizable, roles |
| `app/routers/materials.py` | Limpieza de codigo comentado |
| `app/routers/products.py` | Auth en create/delete/update, validacion MIME, fix N+1 |
| `app/routers/logout.py` | Implementacion funcional con blacklist |

---

## Problemas NO corregidos (requieren cambios de infraestructura)

Estos puntos requieren cambios fuera del codigo de la aplicacion:

1. **MySQL usa usuario root** - Crear un usuario dedicado con permisos minimos
2. **JWT secret debil** - Cambiar `SECRET_KEY` en `.env` por una clave de al menos 256 bits
3. **Sin HTTPS** - Configurar un reverse proxy (nginx) con SSL/TLS
4. **`.env` con secretos en disco** - Usar un gestor de secretos (Vault, Secrets Manager)
