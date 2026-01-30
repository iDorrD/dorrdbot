# 🤖 DorrdBOT

Un bot de Discord completamente funcional con estructura modular y soporte para múltiples eventos.

## 📋 Características

- ✅ Mensaje de bienvenida automático cuando un usuario se une al servidor
- ✅ Webhook con color personalizado (#8970ff)
- ✅ Estructura modular de carpetas para fácil mantenimiento
- ✅ Sistema de intents para mejor rendimiento
- ✅ Cargador automático de módulos (cogs)

## 📁 Estructura del Proyecto

```
DorrdBOT/
├── main.py                 # Archivo principal del bot
├── requirements.txt        # Dependencias de Python
├── .env.example           # Ejemplo de variables de entorno
├── README.md              # Este archivo
├── config/
│   └── config.py          # Configuración del bot
├── events/
│   └── welcome.py         # Evento de bienvenida
└── cogs/                  # Lugar para agregar módulos personalizados
```

## 🚀 Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd DorrdBOT
   ```

2. **Crear un ambiente virtual (opcional pero recomendado)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar el token del bot**
   - Renombra `.env.example` a `.env`
   - Añade tu token de Discord:
     ```
     DISCORD_TOKEN=tu_token_aqui
     ```

## 📝 Uso

Para iniciar el bot:

```bash
python main.py
```

Deberías ver algo como:
```
✅ DorrdBOT conectado como DorrdBOT#0000
📊 Bot en 1 servidor(es)
✅ Eventos cargados exitosamente
```

## ⚙️ Configuración Personalizada

Edita `config/config.py` para cambiar:
- **WELCOME_CHANNEL_ID**: ID del canal donde se enviarán los mensajes de bienvenida
- **WEBHOOK_COLOR**: Color del embed (en formato hexadecimal)
- **BOT_PREFIX**: Prefijo para los comandos

## 🔧 Agregar Nuevos Módulos

1. Crea un nuevo archivo `.py` en la carpeta `cogs/`
2. Define tu cog heredando de `commands.Cog`
3. El sistema cargará automáticamente el módulo

Ejemplo (`cogs/micomando.py`):
```python
from discord.ext import commands

class MiComando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def hola(self, ctx):
        await ctx.send("¡Hola!")

async def setup(bot):
    await bot.add_cog(MiComando(bot))
```

## 🛡️ Permisos Necesarios

Asegúrate de que el bot tiene los siguientes permisos en tu servidor:
- Ver canales
- Enviar mensajes
- Incrustar enlaces
- Cambiar presencia
- Leer historial de mensajes

## 📚 Recursos

- [Documentación de discord.py](https://discordpy.readthedocs.io/)
- [Portal de Desarrolladores de Discord](https://discord.com/developers)

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**¡Disfruta tu bot!** 🎉
