# 📊 Tablero de Control — Circuito Administrativo de Prestaciones Facturadas

Aplicación interactiva desarrollada con **Streamlit** y **Plotly** para el análisis histórico del circuito administrativo de expedientes de prestaciones facturadas, desde la presentación hasta el pago bancario.

---

## 🗂 Estructura del Proyecto

```
proyecto/
├── app.py                  # Script principal del tablero
├── data/
│   ├── 20180101-20260312_3_exptes_pagados_unificado_datos_admin_tiempo_circuito_2026-03-12.csv
│   └── DB_Efectores_Sumar.csv
└── README.md
```

---

## ⚙️ Requisitos

- Python 3.9+
- Las siguientes librerías Python:

```bash
pip install streamlit pandas plotly
```

---

## 🚀 Cómo ejecutar

```bash
streamlit run app.py
```

---

## 📁 Archivos de datos necesarios

Deben estar ubicados dentro de la carpeta `data/` en el mismo directorio que `app.py`.

### `20180101-..._tiempo_circuito_....csv`
Archivo principal con los expedientes de prestaciones pagadas. Separador: `;`, encoding: `latin-1`.

Columnas clave utilizadas:

| Columna | Descripción |
|---|---|
| `periodo` | Período facturado (formato fecha) |
| `cuieadmin` | Código CUIE del efector |
| `efectoradmin` | Nombre del efector |
| `diascreaexpte` | Días desde fin de período hasta creación del expediente |
| `diasliqefect` | Días desde fin de período hasta liquidación del expediente |
| `diaspagobanco` | Días desde fin de período hasta el pago bancario |

### `DB_Efectores_Sumar.csv`
Tabla de referencia de efectores. Separador: `;`, encoding: `latin-1`.

Columnas clave:

| Columna | Descripción |
|---|---|
| `CUIE` | Código único del efector (clave de join) |
| `LOCALIDAD` | Localidad del efector |

---

## 📐 Metodología de medición

Todas las columnas de días se miden desde el **último día del mes facturado** como punto de origen común:

```
Fin del mes facturado
│
├──────────────────────────┤  diascreaexpte   → Presentación
│
├──────────────────────────────────────────────┤  diasliqefect   → Auditoría
│
├─────────────────────────────────────────────────────────────────┤  diaspagobanco  → Pago Banco
```

El **gráfico de efectores** muestra únicamente el **tiempo de gestión interna**, es decir desde la creación del expediente hasta el pago, descomponiendo en dos tramos:

- **Tramo Auditoría** = `diasliqefect` − `diascreaexpte`
- **Tramo Pago** = `diaspagobanco` − `diasliqefect`

---

## 🖥 Funcionalidades del Tablero

### Filtros (barra lateral)
- **Años**: selección múltiple, por defecto 2024 y 2025
- **Meses**: selección múltiple (nombres en español)
- **Efector**: selección múltiple por nombre y localidad
- **Resetear Filtros**: recarga la app con los valores por defecto

### Gráfico 1 — Hitos de Gestión Acumulados por Mes
Gráfico de barras verticales en modo `overlay` que muestra los tres hitos acumulados por período:
- 🔵 **1. Presentación** — creación del expediente
- 🟣 **2. Auditoría** — liquidación del expediente
- 🔴 **3. Pago Banco** — movimiento bancario final

Incluye línea de referencia con el **promedio histórico** del tiempo hasta pago.

### KPIs
- Promedio de días hasta Auditoría
- Promedio de días hasta Pago
- Total de expedientes en el período filtrado

### Gráfico 2 — Top 15 Efectores con Mayor Tiempo de Proceso Interno
Gráfico de barras horizontales apiladas, ordenado de mayor a menor por tiempo total de gestión interna (desde creación del expediente hasta pago). Cada barra muestra:
- 🟣 **2. Auditoría**: días entre creación y liquidación
- 🔴 **3. Pago Banco**: días entre liquidación y pago bancario

Al pasar el mouse sobre cada barra se muestran los valores detallados de cada tramo y el total.

---

## 🎨 Paleta de colores

| Etapa | Color | Hex |
|---|---|---|
| 1. Presentación | Azul | `#5DADE2` |
| 2. Auditoría | Morado | `#A569BD` |
| 3. Pago Banco | Rojo | `#E74C3C` |

---

## 📝 Notas técnicas

- Los datos se cargan con `@st.cache_data` para evitar recargas innecesarias.
- El orden del eje Y en el gráfico de efectores se fuerza explícitamente con `categoryarray` para garantizar el orden descendente correcto independientemente del comportamiento interno de Plotly.
