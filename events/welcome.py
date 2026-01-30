import discord
from discord.ext import commands
from config.config import WELCOME_CHANNEL_ID, WEBHOOK_COLOR, WELCOME_ROLE_ID, INFO_CHANNEL_ID


async def setup_welcome_event(bot):
    """Configura el evento de bienvenida cuando un miembro se une al servidor"""
    
    @bot.event
    async def on_member_join(member):
        """Se ejecuta cuando un nuevo miembro se une al servidor"""
        try:
            # Obtener el canal de bienvenida
            channel = bot.get_channel(WELCOME_CHANNEL_ID)
            
            if channel is None:
                print(f"❌ No se pudo encontrar el canal con ID: {WELCOME_CHANNEL_ID}")
                return
            
            # Asignar el rol automáticamente
            try:
                role = member.guild.get_role(WELCOME_ROLE_ID)
                if role:
                    await member.add_roles(role)
                    print(f"✅ Rol asignado a {member.name}")
                else:
                    print(f"❌ No se pudo encontrar el rol con ID: {WELCOME_ROLE_ID}")
            except Exception as e:
                print(f"❌ Error al asignar rol: {e}")
            
            # Crear el embed con el mensaje de bienvenida
            embed = discord.Embed(
                title="¡Bienvenido a DorrD Club! 💜",
                description=f"¡Tenemos un nuevo miembro, es {member.mention}!\n\nEs un placer conocerte por aqui y entrar al servidor oficial de **DorrD**. Estamos encantados de que unas al club.\n\nSi tu eres {member.name}, recibirás un mensaje privado para ayudarte.",
                color=WEBHOOK_COLOR
            )
            
            # Pie de página
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(
                text=f"{member.guild.name}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            # Enviar el embed al canal de bienvenida
            await channel.send(embed=embed)
            print(f"✅ Mensaje de bienvenida enviado a {member.name}")
            
            # Enviar mensaje privado al usuario
            try:
                info_channel = bot.get_channel(INFO_CHANNEL_ID)
                channel_mention = f"<#{INFO_CHANNEL_ID}>" if info_channel else f"canal de información"
                
                dm_embed = discord.Embed(
                    title="¡Bienvenido a DorrD Club! 👋",
                    description=f"Hola {member.name},\n\nEs un placer darte la bienvenida oficial a **DorrD Club**. Nos alegra mucho que te hayas unido a nosotros.\n\nPor favor, asegúrate de leer el canal {channel_mention} para enterarte de las normas y toda la información importante del servidor.\n\n¡Que disfrutes tu estancia aquí! 💜",
                    color=WEBHOOK_COLOR
                )
                
                dm_embed.set_footer(text="DorrD Club")
                
                await member.send(embed=dm_embed)
                print(f"✅ Mensaje privado enviado a {member.name}")
            except Exception as e:
                print(f"⚠️ No se pudo enviar mensaje privado a {member.name}: {e}")
            
        except Exception as e:
            print(f"❌ Error al enviar mensaje de bienvenida: {e}")
