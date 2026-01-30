import discord
from discord.ext import commands
from config.config import TEMP_VOICE_TRIGGER_CHANNEL_ID, TEMP_VOICE_CATEGORY_ID


class EditChannelNameModal(discord.ui.Modal, title="✏️ Editar nombre del canal"):
    """Modal para editar el nombre del canal temporal"""
    
    def __init__(self, bot, guild_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.guild_id = guild_id
    
    name_input = discord.ui.TextInput(
        label="Nuevo nombre",
        placeholder="Escribe el nuevo nombre del canal (máximo 100 caracteres)",
        required=True,
        max_length=100,
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el servidor.",
                    ephemeral=True
                )
                return
            
            member = guild.get_member(interaction.user.id)
            if not member or not member.voice or not member.voice.channel:
                await interaction.response.send_message(
                    "❌ No estás en un canal de voz.",
                    ephemeral=True
                )
                return
            
            channel = member.voice.channel
            # Editar el nombre del canal
            await channel.edit(name=self.name_input.value)
            await interaction.response.send_message(
                f"✅ El nombre del canal ha sido actualizado a: **{self.name_input.value}**",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al editar el nombre: {e}",
                ephemeral=True
            )


class EditChannelLimitModal(discord.ui.Modal, title="👥 Establecer límite de usuarios"):
    """Modal para establecer el límite de usuarios del canal"""
    
    def __init__(self, bot, guild_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.guild_id = guild_id
    
    limit_input = discord.ui.TextInput(
        label="Límite de usuarios",
        placeholder="Escribe el número de usuarios (0 = sin límite)",
        required=True,
        min_length=1,
        max_length=2,
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            # Validar que sea un número
            limit = int(self.limit_input.value)
            if limit < 0 or limit > 99:
                await interaction.response.send_message(
                    "❌ El límite debe ser entre 0 y 99.",
                    ephemeral=True
                )
                return
            
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el servidor.",
                    ephemeral=True
                )
                return
            
            member = guild.get_member(interaction.user.id)
            if not member or not member.voice or not member.voice.channel:
                await interaction.response.send_message(
                    "❌ No estás en un canal de voz.",
                    ephemeral=True
                )
                return
            
            channel = member.voice.channel
            # Editar el límite del canal
            await channel.edit(user_limit=limit)
            limit_text = "sin límite" if limit == 0 else str(limit)
            await interaction.response.send_message(
                f"✅ El límite del canal ha sido establecido a: **{limit_text}** usuario(s)",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "❌ Debes ingresar un número válido.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al establecer el límite: {e}",
                ephemeral=True
            )


class ChannelConfigView(discord.ui.View):
    """Vista con botones para configurar el canal temporal"""
    
    def __init__(self, bot, guild_id, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.guild_id = guild_id
        self.channel_locked = {}
    
    @discord.ui.button(label="✏️ Editar nombre", style=discord.ButtonStyle.primary)
    async def edit_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botón para editar el nombre del canal"""
        await interaction.response.send_modal(EditChannelNameModal(self.bot, self.guild_id))
    
    @discord.ui.button(label="👥 Límite de usuarios", style=discord.ButtonStyle.primary)
    async def edit_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botón para establecer el límite de usuarios"""
        await interaction.response.send_modal(EditChannelLimitModal(self.bot, self.guild_id))
    
    @discord.ui.button(label="🔒 Bloquear/Desbloquear", style=discord.ButtonStyle.danger)
    async def toggle_lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botón para bloquear/desbloquear el canal"""
        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el servidor.",
                    ephemeral=True
                )
                return
            
            member = guild.get_member(interaction.user.id)
            if not member or not member.voice or not member.voice.channel:
                await interaction.response.send_message(
                    "❌ No estás en un canal de voz.",
                    ephemeral=True
                )
                return
            
            channel = member.voice.channel
            # Obtener el rol @everyone
            everyone_role = guild.default_role
            
            # Alternar el estado de bloqueo
            current_permissions = channel.permissions_for(everyone_role)
            
            if current_permissions.connect:
                # Bloquear el canal
                await channel.set_permissions(
                    everyone_role,
                    connect=False,
                    reason="Canal bloqueado por el propietario"
                )
                await interaction.response.send_message(
                    "🔒 El canal ha sido **bloqueado**. Solo miembros actuales pueden escribir.",
                    ephemeral=True
                )
                self.channel_locked[channel.id] = True
            else:
                # Desbloquear el canal
                await channel.set_permissions(
                    everyone_role,
                    connect=True,
                    reason="Canal desbloqueado por el propietario"
                )
                await interaction.response.send_message(
                    "🔓 El canal ha sido **desbloqueado**. Todos pueden conectarse nuevamente.",
                    ephemeral=True
                )
                self.channel_locked[channel.id] = False
                
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al cambiar el estado del canal: {e}",
                ephemeral=True
            )


class TempVoice(commands.Cog):
    """Cog para manejar canales temporales de voz"""

    def __init__(self, bot):
        self.bot = bot
        # Diccionario para rastrear qué canales temporales pertenecen a qué usuario
        self.temp_channels = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Se ejecuta cuando un usuario cambia de estado de voz
        - Entra a un canal de voz
        - Sale de un canal de voz
        - Se mueve entre canales de voz
        """
        
        # Caso 1: Usuario entra al canal trigger (crear canal temporal)
        if after.channel and after.channel.id == TEMP_VOICE_TRIGGER_CHANNEL_ID:
            await self.create_temp_channel(member)
        
        # Caso 2: Usuario sale de un canal temporal (verificar si está vacío)
        if before.channel:
            # Verificar si es un canal temporal (está en nuestro diccionario)
            if before.channel.id in self.temp_channels.values():
                # Si el canal no tiene usuarios, eliminarlo
                if len(before.channel.members) == 0:
                    await self.delete_temp_channel(before.channel)

    async def create_temp_channel(self, member):
        """Crea un canal temporal de voz para el usuario"""
        try:
            # Obtener la categoría
            category = self.bot.get_channel(TEMP_VOICE_CATEGORY_ID)
            if not category:
                print(f"❌ No se encontró la categoría con ID {TEMP_VOICE_CATEGORY_ID}")
                return
            
            # Crear el nombre del canal: 🔊┃<nombre de usuario>
            channel_name = f"🔊┃{member.name}"
            
            # Crear el canal de voz en la categoría
            temp_channel = await category.create_voice_channel(
                name=channel_name,
                reason=f"Canal temporal creado para {member.name}"
            )
            
            # Rastrear este canal como temporal
            self.temp_channels[member.id] = temp_channel.id
            
            # Mover al usuario al canal creado
            await member.move_to(temp_channel)
            
            # Enviar mensaje privado al usuario con opciones de configuración
            await self.send_config_message(member, temp_channel)
            
            print(f"✅ Canal temporal creado para {member.name}: {channel_name}")
            
        except Exception as e:
            print(f"❌ Error al crear canal temporal: {e}")

    async def send_config_message(self, member, channel):
        """Envía un mensaje privado al usuario con opciones de configuración"""
        try:
            # Crear embed con información
            embed = discord.Embed(
                title="⚙️ Configuración de tu canal temporal",
                description=f"Tu canal **{channel.name}** ha sido creado correctamente.\n\nUsa los botones abajo para configurarlo:",
                color=0x8970ff
            )
            embed.add_field(
                name="✏️ Editar nombre",
                value="Cambia el nombre de tu canal de voz",
                inline=False
            )
            embed.add_field(
                name="👥 Límite de usuarios",
                value="Establece cuántos usuarios pueden conectarse (0 = sin límite)",
                inline=False
            )
            embed.add_field(
                name="🔒 Bloquear/Desbloquear",
                value="Controla quién puede entrar a tu canal",
                inline=False
            )
            embed.set_footer(text="Los botones están disponibles mientras estés en el canal")
            
            # Crear la vista con el bot y el guild_id
            config_view = ChannelConfigView(self.bot, member.guild.id)
            
            # Enviar el mensaje privado con los botones
            await member.send(embed=embed, view=config_view)
            
        except Exception as e:
            print(f"❌ Error al enviar mensaje privado a {member.name}: {e}")

    async def delete_temp_channel(self, channel):
        """Elimina un canal temporal vacío"""
        try:
            # Buscar y eliminar la referencia en nuestro diccionario
            for user_id, channel_id in list(self.temp_channels.items()):
                if channel_id == channel.id:
                    del self.temp_channels[user_id]
                    break
            
            # Eliminar el canal
            await channel.delete(reason="Canal temporal vacío eliminado automáticamente")
            print(f"✅ Canal temporal eliminado: {channel.name}")
            
        except Exception as e:
            print(f"❌ Error al eliminar canal temporal: {e}")


async def setup(bot):
    """Función requerida por discord.py para cargar el cog"""
    await bot.add_cog(TempVoice(bot))
