import PyInstaller.__main__
import os
import platform

# Nombre del ejecutable final
app_name = "NarradorHFY"
# Script principal de la aplicación
main_script = "main.py"

# Construir el comando de PyInstaller
pyinstaller_args = [
    main_script,
    '--onefile',
    f'--name={app_name}',
    # Añadir la configuración y la carpeta de assets por defecto
    f'--add-data={os.path.join("config.yaml", ".")}',
]

# Ocultar la consola solo en Windows
if platform.system() == "Windows":
    pyinstaller_args.append('--noconsole')

print(f"Ejecutando PyInstaller con los siguientes argumentos: {pyinstaller_args}")

PyInstaller.__main__.run(pyinstaller_args)

print(f"\n¡Empaquetado completado! Busca el ejecutable en la carpeta 'dist/{app_name}'.")
