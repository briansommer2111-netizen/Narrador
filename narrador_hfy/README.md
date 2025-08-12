# Narrador de Historias HFY 🤖

Este proyecto es una aplicación completa para automatizar la creación de videos de narración a partir de historias del subreddit r/HFY, traducidas al español, con voces de múltiples personajes generadas por IA.

## ✨ Características

-   **Extracción Automática:** Obtiene historias directamente desde una URL de Reddit.
-   **Traducción Local:** Traduce de inglés a español usando modelos de IA locales (sin APIs de pago).
-   **Análisis de Diálogos:** Identifica automáticamente personajes y diálogos.
-   **Síntesis de Voz Multi-personaje:** Utiliza Coqui XTTSv2 para clonar voces y dar una voz única a cada personaje.
-   **Creación de Video:** Genera un archivo de video MP4 con el audio y subtítulos sobre una imagen de fondo.
-   **Interfaz Gráfica:** Un asistente paso a paso creado con Streamlit guía al usuario en todo el proceso.

## ⚙️ Instalación

**Requisitos Previos:**
-   Python 3.10+
-   Git
-   FFmpeg (debe estar instalado y accesible en el PATH del sistema).

**Pasos:**

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu_usuario/narrador_hfy.git
    cd narrador_hfy
    ```

2.  **Instalar dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Descargar modelo de lenguaje para español:**
    ```bash
    python -m spacy download es_core_news_md
    ```

4.  **Descarga de Modelos de IA:** La primera vez que ejecutes la aplicación, se descargarán los modelos de traducción y de síntesis de voz (~2.5 GB). Esto requiere una conexión a internet.

## 🚀 Uso

1.  **Configura tus voces:** Añade archivos `.wav` de 5-10 segundos en la carpeta `data/voice_bank/`. El nombre del archivo (sin extensión) será el nombre del "arquetipo de voz" que verás en la UI (ej. `heroina.wav`).

2.  **Inicia la aplicación:**
    ```bash
    streamlit run main.py
    ```

3.  Abre tu navegador en la dirección que indique Streamlit (normalmente `http://localhost:8501`) y sigue los pasos del asistente.

## 🔧 Empaquetado

Para crear un ejecutable autocontenido para Windows/Linux, puedes usar el script de `build.py`.

```bash
pip install pyinstaller
python build.py
```
El ejecutable se encontrará en la carpeta `dist/`.

## ⚠️ Solución de Problemas

-   **Error `ffmpeg not found`**: Asegúrate de que FFmpeg está instalado y que su directorio `bin` está en la variable de entorno `PATH` de tu sistema.
-   **Error `CUDA out of memory`**: El proceso de síntesis de voz o de IA de video consume mucha VRAM. Cierra otras aplicaciones que usen la GPU. Si el error persiste, tu GPU puede no tener suficiente memoria para los modelos por defecto.
-   **La aplicación es lenta la primera vez**: Es normal. Se están descargando y cargando en memoria los modelos de IA. Las ejecuciones posteriores serán más rápidas.
