import random
import math
import eureka
import datetime as date_time
import discord
from datetime import timedelta

def get_disc_time(weather_list, idx, offset=False):

    dt = eureka.parse_time_str(weather_list[idx][2])

    if offset:
        dt += timedelta(seconds=1400)

    timestamp = f'<t:{round((dt - date_time.datetime(1970, 1, 1)) / timedelta(seconds=1))}:R>'
    
    return timestamp


def make_embed(zone, weather):

    eureka.call_update()
    weather_list, current, soonest, recent = eureka.check_weather(zone, weather)

    embed = discord.Embed(
            title = f'{weather} in {zone}',
            #description = 'Showing data for last 20 hours.',
            color = discord.Color.greyple(),
            timestamp = (date_time.datetime.now())
    )
    embed.set_footer(text=f'\u200b')

    if current != -1:

        timestamp = get_disc_time(weather_list, current)
        curr_msg = f' {timestamp}'

        embed.add_field(name=f'Current {weather}', value=curr_msg, inline=False)
        
    if soonest != -1:

        timestamp = get_disc_time(weather_list, soonest)
        soon_msg = f' {timestamp}'

        embed.add_field(name=f'Next {weather}', value=soon_msg, inline = False)

    if recent != -1:

        timestamp = get_disc_time(weather_list, recent)
        last_msg = f' {timestamp}'

        embed.add_field(name=f'Last {weather}', value=last_msg, inline=False)

    return embed

def get_response(msg_data, message: str) -> str:
    p_message = message.lower()
    
    if p_message == '!cass' or p_message == 'cass':

        cass_embed = make_embed('Eureka Pagos', 'Blizzards')

        return '', cass_embed

    if p_message == '!crab' or p_message == 'crab':

        crab_embed = make_embed('Eureka Pagos', 'Fog')

        return '', crab_embed

    if p_message == '!skoll' or p_message == 'skoll':

        skoll_embed = make_embed('Eureka Pyros', 'Blizzards')

        return '', skoll_embed