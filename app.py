import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración
st.set_page_config(page_title="Tablero de Control Histórico", layout="wide")

PATH = r'data'  # Cambia esta ruta a la ubicación de tus archivos CSV (data es relativo al directorio del proyecto)
FILE_EXPEDIENTES = os.path.join(PATH, '20180101-20260312_3_exptes_pagados_unificado_datos_admin_tiempo_circuito_2026-03-12.csv') 
FILE_EFECTORES = os.path.join(PATH, 'DB_Efectores_Sumar.csv')

@st.cache_data
def load_data():
    df = pd.read_csv(FILE_EXPEDIENTES, sep=';', encoding='latin-1')
    df_efectores = pd.read_csv(FILE_EFECTORES, sep=';', encoding='latin-1')
    
    # 1. Limpieza de Período y Creación de Filtros Temporales
    df['periodo_dt'] = pd.to_datetime(df['periodo'], errors='coerce')
    df['Año'] = df['periodo_dt'].dt.year.fillna(0).astype(int)
    df['Mes'] = df['periodo_dt'].dt.month.fillna(0).astype(int)
    
    # 2. Merge con datos de efectores
    # Nota: Asegurate que 'LOCALIDAD' venga de df_efectores
    df_final = pd.merge(df, df_efectores, left_on='cuieadmin', right_on='CUIE', how='left')

    # --- PREPARACIÓN DE COLUMNA DE DISPLAY ---
    # La creamos directamente en df_final que es lo que devolvemos
    df_final['efector_display'] = df_final['efectoradmin'] + " (" + df_final['LOCALIDAD'].fillna("Sin Localidad") + ")"
    
    # 3. Conversión de columnas de días a numérico
    cols_dias = [
        'diaslabcreaexpte', 'diasiniciocreacionexpte', 'diaslabliqefect',
        'diaslabop', 'diaslabpagobanco', 'diastotalcreacionexptepago', 'diastotalfinperiodo'
    ]
    for col in cols_dias:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
        
    return df_final

# --- CARGA DE DATOS ---
df_raw = load_data()

# --- PREPARACIÓN DE LISTA PARA EL FILTRO ---
# Esto tiene que estar afuera de la función para que el multiselect lo vea
lista_efectores = sorted(df_raw['efector_display'].unique())

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("⚙️ Controles del Tablero")

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Filtros Temporales")

# Filtro de Año
años_disponibles = sorted(df_raw['Año'].unique(), reverse=True)
años_sel = st.sidebar.multiselect("Años", options=años_disponibles, default=[2025, 2024])

# Filtro de Mes
meses_nombres = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 
                  7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
meses_sel = st.sidebar.multiselect("Meses", options=list(meses_nombres.keys()), 
                                    format_func=lambda x: meses_nombres[x])

st.sidebar.subheader("🏥 Filtros de Gestión")

# Ahora 'lista_efectores' ya es visible aquí
efector_seleccionado = st.sidebar.multiselect(
    "Seleccionar Efector:",
    options=lista_efectores,
    default=None
)

# Botón de Reset
if st.sidebar.button("♻️ Resetear Filtros"):
    st.rerun()

# --- APLICACIÓN DE FILTROS ---
df_filtrado = df_raw.copy()
if años_sel:
    df_filtrado = df_filtrado[df_filtrado['Año'].isin(años_sel)]
if meses_sel:
    df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_sel)]
if efector_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['efector_display'].isin(efector_seleccionado)]


# --- CUERPO DEL TABLERO ---
st.title("📊 Circuito Administrativo de las Prestaciones Facturadas 2018 - 2025")

