import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import asyncio
from config.config import WEBHOOK_COLOR, TICKETS_CHANNEL_ID, TICKETS_CATEGORY_ID, TICKETS_ADMIN_CHANNEL_ID


class TicketModal(discord.ui.Modal, title="🔐 Cerrar Ticket"):
    """Modal para cerrar un ticket y solicitar el motivo"""

    reason = discord.ui.TextInput(
        label="Motivo del cierre",
        placeholder="Explica brevemente por qué se cierra el ticket",
        required=True,
        max_length=1000,
        style=discord.TextStyle.long,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Se ejecuta cuando el usuario envía el formulario de cierre"""
        try:
            # Obtener el canal del ticket
            ticket_channel = interaction.channel
            if not ticket_channel:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el canal del ticket.",
                    ephemeral=True,
                )
                return

            # Crear el embed con el cierre del ticket
            embed = discord.Embed(
                title="🔐 Ticket Cerrado",
                description=f"**Motivo del cierre:**\n{self.reason.value}",
                color=0xff6b6b,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            # Enviar el embed al canal del ticket
            await ticket_channel.send(embed=embed)

            # Actualizar el topic del canal para mostrar que está cerrado
            ticket_id = ticket_channel.id
            creator_id = None
            claimed_info = ""
            
            # Extraer información del topic actual
            if ticket_channel.topic:
                import re
                creator_match = re.search(r'creator_id: (\d+)', ticket_channel.topic)
                claimed_match = re.search(r'Reclamado: :white_check_mark: Sí \((.*?)\)', ticket_channel.topic)
                
                if creator_match:
                    creator_id = int(creator_match.group(1))
                if claimed_match:
                    claimed_info = f" ({claimed_match.group(1)})"
            
            # Actualizar el topic con estado cerrado
            new_topic = f"ID del ticket: {ticket_id} | Estado: :red_square: Cerrado | Reclamado: :white_check_mark: Sí{claimed_info} | creator_id: {creator_id}"
            await ticket_channel.edit(topic=new_topic)

            # Bloquear el canal cuando está cerrado
            # - El creador puede VER pero NO escribir
            # - Los admins pueden ver y escribir
            # - @everyone está bloqueado
            admin_role_id = 1466585864929804339
            admin_role = ticket_channel.guild.get_role(admin_role_id)
            
            # Bloquear a @everyone
            await ticket_channel.set_permissions(
                ticket_channel.guild.default_role, view_channel=False, send_messages=False
            )
            
            # El creador puede ver pero NO escribir
            if creator_id:
                try:
                    creator_member = await ticket_channel.guild.fetch_member(creator_id)
                    await ticket_channel.set_permissions(
                        creator_member,
                        view_channel=True,
                        send_messages=False,
                        read_message_history=True
                    )
                except:
                    pass
            
            # Los admins pueden ver y escribir
            if admin_role:
                await ticket_channel.set_permissions(
                    admin_role,
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

            # Responder al usuario
            await interaction.response.send_message(
                "✅ El ticket ha sido cerrado exitosamente.",
                ephemeral=True,
            )

            # Enviar mensaje privado al creador del ticket solicitando valoración
            if creator_id:
                try:
                    creator = await interaction.client.fetch_user(creator_id)
                    
                    # Crear el embed del mensaje privado
                    rating_embed = discord.Embed(
                        title="¡Muchas gracias por tu ticket!",
                        description="Esperemos que su duda o problema haya sido resuelta, agradecemos que nos valore con una nota. ¿Que nota nos pones del 0 al 10 por tu asistencia? \n\nEscribe tu valoración en este mismo chat. Si no deseas valorar, escribe 'cancelar'.",
                        color=WEBHOOK_COLOR,
                    )
                    
                    # Enviar el mensaje
                    await creator.send(embed=rating_embed)
                    
                    # Esperar la respuesta del usuario
                    def check(msg):
                        return msg.author.id == creator_id and isinstance(msg.channel, discord.DMChannel)
                    
                    try:
                        response = await interaction.client.wait_for('message', check=check, timeout=300.0)  # 5 minutos
                        
                        # Validar la respuesta
                        if response.content.lower() == "cancelar":
                            await creator.send("❌ Valoración cancelada. ¡Gracias de todas formas!")
                            return
                        
                        try:
                            rating = int(response.content)
                            if 0 <= rating <= 10:
                                # Enviar la valoración al canal de administración
                                admin_channel = interaction.client.get_channel(TICKETS_ADMIN_CHANNEL_ID)
                                if admin_channel:
                                    admin_embed = discord.Embed(
                                        title="⭐ Nueva Valoración de Ticket",
                                        color=WEBHOOK_COLOR,
                                    )
                                    admin_embed.add_field(name="Usuario", value=creator.mention, inline=True)
                                    admin_embed.add_field(name="ID Ticket", value=ticket_id, inline=True)
                                    admin_embed.add_field(name="Valoración", value=f"⭐ {rating}/10", inline=True)
                                    admin_embed.add_field(name="Atendido por", value=interaction.user.mention, inline=True)
                                    
                                    await admin_channel.send(embed=admin_embed)
                                
                                # Confirmar al usuario
                                await creator.send(f"✅ ¡Gracias! Tu valoración de {rating}/10 ha sido registrada.")
                            else:
                                await creator.send("❌ Por favor, introduce un número entre 0 y 10.")
                        except ValueError:
                            await creator.send("❌ Por favor, introduce un número entre 0 y 10 o escribe 'cancelar'.")
                    
                    except asyncio.TimeoutError:
                        await creator.send("⏱️ Se agotó el tiempo para responder. Valoración cancelada.")
                
                except discord.NotFound:
                    print(f"❌ No se pudo encontrar el usuario con ID {creator_id}")
                except Exception as e:
                    print(f"❌ Error al enviar mensaje privado: {e}")
        
        except Exception as e:
            print(f"❌ Error al cerrar el ticket: {e}")
            await interaction.response.send_message(
                "❌ Hubo un error al cerrar el ticket.",
                ephemeral=True,
            )
        except Exception as e:
            print(f"❌ Error al cerrar el ticket: {e}")
            await interaction.response.send_message(
                "❌ Hubo un error al cerrar el ticket.",
                ephemeral=True,
            )


class TicketSelectView(discord.ui.View):
    """Vista con el desplegable para manejar opciones del ticket"""

    def __init__(self, bot: commands.Bot, creator_id: int):
        super().__init__()
        self.bot = bot
        self.creator_id = creator_id

    @discord.ui.select(
        placeholder="🎫 Selecciona una opción...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Reclamar ticket",
                value="claim_ticket",
                emoji="👤",
                description="Asignar el ticket a un admin",
            ),
            discord.SelectOption(
                label="Cerrar ticket",
                value="close_ticket",
                emoji="🔐",
                description="Cerrar el ticket y bloquear el canal",
            ),
            discord.SelectOption(
                label="Borrar ticket",
                value="delete_ticket",
                emoji="🗑️",
                description="Eliminar el canal del ticket",
            ),
        ],
    )
    async def ticket_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ) -> None:
        """Maneja la selección del desplegable"""
        selected_value = select.values[0]

        # Verificar si es admin
        is_admin = (
            interaction.user.guild_permissions.administrator
            or interaction.user.id == self.creator_id
        )

        if selected_value == "claim_ticket":
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Solo los admins pueden reclamar tickets.",
                    ephemeral=True,
                )
                return

            # Actualizar el topic del canal
            channel = interaction.channel
            ticket_id = channel.id
            creator_id = None
            
            # Extraer el creator_id del topic actual
            if channel.topic:
                import re
                match = re.search(r'creator_id: (\d+)', channel.topic)
                if match:
                    creator_id = match.group(1)
            
            # Actualizar el topic con la información de reclamado
            new_topic = f"ID del ticket: {ticket_id} | Estado: :white_check_mark: Abierto | Reclamado: :white_check_mark: Sí ({interaction.user.mention}) | creator_id: {creator_id}"
            await channel.edit(topic=new_topic)

            await interaction.response.send_message(
                f"✅ {interaction.user.mention} ha reclamado el ticket.",
                ephemeral=False,
            )

        elif selected_value == "close_ticket":
            # Solo admins con el rol específico pueden cerrar tickets
            admin_role_id = 1466585864929804339
            admin_role = interaction.guild.get_role(admin_role_id)
            has_admin_role = admin_role and admin_role in interaction.user.roles
            
            if not has_admin_role:
                await interaction.response.send_message(
                    "❌ Solo los admins pueden cerrar tickets.",
                    ephemeral=True,
                )
                return

            # Mostrar el modal de cierre
            modal = TicketModal()
            await interaction.response.send_modal(modal)

        elif selected_value == "delete_ticket":
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Solo los admins pueden borrar tickets.",
                    ephemeral=True,
                )
                return

            # Confirmar la eliminación
            await interaction.response.send_message(
                "⚠️ El ticket será eliminado en 5 segundos...",
                ephemeral=False,
            )

            # Esperar 5 segundos y luego eliminar el canal
            import asyncio

            await asyncio.sleep(5)
            try:
                await interaction.channel.delete(reason="Ticket eliminado por admin")
            except Exception as e:
                print(f"❌ Error al eliminar el canal del ticket: {e}")


class TicketCreateView(discord.ui.View):
    """Vista con el botón para crear un ticket"""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(
        label="Crear Ticket",
        style=discord.ButtonStyle.primary,
        emoji="✉️",
        custom_id="create_ticket_button",
    )
    async def create_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Crea un nuevo ticket para el usuario"""
        try:
            user = interaction.user
            guild = interaction.guild

            # Verificar si el usuario ya tiene un ticket abierto
            # Buscar un canal con el creator_id del usuario en el topic
            for channel in guild.text_channels:
                if channel.topic and f"creator_id: {user.id}" in channel.topic:
                    await interaction.response.send_message(
                        f"❌ Ya tienes un ticket abierto: {channel.mention}",
                        ephemeral=True,
                    )
                    return

            # Obtener la categoría de tickets
            category = guild.get_channel(TICKETS_CATEGORY_ID)
            if not category:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar la categoría de tickets.",
                    ephemeral=True,
                )
                return

            # Crear el canal del ticket
            ticket_info = f"ID del ticket: (waiting) | Estado: :white_check_mark: Abierto | Reclamado: :x: No | creator_id: {user.id}"
            ticket_channel = await guild.create_text_channel(
                name=f"✉️┃{user.name}",
                category=category,
                topic=ticket_info,
                reason=f"Ticket creado por {user.display_name}",
            )
            
            # Actualizar el topic con el ID real del canal
            ticket_id = ticket_channel.id
            ticket_info = f"ID del ticket: {ticket_id} | Estado: :white_check_mark: Abierto | Reclamado: :x: No | creator_id: {user.id}"
            await ticket_channel.edit(topic=ticket_info)

            # Establecer los permisos del canal
            admin_role_id = 1466585864929804339
            admin_role = guild.get_role(admin_role_id)
            
            # Bloquear @everyone para ver el ticket
            await ticket_channel.set_permissions(
                guild.default_role, view_channel=False, send_messages=False
            )

            # Permitir acceso al creador del ticket (ver y escribir)
            await ticket_channel.set_permissions(
                user, view_channel=True, send_messages=True, read_message_history=True
            )

            # Permitir acceso al rol de admin (ver y escribir)
            if admin_role:
                await ticket_channel.set_permissions(
                    admin_role,
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                )

            # Enviar un mensaje mencionando al usuario
            welcome_embed = discord.Embed(
                title="✉️ Ticket Creado Correctamente",
                description=f"{user.mention}, tu ticket ha sido creado exitosamente. Por favor, describe tu problema o duda a continuación.",
                color=WEBHOOK_COLOR,
            )
            welcome_embed.set_author(
                name=guild.name, icon_url=guild.icon.url if guild.icon else None
            )

            # Enviar el mensaje con la vista del desplegable
            view = TicketSelectView(self.bot, user.id)
            await ticket_channel.send(embed=welcome_embed, view=view)

            # Responder al usuario que creó el ticket
            await interaction.response.send_message(
                f"✅ Tu ticket ha sido creado exitosamente: {ticket_channel.mention}",
                ephemeral=True,
            )

        except Exception as e:
            print(f"❌ Error al crear el ticket: {e}")
            await interaction.response.send_message(
                "❌ Hubo un error al crear el ticket.",
                ephemeral=True,
            )


