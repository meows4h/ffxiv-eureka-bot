import discord
from discord.ext import tasks, commands
import responses
import eureka
import csv

async def send_message(message, user_message, is_private):
    try:
        response, embed = responses.get_response(message, user_message)

        if embed != None:
            await message.author.send(response, embed=embed) if is_private else await message.channel.send(response, embed=embed)
        else:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():

    # token and intents
    with open('token.txt') as token_file:
        TOKEN = token_file.read()

    print(TOKEN)

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # on start
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        game = discord.Game('Eureka Data Coming Online...')
        await client.change_presence(status=discord.Status.idle, activity=game)

        try:
            subroutine_loop.start()
            # maybe include a send message to a particular channel, then edit that embed with updated time stamps as time periods pass.
            # the intital send is here, the update is in the loop
            # if the last message sent is from the bot, delete it
            print("Subroutine started.")
        except:
            subroutine_loop.cancel()
            print("Subroutine stopped.")

        try:
            check_loop.start()
            print("Check started.")
        except:
            check_loop.cancel()
            print("Check stopped.")
    
    @tasks.loop(minutes=24)
    async def subroutine_loop():
        eureka.call_update()

    @tasks.loop(minutes=1)
    async def check_loop():
        # crab, last_crab = eureka.status_updater('Fog', 'Eureka Pagos')
        # cass, last_cass = eureka.status_updater('Blizzards', 'Eureka Pagos')
        # skoll, last_skoll = eureka.status_updater('Blizzards', 'Eureka Pyros')
        # await client.change_presence(status=discord.Status.idle, activity=f'Pagos Fog in {crab}m (+{last_crab}m) | Pagos Blizz in {cass}m (+{last_cass}m) | Pyros Blizz in {skoll}m (+{last_skoll}m)')
        embed, check = eureka.check_near_event()
        if check:
            channel = client.get_channel(1276792993809961041)
            await channel.send(embed=embed)


    @client.event
    async def on_message(message):

        # checks to not respond to self or bots
        if message.author == client.user or message.author.bot == True:
            return
        
        # gather info
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        # command and ping check.
        if channel == 'Direct Message with Unknown User':
            await send_message(message, user_message, is_private=True)
        else:
            if '~meow ' in user_message:
                user_message = user_message[6:]
                print(user_message)
                await send_message(message, user_message, is_private=False)
            elif '<@1254202562606006373>' in user_message:
                user_message = user_message.replace('<@1254202562606006373>', '')
                if user_message[0] == ' ':
                    user_message = user_message[1:]
                if user_message[len(user_message)-1] == ' ':
                    user_message = user_message[:len(user_message)-1]
                if '  ' in user_message:
                    user_message = user_message.replace('  ', ' ')
                await send_message(message, user_message, is_private=False)

    # runs
    client.run(TOKEN)
