# Configuración del Bot DorrdBOT
import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot
TOKEN = os.getenv("DISCORD_TOKEN")

# ID del canal de bienvenida
WELCOME_CHANNEL_ID = 1466586670861127796

# ID del rol a asignar a nuevos miembros
WELCOME_ROLE_ID = 1466762477374013532

# ID del canal para leer normas/información (a mencionar en DM)
INFO_CHANNEL_ID = 1466584166647992321

# Color del webhook (en formato decimal)
WEBHOOK_COLOR = 0x8970ff

# Nombre del bot
BOT_PREFIX = "!"
BOT_NAME = "DorrdBOT"

# IDs para canales temporales de voz
TEMP_VOICE_TRIGGER_CHANNEL_ID = 1466599127252205672  # Canal que dispara la creación
TEMP_VOICE_CATEGORY_ID = 1466598747101462850  # Categoría donde se crean los canales temporales

# ID del canal de tickets de soporte
TICKETS_CHANNEL_ID = 1466773527129751634

# ID de la categoría para los tickets
TICKETS_CATEGORY_ID = 1466773459517440115

# ID del canal de administración para valoraciones de tickets
TICKETS_ADMIN_CHANNEL_ID = 1466780909985464380
# ID del canal para webhooks de sanciones (bans, kicks, temporary bans)
MODERATION_LOG_CHANNEL_ID = 1466781522605641863

# Color del webhook para sanciones (rojo claro)
MODERATION_WEBHOOK_COLOR = 0xFF6B6B