# Novel-to-Radioplay AI Pipeline

Este proyecto es un sistema open-source para convertir capítulos de novelas en narraciones de estilo radioteatro y, eventualmente, en videos animados.

## Arquitectura

El proyecto está dividido en los siguientes módulos:

- `orchestrator/`: Orquesta el flujo de trabajo completo.
- `ingest/`: Maneja la carga de los capítulos de texto.
- `script_generator/`: Convierte el texto plano a un formato de guion.
- `voice_engine/`: Genera el audio multi-voz usando TTS.
- `image_engine/`: Crea imágenes consistentes para escenas y personajes.
- `media_assembler/`: Ensambla el audio, imágenes y subtítulos.
- `memory_db/`: Mantiene una base de datos persistente de personajes, escenas y assets.
- `validation/`: Realiza chequeos de calidad sobre los medios generados.
- `web_ui/`: (Opcional) Una interfaz para la revisión humana.
- `docs/`: Documentación del proyecto.

Este proyecto está siendo desarrollado por Jules, un asistente de IA.
