import random
import math
import eureka
import datetime as date_time
import discord
from datetime import timedelta

def get_disc_time(weather_list, idx):

    dt = eureka.parse_time_str(weather_list[idx][2])
    timestamp = f'<t:{round((dt - date_time.datetime(1970, 1, 1)) / timedelta(seconds=1))}:R>'
    
    return timestamp


def make_embed(zone, weather):

    eureka.call_update()
    current_time = eureka.get_time_now()
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
        curr_msg2 = f' {timestamp}'

        curr_time = math.floor((eureka.parse_time_str(weather_list[current][2]) - current_time).total_seconds() + 1400)

        curr_sec = curr_time % 60
        curr_min = math.floor(curr_time / 60) % 60
        curr_hour = math.floor((curr_time / 60) / 60)

        curr_msg = ''

        if curr_hour > 0:
            curr_msg += f'{curr_hour} hours, '
        if curr_min > 0:
            curr_msg += f'{curr_min} minutes, '
        if curr_sec >= 0:
            curr_msg += f'{curr_sec} seconds left.'

        embed.add_field(name=f'Current {weather}', value=curr_msg2, inline=False)
        
    if soonest != -1:

        timestamp = get_disc_time(weather_list, soonest)
        soon_msg2 = f' {timestamp}'

        soon_time = math.floor((eureka.parse_time_str(weather_list[soonest][2]) - current_time).total_seconds())

        soon_sec = soon_time % 60
        soon_min = math.floor(soon_time / 60) % 60
        soon_hour = math.floor((soon_time / 60) / 60)

        soon_msg = ''

        if soon_hour > 0:
            soon_msg += f'{soon_hour} hours, '
        if soon_min > 0:
            soon_msg += f'{soon_min} minutes, '
        if soon_sec >= 0:
            soon_msg += f'{soon_sec} seconds.'

        embed.add_field(name=f'Next {weather}', value=soon_msg2, inline = False)

    if recent != -1:

        timestamp = get_disc_time(weather_list, recent)
        last_msg2 = f' {timestamp}'

        last_time = math.floor((current_time - eureka.parse_time_str(weather_list[recent][2])).total_seconds() - 1400)

        last_sec = last_time % 60
        last_min = math.floor(last_time / 60) % 60
        last_hour = math.floor((last_time / 60) / 60)

        last_msg = ''

        if last_hour > 0:
            last_msg += f'{last_hour} hours, '
        if last_min > 0:
            last_msg += f'{last_min} minutes, '
        if last_sec >= 0:
            last_msg += f'{last_sec} seconds ago.'

        embed.add_field(name=f'Last {weather}', value=last_msg2, inline=False)

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