import discord
from discord import app_commands
from discord.ext import commands
from config.config import MODERATION_LOG_CHANNEL_ID, MODERATION_WEBHOOK_COLOR

# IDs de roles de admin
ADMIN_ROLE_IDS = [
    1466585692791378113,
    1466585864929804339,
    1466787362712588309,
]


class Moderation(commands.Cog):
    """Cog para manejar las sanciones del servidor (bans, kicks, temporary bans)"""

    def __init__(self, bot):
        self.bot = bot

    def has_admin_role(self, member: discord.Member) -> bool:
        """Verifica si el miembro tiene alguno de los roles de admin"""
        return any(role.id in ADMIN_ROLE_IDS for role in member.roles)

    async def send_moderation_webhook(
        self,
        guild: discord.Guild,
        action: str,
        sanctioned_user: discord.User,
        reason: str,
        moderator: discord.User,
    ):
        """
        Envía un webhook de sanción a un canal específico.
        """
        try:
            channel = guild.get_channel(MODERATION_LOG_CHANNEL_ID)
            if not channel:
                print(f"❌ No se encontró el canal de moderación {MODERATION_LOG_CHANNEL_ID}")
                return

            reason_display = reason if reason and reason.strip() else "No especificado"

            embed = discord.Embed(
                title=f"`{sanctioned_user.name}` ha sido {action}",
                description=(
                    f"**Motivo:** {reason_display}\n"
                    f"**Sancionador:** {moderator.mention}"
                ),
                color=MODERATION_WEBHOOK_COLOR,
            )
            embed.set_author(
                name=sanctioned_user.display_name,
                icon_url=sanctioned_user.display_avatar.url,
            )
            embed.set_footer(text=f"ID: {sanctioned_user.id}")

            await channel.send(embed=embed)
            print(f"✅ Webhook de sanción enviado: {sanctioned_user.name} {action}")

        except Exception as e:
            print(f"❌ Error al enviar webhook de sanción: {e}")

    async def send_sanction_dm(
        self,
        sanctioned_user: discord.User,
        action: str,
        reason: str,
        moderator: discord.User,
    ):
        """
        Envía un mensaje privado al usuario sancionado.
        """
        try:
            embed = discord.Embed(
                title=f"❌ Has sido {action}",
                description=(
                    f"**Motivo:** {reason if reason and reason.strip() else 'No especificado'}\n"
                    f"**Sancionador:** {moderator.mention}"
                ),
                color=MODERATION_WEBHOOK_COLOR,
            )
            embed.set_footer(text="Si crees que esto es un error, contacta con los administradores")
            
            await sanctioned_user.send(embed=embed)
            print(f"✅ DM de sanción enviado a: {sanctioned_user.name}")
            
        except discord.Forbidden:
            print(f"❌ No se pudo enviar DM a {sanctioned_user.name} (DMs deshabilitados)")
        except Exception as e:
            print(f"❌ Error al enviar DM de sanción: {e}")


    @app_commands.command(name="kick", description="Expulsa a un usuario del servidor")
    async def slash_kick(
        self, 
        interaction: discord.Interaction, 
        usuario: discord.User,
        motivo: str = None
    ):
        """Expulsa a un usuario del servidor"""
        
        # Verificar si el usuario tiene rol de admin
        if not self.has_admin_role(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando. Solo admins pueden expulsar miembros.",
                ephemeral=True
            )
            return
        
        try:
            # Obtener el miembro del servidor
            member = await interaction.guild.fetch_member(usuario.id)
            
            reason_display = motivo if motivo and motivo.strip() else "No especificado"
            
            # Enviar DM al usuario ANTES de kickearlo
            await self.send_sanction_dm(
                sanctioned_user=usuario,
                action="kickeado",
                reason=reason_display,
                moderator=interaction.user,
            )
            
            # Kickear al usuario
            await member.kick(reason=reason_display)
            
            # Enviar webhook
            await self.send_moderation_webhook(
                guild=interaction.guild,
                action="kickeado",
                sanctioned_user=usuario,
                reason=reason_display,
                moderator=interaction.user,
            )
            
            # Respuesta de éxito
            embed = discord.Embed(
                title="✅ Usuario Expulsado",
                description=f"{usuario.mention} ha sido expulsado del servidor",
                color=0x00ff00,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para expulsar a este usuario.",
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                "❌ Usuario no encontrado en el servidor.",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Error en kick: {e}")
            await interaction.response.send_message(
                f"❌ Error al expulsar al usuario: {e}",
                ephemeral=True
            )

    @app_commands.command(name="ban", description="Banea a un usuario del servidor")
    async def slash_ban(
        self,
        interaction: discord.Interaction,
        usuario: discord.User,
        motivo: str = None
    ):
        """Banea a un usuario del servidor"""
        
        # Verificar si el usuario tiene rol de admin
        if not self.has_admin_role(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando. Solo admins pueden banear miembros.",
                ephemeral=True
            )
            return
        
        try:
            reason_display = motivo if motivo and motivo.strip() else "No especificado"
            
            # Enviar DM al usuario ANTES de banearlo
            await self.send_sanction_dm(
                sanctioned_user=usuario,
                action="baneado",
                reason=reason_display,
                moderator=interaction.user,
            )
            
            # Banear al usuario
            await interaction.guild.ban(usuario, reason=reason_display)
            
            # Enviar webhook
            await self.send_moderation_webhook(
                guild=interaction.guild,
                action="baneado",
                sanctioned_user=usuario,
                reason=reason_display,
                moderator=interaction.user,
            )
            
            # Respuesta de éxito
            embed = discord.Embed(
                title="✅ Usuario Baneado",
                description=f"{usuario.mention} ha sido baneado del servidor",
                color=0x00ff00,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para banear a este usuario.",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Error en ban: {e}")
            await interaction.response.send_message(
                f"❌ Error al banear al usuario: {e}",
                ephemeral=True
            )

    @app_commands.command(name="tempban", description="Banea temporalmente a un usuario del servidor")
    async def slash_tempban(
        self,
        interaction: discord.Interaction,
        usuario: discord.User,
        tiempo: str,
        motivo: str = None
    ):
        """
        Banea temporalmente a un usuario del servidor.
        
        Tiempo: número de días (ej: 7, 30, etc)
        """
        
        # Verificar si el usuario tiene rol de admin
        if not self.has_admin_role(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando. Solo admins pueden banear miembros.",
                ephemeral=True
            )
            return
        
        try:
            # Validar que el tiempo sea un número
            try:
                dias = int(tiempo)
            except ValueError:
                await interaction.response.send_message(
                    f"❌ El tiempo debe ser un número de días. Recibido: {tiempo}",
                    ephemeral=True
                )
                return
            
            if dias <= 0:
                await interaction.response.send_message(
                    "❌ El número de días debe ser mayor a 0.",
                    ephemeral=True
                )
                return
            
            reason_display = motivo if motivo and motivo.strip() else "No especificado"
            
            # Enviar DM al usuario ANTES de banearlo
            await self.send_sanction_dm(
                sanctioned_user=usuario,
                action=f"baneado temporalmente por {dias} día(s)",
                reason=reason_display,
                moderator=interaction.user,
            )
            
            # Banear al usuario
            await interaction.guild.ban(
                usuario, 
                reason=f"{reason_display} (Temporal: {dias} día(s))"
            )
            
            # Enviar webhook
            await self.send_moderation_webhook(
                guild=interaction.guild,
                action=f"baneado temporalmente por {dias} día(s)",
                sanctioned_user=usuario,
                reason=reason_display,
                moderator=interaction.user,
            )
            
            # Respuesta de éxito
            embed = discord.Embed(
                title="✅ Usuario Baneado Temporalmente",
                description=f"{usuario.mention} ha sido baneado por {dias} día(s)",
                color=0x00ff00,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para banear a este usuario.",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ Error en tempban: {e}")
            await interaction.response.send_message(
                f"❌ Error al banear temporalmente al usuario: {e}",
                ephemeral=True
            )


async def setup(bot):
    """Cargar el cog"""
    await bot.add_cog(Moderation(bot))