class Tickets(commands.Cog):
    """Cog para manejar el sistema de tickets de soporte"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Se ejecuta cuando el bot está listo"""
        print("✅ Cog de Tickets cargado")
        
        # Obtener el canal de tickets
        channel = self.bot.get_channel(TICKETS_CHANNEL_ID)
        
        if not channel:
            print(f"❌ Canal de tickets {TICKETS_CHANNEL_ID} no encontrado")
            return
        
        # Limpiar todos los mensajes del canal
        try:
            async for message in channel.history(limit=None):
                await message.delete()
            print(f"✅ Canal {TICKETS_CHANNEL_ID} limpiado")
        except discord.Forbidden:
            print(f"❌ No tengo permisos para eliminar mensajes en el canal {TICKETS_CHANNEL_ID}")
        except Exception as e:
            print(f"❌ Error limpiando el canal: {e}")
        
        # Crear y enviar el embed con el botón de crear ticket
        embed = discord.Embed(
            title="✉️ ¿Necesitas ayuda?",
            description="En este canal podrás abrir un ticket para hablar directamente con el staff de DorrD, quienes te ayudarán con los problemas o dudas que tengas.",
            color=WEBHOOK_COLOR,
        )
        
        view = TicketCreateView(self.bot)
        
        try:
            await channel.send(embed=embed, view=view)
            print(f"✅ Sistema de tickets enviado al canal {TICKETS_CHANNEL_ID}")
        except discord.Forbidden:
            print(f"❌ No tengo permisos para enviar mensajes en el canal {TICKETS_CHANNEL_ID}")
        except Exception as e:
            print(f"❌ Error al enviar el sistema de tickets: {e}")


async def setup(bot: commands.Bot) -> None:
    """Función requerida por discord.py para cargar el cog"""
    await bot.add_cog(Tickets(bot))
