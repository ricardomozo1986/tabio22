import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np
# Importar MarkerCluster
from folium.plugins import MarkerCluster

st.set_page_config(layout="wide", page_title="Plataforma Predial Municipal")
st.title("📊 Plataforma de Análisis Predial Municipal")

@st.cache_data(ttl=3600)
def load_and_preprocess_data(uploaded_file_buffer):
    if uploaded_file_buffer is None:
        return pd.DataFrame()

    df = pd.read_excel(uploaded_file_buffer)
    df.columns = (
        df.columns.str.strip().str.lower()
        .str.replace(" ", "_")
        .str.replace("á", "a").str.replace("é", "e")
        .str.replace("í", "i").str.replace("ó", "o").str.replace("ú", "u")
        .str.replace("ñ", "n")
    )
    required_columns = [
        "valor_impuesto_a_pagar", "recaudo_predial", "pago_impuesto_predial",
        "avaluo_catastral", "descuentos_impuesto_predial", "sector",
        "sector_urbano", "vereda", "destino_economico_predio",
        "propiedad_horizontal", "latitud", "longitud", "codigo_igac",
        "area_construida", "financiacion_impuesto_predial"
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"El archivo Excel cargado no contiene las siguientes columnas requeridas: {', '.join(missing_columns)}. Por favor, asegúrese de que el archivo sea correcto.")
        st.stop()
        return pd.DataFrame()

    for col in ["valor_impuesto_a_pagar", "recaudo_predial", "avaluo_catastral",
                "descuentos_impuesto_predial", "latitud", "longitud", "area_construida"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['saldo'] = df['valor_impuesto_a_pagar'] - df['recaudo_predial']
    df['cumplimiento'] = df['pago_impuesto_predial'].astype(str).str.lower().isin(['si', 'sí'])
    return df

uploaded_file = st.file_uploader("Cargar archivo Excel con datos prediales", type=["xlsx"])
df = pd.DataFrame()
if uploaded_file:
    df = load_and_preprocess_data(uploaded_file)
else:
    st.info("Por favor, cargue un archivo Excel para comenzar el análisis.")

if not df.empty:
    with st.sidebar:
        st.header("Filtros Globales")
        sector_options = ["Todos"] + sorted(df["sector"].dropna().astype(str).unique().tolist())
        sector_urbano_options = ["Todos"] + sorted(df["sector_urbano"].dropna().astype(str).unique().tolist())
        vereda_options = ["Todas"] + sorted(df["vereda"].dropna().astype(str).unique().tolist())
        uso_options = ["Todos"] + sorted(df["destino_economico_predio"].dropna().astype(str).unique().tolist())

        sector = st.selectbox("Sector (urbano/rural)", sector_options)
        sector_urbano = st.selectbox("Sector Urbano", sector_urbano_options)
        vereda = st.selectbox("Vereda", vereda_options)
        uso = st.selectbox("Uso del predio", uso_options)
        ph = st.selectbox("Propiedad horizontal", ["Todos", "Sí", "No"])

    def aplicar_filtros(data):
        dff = data.copy()
        if sector != "Todos":
            dff = dff[dff["sector"].astype(str) == sector]
        if sector_urbano != "Todos":
            dff = dff[dff["sector_urbano"].astype(str) == sector_urbano]
        if vereda != "Todas":
            dff = dff[dff["vereda"].astype(str) == vereda]
        if uso != "Todos":
            dff = dff[dff["destino_economico_predio"].astype(str) == uso]
        if ph != "Todos":
            if 'propiedad_horizontal' in dff.columns:
                dff = dff[dff["propiedad_horizontal"].astype(str).str.lower() == ph.lower()]
        return dff

    df_filtrado = aplicar_filtros(df)

    if df_filtrado.empty:
        st.warning("Los filtros seleccionados no arrojaron ningún resultado. Por favor, ajuste los filtros.")
        pass
    else:
        tabs = st.tabs([
            "📊 Información General",
            "📌 Cumplimiento Tributario",
            "📉 Cartera Morosa",
            "🏗️ Oportunidades Catastrales",
            "💼 Estrategias de Cobro",
            "🔮 Simulación de Escenarios",
            "🗺️ Riesgo Geoespacial"
        ])

        with tabs[0]:
            st.subheader("📊 Información General")
            def resumen_tabla(df_sub):
                return {
                    "Número de predios": len(df_sub),
                    "Avalúo total": df_sub['avaluo_catastral'].sum(),
                    "Impuesto total": df_sub['valor_impuesto_a_pagar'].sum(),
                    "Recaudo total": df_sub['recaudo_predial'].sum(),
                    "Descuento total": df_sub['descuentos_impuesto_predial'].sum(),
                    "Saldo por pagar": df_sub['saldo'].sum()
                }
            total = resumen_tabla(df_filtrado)
            urbano = resumen_tabla(df_filtrado[df_filtrado['sector'].astype(str).str.upper() == 'URBANO'])
            rural = resumen_tabla(df_filtrado[df_filtrado['sector'].astype(str).str.upper() == 'RURAL'])
            resumen_df = pd.DataFrame([total, urbano, rural], index=["Total", "Urbano", "Rural"]).T
            format_mapping = {
                "Avalúo total": "${:,.0f}", "Impuesto total": "${:,.0f}",
                "Recaudo total": "${:,.0f}", "Descuento total": "${:,.0f}",
                "Saldo por pagar": "${:,.0f}"
            }
            try:
                st.dataframe(resumen_df.style.format(format_mapping))
            except Exception as e:
                st.warning(f"No se pudo aplicar formato de estilo a la tabla: {e}. Mostrando tabla sin formato.")
                st.dataframe(resumen_df)


        with tabs[1]:
            st.subheader("📌 Cumplimiento Tributario")
            pagados = df_filtrado[df_filtrado['cumplimiento'] == True]
            no_pagados = df_filtrado[df_filtrado['cumplimiento'] == False]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tasa de Cumplimiento", f"{len(pagados) / len(df_filtrado) * 100:.2f}%" if len(df_filtrado) > 0 else "0%")
            with col2:
                total_impuesto_facturado = df_filtrado['valor_impuesto_a_pagar'].sum()
                recaudo_porcentaje = f"{pagados['recaudo_predial'].sum() / total_impuesto_facturado * 100:.2f}%" if total_impuesto_facturado > 0 else "0%"
                st.metric("Recaudo / Facturado", recaudo_porcentaje)
            with col3:
                st.metric("Predios Pagados", f"{len(pagados):,}")

            if not df_filtrado.empty and not df_filtrado[['latitud', 'longitud']].isnull().all().all():
                map_center_lat = df_filtrado['latitud'].mean() if not df_filtrado['latitud'].isnull().all() else 4.710989
                map_center_lon = df_filtrado['longitud'].mean() if not df_filtrado['longitud'].isnull().all() else -74.072090
                m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=13)

                # Instanciar MarkerCluster para los predios pagados
                mc_pagados = MarkerCluster(name='Predios Pagados', control=False).add_to(m)
                for idx, row in pagados.iterrows():
                    if pd.notnull(row['latitud']) and pd.notnull(row['longitud']):
                        folium.CircleMarker(
                            location=[row['latitud'], row['longitud']],
                            radius=5,
                            color='green',
                            fill=True,
                            fill_opacity=0.6,
                            popup=f"IGAC: {row['codigo_igac']}\nPagado: ${row['recaudo_predial']:,.0f}"
                        ).add_to(mc_pagados) # Añadir al cluster

                # Instanciar MarkerCluster para los predios no pagados
                mc_no_pagados = MarkerCluster(name='Predios No Pagados', control=False).add_to(m)
                for idx, row in no_pagados.iterrows():
                    if pd.notnull(row['latitud']) and pd.notnull(row['longitud']):
                        folium.CircleMarker(
                            location=[row['latitud'], row['longitud']],
                            radius=5,
                            color='red',
                            fill=True,
                            fill_opacity=0.6,
                            popup=f"IGAC: {row['codigo_igac']}\nPendiente: ${row['valor_impuesto_a_pagar']:,.0f}"
                        ).add_to(mc_no_pagados) # Añadir al cluster

                folium.LayerControl().add_to(m) # Opcional: para activar/desactivar clusters
                st_folium(m, width=1000, height=500)
            else:
                st.warning("No hay datos de latitud/longitud para mostrar en el mapa de Cumplimiento Tributario o los datos filtrados están vacíos.")

            st.markdown("### Tabla de Predios que Pagaron")
            if not pagados.empty:
                pagados_display = pagados.copy()
                pagados_display["valor_impuesto_a_pagar"] = pd.to_numeric(pagados_display["valor_impuesto_a_pagar"], errors='coerce').fillna(0)
                pagados_display["recaudo_predial"] = pd.to_numeric(pagados_display["recaudo_predial"], errors='coerce').fillna(0)
                tabla_pagados = pagados_display.sort_values(by="recaudo_predial", ascending=False)[
                    ["codigo_igac", "vereda", "sector", "valor_impuesto_a_pagar", "recaudo_predial"]
                ]
                st.dataframe(tabla_pagados.reset_index(drop=True).style.format({"valor_impuesto_a_pagar": "${:,.0f}", "recaudo_predial": "${:,.0f}"}))
            else:
                st.info("No hay predios pagados para mostrar con los filtros actuales.")


        # ... (restante del código para las otras pestañas, aplicando MarkerCluster a los mapas si es necesario)
        # Por ejemplo, para la pestaña de Cartera Morosa:
        with tabs[2]:
            st.subheader("📉 Segmentación de Cartera Morosa")

            morosos = df_filtrado[df_filtrado['cumplimiento'] == False]

            st.markdown(f"**Número total de predios morosos:** {len(morosos):,}")
            st.markdown(f"**Valor total en mora:** ${morosos['valor_impuesto_a_pagar'].sum():,.0f}")

            if not morosos.empty and not morosos[['latitud', 'longitud']].isnull().all().all():
                map_center_mora = morosos['latitud'].mean() if not morosos['latitud'].isnull().all() else 4.710989
                map_center_lon_mora = morosos['longitud'].mean() if not morosos['longitud'].isnull().all() else -74.072090
                m_mora = folium.Map(location=[map_center_mora, map_center_lon_mora], zoom_start=13)
                
                # Usar MarkerCluster aquí también
                mc_morosos = MarkerCluster(name='Predios Morosos').add_to(m_mora)
                for idx, row in morosos.iterrows():
                    if pd.notnull(row['latitud']) and pd.notnull(row['longitud']):
                        folium.CircleMarker(
                            location=[row['latitud'], row['longitud']],
                            radius=5,
                            color='red',
                            fill=True,
                            fill_opacity=0.6,
                            popup=f"IGAC: {row['codigo_igac']}\nImpuesto: ${row['valor_impuesto_a_pagar']:,.0f}"
                        ).add_to(mc_morosos)
                st_folium(m_mora, width=1000, height=500)
            else:
                st.warning("No hay datos de latitud/longitud para mostrar en el mapa de Cartera Morosa o no hay predios morosos con los filtros actuales.")

            st.markdown("### Tabla de Predios Morosos")
            if not morosos.empty:
                morosos_display = morosos.copy()
                morosos_display["avaluo_catastral"] = pd.to_numeric(morosos_display["avaluo_catastral"], errors='coerce').fillna(0)
                morosos_display["valor_impuesto_a_pagar"] = pd.to_numeric(morosos_display["valor_impuesto_a_pagar"], errors='coerce').fillna(0)

                tabla_morosos = morosos_display[
                    ["codigo_igac", "vereda", "sector", "destino_economico_predio", "avaluo_catastral", "valor_impuesto_a_pagar", "area_construida"]
                ]
                st.dataframe(tabla_morosos.reset_index(drop=True).style.format({"avaluo_catastral": "${:,.0f}", "valor_impuesto_a_pagar": "${:,.0f}"}))
            else:
                st.info("No hay predios morosos para mostrar con los filtros actuales.")

        # ... (Continuar aplicando MarkerCluster a los demás mapas si es necesario)
