# 📊 Plataforma de Análisis Predial Municipal

Este repositorio contiene una aplicación web interactiva desarrollada en Python con Streamlit para el análisis de datos prediales municipales. La aplicación permite cargar archivos Excel con información predial, aplicar filtros y visualizar métricas clave, mapas interactivos y tablas segmentadas para la gestión tributaria y catastral.

## Características Principales

* **Carga de Datos Flexible:** Permite cargar archivos Excel (`.xlsx`) con datos prediales.
* **Filtros Interactivos:** Filtra los datos por sector (urbano/rural), sector urbano específico, vereda, uso del predio y propiedad horizontal.
* **Módulos de Análisis:**
    * **Información General:** Resumen consolidado de métricas prediales.
    * **Cumplimiento Tributario:** Análisis de predios pagados y no pagados, con visualización geográfica.
    * **Cartera Morosa:** Segmentación y visualización de predios en mora.
    * **Oportunidades Catastrales:** Identificación de predios con potencial de actualización catastral.
    * **Estrategias de Cobro:** Focalización de predios de alto valor en mora para campañas de cobro.
    * **Simulación de Escenarios:** Proyección de recaudo bajo diferentes coberturas.
    * **Riesgo Geoespacial:** Mapa de riesgo tributario basado en factores fiscales, catastrales y comportamentales.
* **Mapas Interactivos:** Utiliza Folium para visualizar la distribución geográfica de los predios.
* **Tablas Detalladas:** Muestra los datos relevantes en formato tabular.

## Requisitos

Para ejecutar esta aplicación localmente, necesitarás tener Python instalado (se recomienda Python 3.8 o superior).

Las dependencias necesarias se listan en el archivo `requirements.txt`.

## Instalación Local

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/nombre-de-tu-repo.git](https://github.com/tu-usuario/nombre-de-tu-repo.git)
    cd nombre-de-tu-repo
    ```
    (Reemplaza `tu-usuario/nombre-de-tu-repo` con la ruta real de tu repositorio en GitHub).

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación Streamlit:**
    ```bash
    streamlit run app_streamlit_predial.py
    ```
    Esto abrirá la aplicación en tu navegador web por defecto.

## Despliegue en Streamlit Cloud

Streamlit Cloud detectará automáticamente el archivo `requirements.txt` y lo usará para instalar las dependencias.

Para desplegar tu aplicación:

1.  Asegúrate de que tu aplicación (`app_streamlit_predial.py`) y el archivo `requirements.txt` estén en la raíz de tu repositorio de GitHub.
2.  Ve a [Streamlit Cloud](https://share.streamlit.io/).
3.  Haz clic en "New app" o "Deploy an app".
4.  Selecciona tu repositorio de GitHub y la rama donde se encuentra tu código.
5.  Asegúrate de que "Main file path" sea `app_streamlit_predial.py`.
6.  Haz clic en "Deploy!".

Streamlit Cloud se encargará de instalar las dependencias y publicar tu aplicación.

## Estructura del Proyecto