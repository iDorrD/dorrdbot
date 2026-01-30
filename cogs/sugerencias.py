import discord
from discord import app_commands
from discord.ext import commands
from config.config import WEBHOOK_COLOR

SUGERENCIAS_CHANNEL_ID = 1466598331089162278


class SugerenciaModal(discord.ui.Modal, title="📨 ¡Nueva sugerencia!"):
    """Modal para que los usuarios envíen sus sugerencias"""

    sugerencia = discord.ui.TextInput(
        label="Tu sugerencia",
        placeholder="Escribe tu sugerencia aquí (máximo 4000 caracteres)",
        required=True,
        max_length=4000,
        style=discord.TextStyle.long,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Se ejecuta cuando el usuario envía el formulario"""
        try:
            # Obtener el canal de sugerencias
            sugerencias_channel = interaction.client.get_channel(SUGERENCIAS_CHANNEL_ID)
            if not sugerencias_channel:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el canal de sugerencias.",
                    ephemeral=True,
                )
                return

            # Crear el embed (webhook) con la sugerencia
            embed = discord.Embed(
                title="📨 ¡Nueva sugerencia!",
                description=self.sugerencia.value,
                color=WEBHOOK_COLOR,
            )

            # Configurar el header del webhook con información del usuario
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            # Enviar el embed al canal de sugerencias
            message = await sugerencias_channel.send(embed=embed)

            # Auto-reaccionar con :arrow_up:
            await message.add_reaction("⬆️")

            # Responder al usuario
            await interaction.response.send_message(
                "✅ ¡Tu sugerencia ha sido enviada exitosamente!",
                ephemeral=True,
            )
        except Exception as e:
            print(f"❌ Error en el modal de sugerencias: {e}")
            await interaction.response.send_message(
                "❌ Hubo un error al procesar tu sugerencia.",
                ephemeral=True,
            )


class Sugerencias(commands.Cog):
    """Cog para manejar el sistema de sugerencias"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listener para eliminar automáticamente mensajes en el canal de sugerencias (excepto del bot)"""
        # Ignorar mensajes del bot
        if message.author == self.bot.user:
            return

        # Verificar si el mensaje está en el canal de sugerencias
        if message.channel.id == SUGERENCIAS_CHANNEL_ID:
            try:
                # Borrar el mensaje automáticamente
                await message.delete()
            except discord.Forbidden:
                print(
                    f"❌ No tengo permisos para eliminar mensajes en el canal {SUGERENCIAS_CHANNEL_ID}"
                )
            except discord.NotFound:
                pass  # El mensaje ya fue eliminado
            except Exception as e:
                print(f"❌ Error al eliminar mensaje en sugerencias: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """Listener para detectar reacciones en el canal de sugerencias"""
        # Verificar si la reacción está en el canal de sugerencias
        if payload.channel_id != SUGERENCIAS_CHANNEL_ID:
            return

        # Verificar si la reacción es un check mark
        if payload.emoji.name != "✅":
            return

        # Ignorar reacciones del bot
        if payload.user_id == self.bot.user.id:
            return

        try:
            # Obtener el usuario que reaccionó
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            # Verificar que el usuario tiene permisos de administrador
            if not member or not member.guild_permissions.administrator:
                return

            # Obtener el canal y el mensaje
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            # Extraer la información de la sugerencia del embed original
            if not message.embeds:
                return

            original_embed = message.embeds[0]
            sugerencia_text = original_embed.description
            autor_name = original_embed.author.name
            autor_icon = original_embed.author.icon_url

            # Obtener el usuario original de la sugerencia
            # Intentamos encontrarlo por el nombre en el servidor
            original_user = None
            for member_search in guild.members:
                if member_search.display_name == autor_name:
                    original_user = member_search
                    break

            # Crear el embed de aprobación con color verde claro
            approval_embed = discord.Embed(
                title="✅ ¡Sugerencia Aprobada!",
                description=sugerencia_text,
                color=0x57F287,  # Verde claro
            )

            # Configurar el header del webhook
            approval_embed.set_author(
                name=autor_name,
                icon_url=autor_icon,
            )

            # Agregar mención al usuario original si se encontró
            mention_text = ""
            if original_user:
                mention_text = f"\n\n👤 Sugerencia de {original_user.mention}"
            else:
                mention_text = f"\n\n👤 Sugerencia de {autor_name}"

            approval_embed.add_field(
                name="",
                value=mention_text,
                inline=False,
            )

            # Enviar el embed de aprobación al mismo canal
            await channel.send(embed=approval_embed)

            # Enviar mensaje privado al usuario original si existe
            if original_user:
                try:
                    dm_embed = discord.Embed(
                        title="✅ ¡Tu sugerencia fue aprobada!",
                        description=f"Un administrador ha aprobado tu sugerencia:\n\n> {sugerencia_text}",
                        color=0x57F287,  # Verde claro
                    )
                    await original_user.send(embed=dm_embed)
                except discord.Forbidden:
                    print(f"⚠️ No se pudo enviar DM a {original_user} - tiene los DMs desactivados")
                except Exception as e:
                    print(f"❌ Error al enviar DM al usuario: {e}")

        except Exception as e:
            print(f"❌ Error procesando reacción de aprobación: {e}")

    @app_commands.command(name="sugerencia", description="Envía una sugerencia al servidor")
    async def sugerencia(self, interaction: discord.Interaction) -> None:
        """Comando slash para abrir el modal de sugerencias"""
        # Mostrar el modal al usuario
        await interaction.response.send_modal(SugerenciaModal())


async def setup(bot: commands.Bot) -> None:
    """Cargar el cog de sugerencias"""
    await bot.add_cog(Sugerencias(bot))
    print("✅ Sistema de sugerencias cargado")
