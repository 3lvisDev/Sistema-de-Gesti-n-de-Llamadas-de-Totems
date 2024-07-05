
### Proyecto: Sistema de Gestión de Llamadas de Totems

Este proyecto consiste en un sistema para gestionar llamadas de totems mediante una interfaz cliente, un servidor intermedio y una Raspberry Pi que actúa como intermediaria. Está diseñado para un entorno de seguridad donde los totems pueden enviar señales al servidor y los clientes pueden aceptar y gestionar estas señales.

#### Estructura del Proyecto

1. **cliente_au.py**: Archivo que contiene la lógica del cliente.
2. **interfaz_ui.py**: Archivo que define la interfaz de usuario.
3. **main.py**: Archivo principal que inicializa y ejecuta la aplicación.
4. **Servicio_VAS_Reinicio.py**: Archivo que contiene el servicio Flask para gestionar las señales de los totems.
5. **imput_envio.py**: Archivo para gestionar el envío de señales desde la Raspberry Pi.

#### Requisitos

Para ejecutar este proyecto, necesitas tener instalado lo siguiente:

- **Python 3.8 o superior**
- **Flask**: Para gestionar el servidor.
- **RPi.GPIO**: Para manejar los pines GPIO de la Raspberry Pi.
- **requests**: Para enviar solicitudes HTTP.
- **PyQt5**: Para la interfaz gráfica de usuario.

#### Instalación

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/3lvisDev/Sistema-de-Gesti-n-de-Llamadas-de-Totems.git
   ```

2. **Crear un entorno virtual**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts ctivate`
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

#### Ejecución

1. **Iniciar el servidor Flask**

   ```bash
   python Servicio_VAS_Reinicio.py
   ```

2. **Ejecutar la interfaz de usuario**

   ```bash
   python main.py
   ```

3. **Configurar la Raspberry Pi**

   Asegúrate de que la Raspberry Pi esté configurada correctamente para manejar los pines GPIO y enviar las señales HTTP al servidor Flask.

#### Uso

- **Cliente**: La interfaz de usuario permite aceptar y gestionar las llamadas desde los totems.
- **Totems**: Al presionar el botón en un totem, se envía una señal HTTP al servidor, que luego notifica al cliente para gestionar la llamada.

#### Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para cualquier cambio o mejora que desees proponer.

#### Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

#### Contacto

Para cualquier consulta o soporte, por favor contacta a [tu_email@dominio.com](mailto:xxelvisdsxx@gmail.com).

---

A continuación, el contenido del archivo `requirements.txt` necesario para la instalación de las dependencias:

```
Flask>=2.0.0
RPi.GPIO
requests
PyQt5
```
