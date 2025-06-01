import nextcord
from nextcord.ext import commands
from nextcord import Embed, ui, SlashOption
from nextcord.interactions import Interaction
import asyncio
import os
import json

# ========== KONFIGURASI ==========
GUILD_ID = [server_id] # GUILD SERVER ID
CATEGORY_ID = [category_channel_id] # CATEGORY CHANNEL ID
LOG_CHANNEL_IDS = [log_channel_id] # LOG CHANNEL ID
COUNTER_FILE = "ticket_counter.txt"
TRANSAKSI_FILE = "transaksi_data.json"

MANAGE_TICKET_USER_IDS = [user_id_admin] # PERMISSION ADMIN USER ID

# ========== INTENTS DAN BOT ==========
intents = nextcord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

# ========== TICKET COUNTER ==========
def get_next_ticket_number():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("1")
    with open(COUNTER_FILE, "r") as f:
        current = int(f.read().strip())
    with open(COUNTER_FILE, "w") as f:
        f.write(str(current + 1))
    return current

# ========== TRANSAKSI UTILITY ==========
def load_transaksi():
    if not os.path.exists(TRANSAKSI_FILE):
        return {}
    try:
        with open(TRANSAKSI_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_transaksi(data):
    with open(TRANSAKSI_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ========== MODALS ==========
class GamepassModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Format Gamepass")
        self.beli_gamepass = ui.TextInput(label="Beli Gamepass Apa?", required=True,  max_length=20, placeholder="Contoh: Blox Fruit/Grow A Garden")
        self.username_roblox = ui.TextInput(label="Username Roblox?", required=True, max_length=20)
        self.harga = ui.TextInput(label="Harga Gamepass", required=False, max_length=20, placeholder="Contoh: 100 Robux")
        self.add_item(self.beli_gamepass)
        self.add_item(self.username_roblox)
        self.add_item(self.harga)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, "gamepass", {
            "Beli Gamepass": self.beli_gamepass.value,
            "Username": self.username_roblox.value or "-",
            "Harga": self.harga.value or "-"
        })

class RobuxModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Format Robux 5 Hari")
        self.jumlah_robux = ui.TextInput(label="Jumlah Robux yang ingin dibeli?", required=True, max_length=20, placeholder="Contoh: 1000 Robux")
        self.link_gamepass = ui.TextInput(label="Link Gamepass", required=False, max_length=100)
        self.username_roblox = ui.TextInput(label="Username Roblox?", required=False, max_length=20)
        self.add_item(self.jumlah_robux)
        self.add_item(self.link_gamepass)
        self.add_item(self.username_roblox)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, "robux", {
            "Jumlah Robux": self.jumlah_robux.value,
            "Link Gamepass": self.link_gamepass.value or "-",
            "Username": self.username_roblox.value or "-"
        })

class RobuxInstantModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Format Robux Instant")
        self.jumlah_robux = ui.TextInput(label="Jumlah Robux yang ingin dibeli?", required=True, max_length=20)
        self.username_roblox = ui.TextInput(label="Username Roblox?", required=False, max_length=20)
        self.metode_pembayaran = ui.TextInput(label="Metode Pembayaran (opsional)", required=False, max_length=30)
        self.add_item(self.jumlah_robux)
        self.add_item(self.username_roblox)
        self.add_item(self.metode_pembayaran)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, "robux instant", {
            "Jumlah Robux": self.jumlah_robux.value,
            "Username": self.username_roblox.value or "-",
            "Metode Pembayaran": self.metode_pembayaran.value or "-"
        })

class TanyaModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Format Bertanya")
        self.pertanyaan = ui.TextInput(label="Apa yang ingin Anda tanyakan?", required=True, style=nextcord.TextInputStyle.paragraph, max_length=300)
        self.add_item(self.pertanyaan)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, "tanya", {
            "Pertanyaan": self.pertanyaan.value
        })

