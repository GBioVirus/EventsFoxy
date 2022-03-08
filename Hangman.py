
import discord
from discord.ext import commands, tasks
from discord_buttons_plugin import *
import threading
import asyncio
import time
import json

TOKEN = "токен"

bot = commands.Bot(command_prefix='')
buttons = ButtonsClient(bot)
games = []

@bot.event
async def on_ready():
    activity = discord.Game(name="Bot bug dance", type=3)
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print('We have logged in as {0.user}'.format(bot))
 
#@bot.command(name="k!play")
#async def play(ctx):
#    mytag = open("tags.json", "r") 
#    await ctx.send(mytag)
      
    
@bot.command(name="k!Hangman")
async def Hangman(ctx, user1: discord.User, user2: discord.User, chan: discord.TextChannel):
    await hangman_command(ctx, user1, user2, chan)


@bot.command(name="k!hangman")
async def hangman(ctx, user1: discord.User, user2: discord.User, chan: discord.TextChannel):
    await hangman_command(ctx, user1, user2, chan)


def generate_embed(text):
    return discord.Embed(color=0xff0000, description=text)


async def hangman_command(ctx, user1, user2, chan):
    if find_json(user1.id, user2.id) != '':
        await ctx.send('Game with one of these players already exists')
        return
    word = ' '.join(ctx.message.content.split()[4:])

    j = {
        'author': ctx.author.id,
        "player1": user1.id,
        "player2": user2.id,
        "turn": 1,
        "channel": chan,
        "word": word.lower(),
        "letters": [],
        "id": len(games)
    }

    msg = await ctx.send(
        embed=generate_embed(f"<@{user1.id}> & <@{user2.id}>\nWord: {word}"),
    )

    await buttons.send(
        content="‎",
        channel=ctx.channel.id,
        components=[
            ActionRow([
                Button(
                    label="Stop Game",
                    style=ButtonType().Danger,
                    custom_id='stop_game'
                )
            ])
        ]
    )

    j['messages'] = [msg]

    games.append(j)
    j['messages'].append(await chan.send(embed=generate_embed(f"Welcome to Hangman\n<@{user1.id}> vs <@{user2.id}>")))


@buttons.click
async def stop_game(interaction):
    json = find_json(interaction.member.id)
    if json != '':
        if interaction.member.id == json['author']:
            games.remove(json)
            await interaction.message.delete()
            await interaction.channel.send('Game has been stopped')


async def parse_message(text, json):
    if text.lower().startswith('>') and len(text) > 1:
        if json['word'] == ' '.join(text[1:].split()):
            await json['channel'].send('Correct!')
            for i in ''.join(text[1:].split()):
                if i not in json['letters']:
                    json['letters'].append(i)
        else:
            await json['channel'].send('Incorrect')
            switch_turn(json)
    elif len(text) != 1 or text in json['letters']:
        await json['channel'].send("Repit")
        return False
    else:
        if text in json['word']:
            await json['channel'].send('Yup')
        else:
            await json['channel'].send('Nope')
            switch_turn(json)
        json['letters'].append(text)
    await json['channel'].send(embed=generate_embed(await generate_hangman_message(json)))
    return True


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id and len(message.embeds) == 1 and message.embeds[0].description.startswith(
            'Welcome to Hangman'):
        time.sleep(2)
        game = {}
        for game in games:
            if message in game['messages']:
                break

        await message.channel.send(embed=generate_embed(await generate_hangman_message(game)))

        def check(mes):
            return game['player' + str(game['turn'])] == mes.author.id and mes.channel == game['channel']

        def json_check(j):
            return j in games

        while json_check(game):
            try:
                m = await bot.wait_for('message', check=check, timeout=30)
                if json_check(game):
                    await parse_message(m.content.lower(), game)
            except asyncio.TimeoutError:
                switch_turn(game)
                if json_check(game):
                    await game['channel'].send(f'Run out of time! Now is turn <@{game["player" + str(game["turn"])]}>')

    elif message.content.startswith('k!'):
        await bot.process_commands(message)


def switch_turn(json):
    if json['turn'] == 1:
        json['turn'] = 2
    else:
        json['turn'] = 1


def find_json(user, sub=''):
    for i in games:
        for key in i:
            if i[key] == user or (key != 'author' and i[key] == sub):
                return i

        #if i['player1'] == user or i['']or i['player2'] == user or i['author'] == user:
        #    return i
    return ' 


async def generate_hangman_message(json):
    global games
    s = f"<@{json['player' + str(json['turn'])]}>\nLetters: {', '.join(json['letters'])}\nTime: 30sec\n\n**"
    count = 0
    for i in json['word']:
        if i in json['letters']:
            s += str(i).upper()
            count += 1
        elif i == ' ':
            s += '\n'
            count += 1
        else:
            s += "🔵"
    if count == len(json['word']):
        s += f"**\n**Word is guessed!**\nWinner: <@{json['player' + str(json['turn'])]}>"
        games.remove(json)
        for i in json['messages']:
            await i.edit(
                embed=generate_embed(i.embeds[0].description + f"\n<@{json['player' + str(json['turn'])]}> won!"))
    else:
        s += "**\n\nUse >word if you know the word\n<a:30sec:917153751465353237><a:10sec:917153782889078784>"
    return s

bot.run(TOKEN)
