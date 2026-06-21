import os
import random
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("MTQzOTI5MjU1MTUyNTA0NDMzNQ.GiJaCF.3qULm0WY5XzhHokEPmS7ywi-L9AUPxWbUeFE58")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# CONFIG STAFF
# ======================

STAFF_ROLE_NAME = "「équipe de modération」"

def is_staff():
    async def predicate(ctx):
        role = discord.utils.get(ctx.guild.roles, name=STAFF_ROLE_NAME)
        return role in ctx.author.roles
    return commands.check(predicate)

# ======================
# READY
# ======================

@bot.event
async def on_ready():
    print(f"Connecté : {bot.user}")

# ======================
# ANTI-LIEN (tout le monde)
# ======================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    links = ["http://", "https://", "discord.gg/"]

    if any(x in message.content.lower() for x in links):

        role = discord.utils.get(message.guild.roles, name=STAFF_ROLE_NAME)

        if role not in message.author.roles:
            await message.delete()
            await message.channel.send(
                f"🚫 {message.author.mention} liens interdits.",
                delete_after=5
            )

    await bot.process_commands(message)

# ======================
# MODÉRATION (STAFF ONLY)
# ======================

@bot.command()
@is_staff()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages supprimés.", delete_after=3)

@bot.command()
@is_staff()
async def kick(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} expulsé.")

@bot.command()
@is_staff()
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banni.")

@bot.command()
@is_staff()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Salon verrouillé.")

@bot.command()
@is_staff()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Salon ouvert.")

# ======================
# EVENT SYSTEM (STAFF ONLY)
# ======================

@bot.command()
@is_staff()
async def giveaway(ctx, duration: int, *, prize):

    embed = discord.Embed(
        title="🎉 GIVEAWAY",
        description=f"Prix : **{prize}**\nRéagis 🎉",
        color=discord.Color.gold()
    )

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

    await asyncio.sleep(duration)

    msg = await ctx.channel.fetch_message(msg.id)

    users = []

    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for u in reaction.users():
                if not u.bot:
                    users.append(u)

    if not users:
        return await ctx.send("❌ Aucun participant.")

    winner = random.choice(users)

    await ctx.send(f"🏆 Winner : {winner.mention} gagne **{prize}**")

# ======================
# POLL EVENT
# ======================

@bot.command()
@is_staff()
async def poll(ctx, *, question):

    embed = discord.Embed(
        title="📊 Sondage",
        description=question,
        color=discord.Color.blue()
    )

    msg = await ctx.send(embed=embed)

    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# ======================
# HELP
# ======================

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📌 Bot Commands",
        description="Modération + Events",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🛡️ Staff",
        value="clear, kick, ban, lock, unlock, giveaway, poll",
        inline=False
    )

    await ctx.send(embed=embed)

# ======================
# ERROR HANDLER
# ======================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Tu n'es pas staff.")

# ======================
# RUN
# ======================

bot.run(TOKEN)