# ========== VIEW BUTTON ==========
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Gamepass", style=nextcord.ButtonStyle.success, emoji="🎫")
    async def gamepass_button(self, button, interaction: Interaction):
        await interaction.response.send_modal(GamepassModal())

    @ui.button(label="Robux 5 Hari", style=nextcord.ButtonStyle.primary, emoji="⏳")
    async def robux_button(self, button, interaction: Interaction):
        await interaction.response.send_modal(RobuxModal())

    @ui.button(label="Robux Instant", style=nextcord.ButtonStyle.primary, emoji="⚡")
    async def robux_instant_button(self, button, interaction: Interaction):
        await interaction.response.send_modal(RobuxInstantModal())

    @ui.button(label="Bertanya", style=nextcord.ButtonStyle.danger, emoji="❓")
    async def tanya_button(self, button, interaction: Interaction):
        await interaction.response.send_modal(TanyaModal())

# ========== PANEL ==========
@bot.command(name="kstore")
async def panel(ctx):
    if ctx.author.id not in MANAGE_TICKET_USER_IDS:
        await ctx.send("⚠️ Kamu tidak punya izin untuk menjalankan perintah ini.", delete_after=10)
        return
    
    await ctx.message.delete(delay=5)

    embed = Embed(
        title="🎟️ KIM STORE - Open Ticket",
        color=0xffffff
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1329662461871263804/1370249215787401266/KS.gif")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1329662461871263804/1370249902893826129/standard.gif")
    embed.set_footer(text="Made by zaneru.id | KIM STORE", icon_url="https://cdn.discordapp.com/emojis/1273384825801412638.gif?size=512")

    embed.add_field(name="🎫 Gamepass", value="**__Untuk pembelian gamepass__**", inline=False)
    embed.add_field(name="⏳ Robux 5 Hari", value="**__Untuk pembelian robux via link__**", inline=False)
    embed.add_field(name="⚡ Robux Instant", value="**__Untuk pembelian robux instan__**", inline=False)
    embed.add_field(name="❓ Bertanya", value="**__Untuk bertanya__**", inline=False)
    await ctx.send(embed=embed, view=TicketView())

