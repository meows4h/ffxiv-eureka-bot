import discord
from discord.ext import tasks, commands
import responses
import eureka
import csv

# for main embed, global variable that can be updated
list_of_weather = [['Eureka Pagos', 'Fog'], ['Eureka Pagos', 'Blizzards'], ['Eureka Pyros', 'Blizzards']]

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


        # maybe include a send message to a particular channel, then edit that embed with updated time stamps as time periods pass.
        # the intital send is here, the update is in the loop
        # if the last message sent is from the bot, delete it

        channel = client.get_channel(1276792993809961041)
        async for message in channel.history(limit=50):
            if message.author == client.user:
                message.delete()
                break
        
        main_embed = eureka.message_updater(list_of_weather)

        await channel.send(embed=main_embed)

        try:
            subroutine_loop.start()
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

    # this loop manages the embeds that notify when Notorius Monsters may be spawning as well as updating the status message, every minute
    @tasks.loop(minutes=1)
    async def check_loop():

        # getting all relevant weather information, minutes to next, minutes from last, and whether one is ongoing
        crab, last_crab, curr_crab = eureka.status_updater('Eureka Pagos', 'Fog')
        cass, last_cass, curr_cass = eureka.status_updater('Eureka Pagos', 'Blizzards')
        skoll, last_skoll, curr_skoll = eureka.status_updater('Eureka Pyros', 'Blizzards')

        # creating an array to iterate through
        weather_status_array = [[crab, last_crab, curr_crab, 'Pagos', 'Fog'], [cass, last_cass, curr_cass, 'Pagos', 'Blizzards'], [skoll, last_skoll, curr_skoll, 'Pyros', 'Blizzards']]

        # creating the message to pass as the status based on the array
        status_message = ''
        for idx, array in enumerate(weather_status_array):
            if array[2] == True:
                status_message += f'{array[3]} {array[4]} right now! (-{array[0]}m) (+{array[1]}m) | '
            else:
                status_message += f'{array[3]} {array[4]} in {array[0]}m (+{array[1]}m) | '

            # removing the last divider that is added on (the | )
            if idx >= len(weather_status_array) - 1:
                message_len = len(status_message)
                status_message = status_message[:(message_len-3)]

        # update status message
        game_status = discord.Game(status_message)
        await client.change_presence(status=discord.Status.idle, activity=game_status)

        # alert embed
        embed, check = eureka.check_near_event()
        # commented out for trying main embed thing
        # if check:
        #     channel = client.get_channel(1276792993809961041)
        #     await channel.send(embed=embed)

        # main embed
        channel = client.get_channel(1276792993809961041)
        main_embed = eureka.message_updater(list_of_weather)
        async for message in channel.history(limit=50):
            if message.author == client.user:
                message.edit(embed=main_embed)
                break


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
