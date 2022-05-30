import discord
from discord.ext import commands, tasks
import threading
import asyncio
import time
TOKEN = "add token"

bot = commands.Bot(command_prefix='')

games = []


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '🛑':
        json = find_json(user.id)
        if json != '':
            games.remove(json)
            print(games)
            await reaction.message.channel.send('Game has been stopped')


@bot.command(name="k!Hangman")
async def Hangman(ctx, user1: discord.User, user2: discord.User, chan: discord.TextChannel):
    await hangman_command(ctx, user1, user2, chan)


@bot.command(name="k!hangman")
async def hangman(ctx, user1: discord.User, user2: discord.User, chan: discord.TextChannel):
    await hangman_command(ctx, user1, user2, chan)


def generate_embed(text):
    return discord.Embed(color=0xff0000, description=text)


async def hangman_command(ctx, user1, user2, chan):
    if find_json(user1.id) == '' and find_json(user2.id):
        await ctx.send('Game with these players already exists')
        return
    word = ' '.join(ctx.message.content.split()[4:])
    msg = await ctx.send(embed=generate_embed(f"<@{user1.id}> & <@{user2.id}>\nWord: {word}"))

    j = {
        "player1": user1.id,
        "player2": user2.id,
        "turn": 1,
        "channel": chan,
        "word": word.lower(),
        "letters": [],
        "messages": [msg],
        "id": len(games)
    }
    i = len(games)

    await msg.add_reaction('🛑')
    games.append(j)
    j['messages'].append(await chan.send(embed=generate_embed(f"Welcome to Hangman\n<@{user1.id}> vs <@{user2.id}>")))


async def parse_message(text, json):
    if text.lower().startswith('>'):
        if len(text) > 1:
            if json['word'] == ' '.join(text[1:].split()):
                await json['channel'].send('Correct!')
                for i in ''.join(text[1:].split()):
                    if i not in json['letters']:
                        json['letters'].append(i)
            else:
                await json['channel'].send('Incorrect')
    elif len(text) != 1 or text in json['letters']:
        await json['channel'].send("Will Repit")
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
    if message.author.id == bot.user.id and len(message.embeds) == 1 and message.embeds[0].description.startswith('Welcome to Hangman'):
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

        m = ''
        while json_check(game):
            try:
                m = await bot.wait_for('message', check=check, timeout=30)
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


def find_json(user):
    for i in games:
        if i['player1'] == user or i['player2'] == user:
            return i
    return ''


async def generate_hangman_message(json):
    global games
    s = f"<@{json['player' + str(json['turn'])]}>\nLetters: {', '.join(json['letters'])}\nTime: 30sec\n\n**"
    count = 0
    for i in json['word']:
        if i in json['letters']:
            s += str(i).upper()
            count += 1
        elif i == ' ':
            s += '\t'
            count += 1
        else:
            s += "🔵"
    if count == len(json['word']):
        s += f"**\n**Word is guessed!**\nWinner: <@{json['player' + str(json['turn'])]}>"
        games.remove(json)
        for i in json['messages']:
            await i.edit(embed=generate_embed(i.embeds[0].description + f"\n<@{json['player' + str(json['turn'])]}> won!"))
    else:
        s += "**\n\nUse >word if you know the word\n<a:30sec:917153751465353237><a:10sec:917153782889078784>"
    return s


bot.run(TOKEN)