# ========== CREATE TICKET ==========
async def create_ticket(interaction: Interaction, tipe: str, data: dict = None):
    guild = interaction.guild
    category = guild.get_channel(CATEGORY_ID[GUILD_ID.index(guild.id)])

    if not category:
        if interaction.response.is_done():
            await interaction.followup.send("⚠️ Kategori tidak ditemukan atau tidak valid. Silakan hubungi admin.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Kategori tidak ditemukan atau tidak valid. Silakan hubungi admin.", ephemeral=True)
        return

    if len(category.channels) >= 50:
        if interaction.response.is_done():
            await interaction.followup.send("⚠️ Maaf, kategori ticket sudah penuh. Silakan hubungi admin.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Maaf, kategori ticket sudah penuh. Silakan hubungi admin.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
        interaction.user: nextcord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }

    try:
        ticket_number = get_next_ticket_number()
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{ticket_number:04d}",
            overwrites=overwrites,
            category=category,
            topic=str(interaction.user.id)
        )
    except Exception as e:
        if interaction.response.is_done():
            await interaction.followup.send(f"⚠️ Terjadi kesalahan saat membuat ticket: {e}", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Terjadi kesalahan saat membuat ticket: {e}", ephemeral=True)
        return

    embed = Embed(title="📩 Ticket Dibuat", color=0xE4F1F5)
    embed.add_field(name="User", value=interaction.user.mention, inline=False)
    embed.add_field(name="Tipe", value=tipe.capitalize(), inline=False)

    if data:
        for key, value in data.items():
            embed.add_field(name=key, value=value, inline=False)

    await ticket_channel.send(content=interaction.user.mention, embed=embed)
    await ticket_channel.send("Jika transaksi/bertanya telah selesai, silakan klik tombol di bawah untuk menutup tiket.", view=CloseTicketButton())

    for log_channel_id in LOG_CHANNEL_IDS:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            if tipe == "gamepass":
                panel = "🎫 Gamepass"
            elif tipe == "robux":
                panel = "⏳ Robux 5 Hari"
            elif tipe == "robux instant":
                panel = "⚡ Robux Instant"
            else:
                panel = "❓ Bertanya"

            log_embed = Embed(title="Ticket Created", color=0x07B7F9)
            log_embed.add_field(name="Ticket", value=f"🎟️ Ticket-{ticket_number:04d}", inline=False)
            log_embed.add_field(name="Action", value="🔓 Created", inline=False)
            log_embed.add_field(name="Panel", value=panel, inline=False)
            log_embed.add_field(name="Username", value=interaction.user.name, inline=False)
            log_embed.set_image(url="https://cdn.discordapp.com/attachments/1329662461871263804/1370249902893826129/standard.gif")
            log_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1329662461871263804/1370249215787401266/KS.gif")
            log_embed.set_author(name="Ticket Log")
            log_embed.set_footer(text="Made by zaneru.id | KIM STORE", icon_url="https://cdn.discordapp.com/emojis/1273384825801412638.gif?size=512")
            log_embed.timestamp = nextcord.utils.utcnow()
            await log_channel.send(embed=log_embed)

    await interaction.followup.send(f"✅ Ticket kamu sudah dibuat: {ticket_channel.mention}", ephemeral=True)

# ========== CLOSE TICKET BUTTON ==========
class CloseTicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Tutup Ticket", style=nextcord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, button: ui.Button, interaction: Interaction):
        if interaction.user.id not in MANAGE_TICKET_USER_IDS:
            await interaction.response.send_message("⚠️ Kamu tidak punya izin untuk menutup ticket ini.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Ticket ditutup. Akan dihapus dalam 5 detik...", ephemeral=True)
        await interaction.channel.send("🛑 Ticket ini telah ditutup.")
        await asyncio.sleep(5)
        await interaction.channel.delete()

        for log_channel_id in LOG_CHANNEL_IDS:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                log_embed = Embed(title="Ticket Closed", color=0xFE0909)
                log_embed.add_field(name="Ticket", value=f"🎟️ {interaction.channel.name}", inline=False)
                log_embed.add_field(name="Action", value="❌ Closed", inline=False)
                log_embed.add_field(name="Panel", value="🔒 Ticket Closed", inline=False)
                log_embed.add_field(name="Username", value=interaction.user.name, inline=False)
                log_embed.set_image(url="https://cdn.discordapp.com/attachments/1329662461871263804/1370249902893826129/standard.gif")
                log_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1329662461871263804/1370249215787401266/KS.gif")
                log_embed.set_author(name="Ticket Log")
                log_embed.set_footer(text="Made by zaneru.id | KIM STORE", icon_url="https://cdn.discordapp.com/emojis/1273384825801412638.gif?size=512")
                log_embed.timestamp = nextcord.utils.utcnow()
                await log_channel.send(embed=log_embed)

# ========== /transaksi ==========
@bot.slash_command(name="transaksi", description="Tambahkan transaksi ke pengguna", guild_ids=GUILD_ID)
async def transaksi(
    interaction: Interaction,
    member: nextcord.Member = SlashOption(name="member", description="Member yang melakukan transaksi", required=True),
    jumlah: str = SlashOption(name="jumlah", description="Jumlah transaksi (misalnya: 100.000)", required=True),
):
    if interaction.user.id not in MANAGE_TICKET_USER_IDS:
        await interaction.response.send_message("⚠️ Kamu tidak punya izin untuk menggunakan perintah ini.", ephemeral=True)
        return

    try:
        jumlah_int = int(jumlah.replace(".", "").replace(",", ""))
    except ValueError:
        await interaction.response.send_message("❌ Format jumlah tidak valid. Gunakan angka seperti `100.000`.", ephemeral=True)
        return

    data = load_transaksi()
    user_id = str(member.id)
    data[user_id] = data.get(user_id, 0) + jumlah_int
    save_transaksi(data)

    await interaction.response.send_message(
        f"✅ Transaksi sebesar `Rp {jumlah_int:,}` telah ditambahkan untuk {member.mention}. Total sekarang: `Rp {data[user_id]:,}`",
        ephemeral=True
    )

# ========== /total_transaksi ==========
@bot.slash_command(name="total_transaksi", description="Lihat total transaksi kamu", guild_ids=GUILD_ID)
async def total_transaksi(interaction: Interaction):
    data = load_transaksi()
    user_id = str(interaction.user.id)
    total = data.get(user_id, 0)

    embed = Embed(title="💰 Total Transaksi Kamu", color=0x00ffcc)
    embed.add_field(name="Nama", value=interaction.user.name, inline=True)
    embed.add_field(name="Total", value=f"Rp {total:,}", inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== EVENT READY ==========
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} sekarang online!')

# ========== JALANKAN BOT ==========
bot.run("BOT_TOKEN")