# Verificamos si hay datos tras aplicar los filtros para evitar errores
if not df_filtrado.empty:
    
    # --- GRÁFICO DE BARRAS FINAL CON EJE CATEGÓRICO ---
    st.subheader("⏳ Composición del Tiempo por Período desde que finaliza un mes calendario")

    # 1. Agrupamos usando df_filtrado
    df_acum = df_filtrado.groupby('periodo').agg({
        'diaslabcreaexpte': 'mean',
        'diaslabliqefect': 'mean',
        'diaslabpagobanco': 'mean',
        'periodo_dt': 'first' 
    }).reset_index().sort_values('periodo_dt')

    promedio_historico = df_acum['diaslabpagobanco'].mean()

    # MAPEO MANUAL A ESPAÑOL
    meses_es = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }

    # Creamos la etiqueta: "Ene 2024"
    df_acum['periodo_texto'] = df_acum['periodo_dt'].dt.month.map(meses_es) + " " + df_acum['periodo_dt'].dt.year.astype(str)
    
    # 2. Definiciones de Estilo
    nombres_leyenda = {
        'diaslabcreaexpte': '1. Presentación',
        'diaslabliqefect': '2. Auditoría',
        'diaslabpagobanco': '3. Pago Banco'
    }

    colores = {
        '1. Presentación': '#5DADE2', 
        '2. Auditoría': '#A569BD', # Cambiado a Morado como pediste
        '3. Pago Banco': '#E74C3C'          
    }

    # 3. Creación del gráfico
    fig_barras = px.bar(df_acum, 
                        x='periodo_texto', 
                        y=['diaslabpagobanco', 'diaslabliqefect', 'diaslabcreaexpte'], 
                        barmode='overlay',
                        title="Hitos de Gestión Acumulados por Mes")

    for trace in fig_barras.data:
        nombre_real = nombres_leyenda.get(trace.name, trace.name)
        trace.name = nombre_real
        if nombre_real in colores:
            trace.marker.color = colores[nombre_real]
            trace.marker.line.width = 0 

    fig_barras.add_hline(
        y=promedio_historico, 
        line_dash="dash", 
        line_color="#F1C40F", 
        line_width=3,
        annotation_text=f" 💡 PROMEDIO: {promedio_historico:.1f} DÍAS ", 
        annotation_position="top right",
        annotation_font_color="white",
        annotation_bgcolor="#34495E", 
    )

    fig_barras.update_layout(
        xaxis_type='category',
        xaxis_tickangle=-45,
        yaxis_title="Días acumulados desde fin de período",
        legend_title="Etapas del Circuito",
        hovermode="x unified",
        bargap=0.4,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=100, l=50, r=50)
    )

    fig_barras.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)')
    st.plotly_chart(fig_barras, use_container_width=True)

    # --- LEYENDA EXPLICATIVA ---
    with st.expander("ℹ️ ¿Cómo se leen estas barras? (Metodología de medición)", expanded=False):
        st.markdown("""
        Cada barra representa el **tiempo total acumulado** desde el último día del período facturado hasta alcanzar un hito:
        * 🔵 **Azul (Presentación):** Días totales hasta la fecha de creación del expediente en el sistema.
        * 🟣 **Morado (Auditoría):** Días totales hasta que finaliza la liquidación (prestaciones finales listas para CEB, SIRGE, etc.).
        * 🔴 **Rojo (Pago):** Días totales hasta el movimiento bancario final.
        """)

    # Columnas de KPI usando df_filtrado
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Promedio Auditoría", f"{df_filtrado['diaslabliqefect'].mean():.1f} días")
    with c2:
        st.metric("Promedio Pago", f"{df_filtrado['diaslabpagobanco'].mean():.1f} días")
    with c3:
        st.metric("Total Expedientes", len(df_filtrado))

    # --- TOP 15 EFECTORES ---
    st.subheader("⚠️ Top 15 Efectores con Mayor Tiempo de Proceso Interno")
    
    # Usamos la columna 'efector_display' que tiene Nombre (Localidad)
    df_top_delay = df_filtrado.groupby('efector_display')['diastotalcreacionexptepago'].mean().sort_values(ascending=False).head(15).reset_index()

    fig_delay = px.bar(df_top_delay, 
                       x='diastotalcreacionexptepago', 
                       y='efector_display', 
                       orientation='h', 
                       color='diastotalcreacionexptepago',
                       color_continuous_scale='Reds',
                       text_auto='.1f',
                       labels={'diastotalcreacionexptepago': 'Días Promedio', 'efector_display': 'Efector'})

    fig_delay.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
    st.plotly_chart(fig_delay, use_container_width=True)

else:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Por favor, ajusta los Años, Meses o Efectores.")
