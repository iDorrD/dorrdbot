import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config.config import SERIES_CHANNEL_ID, PRO_ROLE_ID, WEBHOOK_COLOR

class SeriesDropdown(discord.ui.Select):
    """Dropdown para seleccionar series"""
    
    def __init__(self, bot, series_data, interaction_user):
        self.bot = bot
        self.series_data = series_data
        self.interaction_user = interaction_user
        self.pro_role_id = PRO_ROLE_ID
        
        options = []
        
        for serie in series_data["series"]:
            # Omitir si está marcado como unlisted
            if serie.get("unlisted", False):
                continue
            
            # Construir el nombre con iconos
            nombre = serie["nombre"]
            
            if serie.get("privado", False):
                nombre += " 🔒"
            
            if serie.get("pro", False):
                nombre += " [Requiere PRO]"
            
            option = discord.SelectOption(
                label=nombre,
                value=serie["nombre"],
                description=serie.get("descripcion", "Sin descripción")
            )
            options.append(option)
        
        # Agregar opción para limpiar todos los roles
        options.append(discord.SelectOption(
            label="🗑️ Limpiar Todos los Roles",
            value="__LIMPIAR_TODOS__",
            description="Elimina todos los roles de series que tengas"
        ))
        
        super().__init__(
            placeholder="Selecciona una serie...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback cuando se selecciona una serie"""
        
        # Opción especial: limpiar todos los roles
        if self.values[0] == "__LIMPIAR_TODOS__":
            roles_removidos = []
            
            for serie in self.series_data["series"]:
                role_id = int(serie["id_rol"])
                role = interaction.guild.get_role(role_id)
                
                if role and role in interaction.user.roles:
                    try:
                        await interaction.user.remove_roles(role)
                        roles_removidos.append(serie["nombre"])
                    except discord.Forbidden:
                        pass
                    except Exception as e:
                        print(f"❌ Error removiendo rol {role_id}: {e}")
            
            if roles_removidos:
                await interaction.response.send_message(
                    f"🗑️ Se han eliminado los siguientes roles:\n" + "\n".join([f"• {r}" for r in roles_removidos]),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "ℹ️ No tienes ningún rol de series activo.",
                    ephemeral=True
                )
            return
        
        selected_serie = None
        
        for serie in self.series_data["series"]:
            if serie["nombre"] == self.values[0]:
                selected_serie = serie
                break
        
        if not selected_serie:
            await interaction.response.send_message("❌ Serie no encontrada.", ephemeral=True)
            return
        
        # Obtener el rol de la serie
        role_id = int(selected_serie["id_rol"])
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message(
                "❌ El rol de la serie no existe.",
                ephemeral=True
            )
            return
        
        # Verificar si el usuario ya tiene el rol
        if role in interaction.user.roles:
            # Quitar el rol (desactivar)
            try:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"❌ Se ha desactivado **{selected_serie['nombre']}**. Rol removido.",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ No tengo permisos para remover roles.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error al remover el rol: {e}",
                    ephemeral=True
                )
            return
        
        # Verificar si es privado - solo admins pueden seleccionarlo
        if selected_serie.get("privado", False):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Esta serie es privada y solo los administradores pueden seleccionarla.",
                    ephemeral=True
                )
                return
        
        # Verificar si es PRO - usuario debe tener el rol PRO
        if selected_serie.get("pro", False):
            pro_role = interaction.guild.get_role(self.pro_role_id)
            if not pro_role or pro_role not in interaction.user.roles:
                await interaction.response.send_message(
                    f"❌ Esta serie es PRO. Necesitas el rol <@&{self.pro_role_id}> para seleccionarla.",
                    ephemeral=True
                )
                return
        
        # Asignar el rol
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ ¡Se te ha asignado el rol para **{selected_serie['nombre']}**!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para asignar roles.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al asignar el rol: {e}",
                ephemeral=True
            )


class SeriesView(discord.ui.View):
    """View que contiene el dropdown de series"""
    
    def __init__(self, bot, series_data, interaction_user):
        super().__init__(timeout=None)
        self.add_item(SeriesDropdown(bot, series_data, interaction_user))


class Series(commands.Cog):
    """Cog para manejar el sistema de series privadas"""
    
    def __init__(self, bot):
        self.bot = bot
        self.series_file = "data/series.json"
        self.load_series()
    
    def load_series(self):
        """Cargar las series del archivo JSON"""
        try:
            with open(self.series_file, "r", encoding="utf-8") as f:
                self.series_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Archivo {self.series_file} no encontrado")
            self.series_data = {"series": []}
        except json.JSONDecodeError:
            print(f"❌ Error decodificando {self.series_file}")
            self.series_data = {"series": []}
    



async def setup(bot):
    """Función requerida por Discord.py para cargar el cog"""
    await bot.add_cog(Series(bot))
