import discord
from discord.ext import commands
import os
from config.config import TOKEN, BOT_PREFIX, BOT_NAME
from events.welcome import setup_welcome_event

# Crear el bot con intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Importante para recibir eventos de miembros
intents.voice_states = True  # Importante para recibir eventos de voz

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    """Se ejecuta cuando el bot se conecta correctamente"""
    print(f"✅ {BOT_NAME} conectado como {bot.user}")
    print(f"📊 Bot en {len(bot.guilds)} servidor(es)")
    
    # Sincronizar los slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) slash sincronizado(s)")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos slash: {e}")
    
    # Cambiar el estado del bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="a los nuevos miembros 👀"
        )
    )

async def load_events():
    """Cargar todos los eventos del bot"""
    await setup_welcome_event(bot)
    print("✅ Eventos cargados exitosamente")

async def load_cogs():
    """Cargar todos los cogs (módulos) del bot"""
    cogs_dir = "cogs"
    
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ Cog cargado: {filename}")
                except Exception as e:
                    print(f"❌ Error cargando cog {filename}: {e}")

async def main():
    """Función principal para iniciar el bot"""
    async with bot:
        # Cargar eventos
        await load_events()
        
        # Cargar cogs
        await load_cogs()
        
        # Iniciar el bot
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
