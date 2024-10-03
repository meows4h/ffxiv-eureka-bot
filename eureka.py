import datetime
import ffxivweather
import csv
import discord
import math
import responses

csv_file = "past3hr.csv"

# calls to update the csv file
def call_update():

    # zone, weather, time
    fields = []
    data = []

    current_time = datetime.datetime.now()
    pending_del = []

    # reading all the csv file info
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            data.append(row)

    # removes stuff from over 20 hrs ago
    for idx, row in enumerate(data):
        # print(row)

        starting_time = parse_time_str(row[2])

        if (current_time - starting_time).total_seconds() / 3600 > 20:
            pending_del.append(idx)

    # deleting
    for idx in reversed(pending_del):
        data.pop(idx)

    pagos = 'Eureka Pagos'
    pyros = 'Eureka Pyros'

    # pagos weather
    pagos_weather = ffxivweather.forecaster.get_forecast(place_name=pagos, count=25)
    for weather, start_time in pagos_weather:
        found = False
        for row in data:
            if f"{row[0]}" == f"{pagos}" and f"{row[1]}" == f"{weather['name_en']}" and f"{row[2]}" == f"{start_time}":
                found = True
                break
        
        if not found:
            data.append([pagos,weather["name_en"],start_time,0])

    # pyros weather
    pyros_weather = ffxivweather.forecaster.get_forecast(place_name=pyros, count=25)
    for weather, start_time in pyros_weather:
        found = False
        for row in data:
            if f"{row[0]}" == f"{pyros}" and f"{row[1]}" == f"{weather['name_en']}" and f"{row[2]}" == f"{start_time}":
                found = True
                break

        if not found:
            data.append([pyros,weather["name_en"],start_time,0])

    # write to the csv
    with open(csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(data)

# getting time now
def get_time_now():
    return datetime.datetime.utcnow()

# parses time
def parse_time_str(time_str):
    return datetime.datetime.fromisoformat(time_str)

# check weather
def check_weather(zone, weather):

    data = []
    current_time = get_time_now()

    # reading the data that has been pulled and putting into an iterative format
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader) # skipping a row ?
        for row in csvreader:
            data.append(row)

    list_weather = []

    for idx, row in enumerate(data):

        # finding matching weather in the zone and putting it into the list
        if f"{row[0]}" == f"{zone}" and f"{row[1]}" == f"{weather}":
            list_weather.append(data[idx])

    # setting up indicies
    current = -1
    soonest = -1
    recent = -1

    # finding when the most recent, current, and next one are
    for idx, row in enumerate(list_weather):

        # parsing into a operable format
        starting_time = parse_time_str(row[2])

        if 0 > (starting_time - current_time).total_seconds() > -1400:
            current = idx

        if -1400 >= (starting_time - current_time).total_seconds():
            recent = idx

        if (starting_time - current_time).total_seconds() >= 0 and soonest == -1:
            soonest = idx

    return list_weather, current, soonest, recent

# parsing data into embeds
def parse_nm_times(weather_list, soonest, recent, data, monster_list, nms_embed, boss_name, zone, weather):

    curr_time = get_time_now()

    monster = False

    # assuming it finds something
    if soonest != -1:

        # realized there is unintended behvaior when no recent weather window can be found, instead takes the last point of data (at index -1); bandaid fix for now
        if recent == -1:
            recent = soonest

        # finding the time from the current moment to the next weather window
        literal_time = parse_time_str(weather_list[soonest][2]) # this is the literal time it takes place at
        weather_time = math.floor((literal_time - curr_time).total_seconds()) # this gets something that only contains the amount of time to the event

        seconds = weather_time % 60
        minutes = math.floor(weather_time / 60) % 60
        hours = math.floor((weather_time / 60) / 60)

        # building output time message + the disc timestamp
        msg = f'{responses.get_disc_time(weather_list, soonest)}'

        # finding the time from recent weather window to the current moment
        check_time = math.floor((curr_time - parse_time_str(weather_list[recent][2])).total_seconds() - 1400)
        recent_seconds = check_time % 60
        recent_minutes = math.floor(check_time / 60) % 60
        recent_hours = math.floor((check_time / 60) / 60)
        
        recent_msg = f'{responses.get_disc_time(weather_list, recent)}'

        pinged = False
        ping_role = False

        if (minutes < 15 and hours == 0 and int(weather_list[soonest][3]) == 0) and (recent_hours >= 2 or (recent_hours >= 1 and recent_minutes >= 45)):
            nms_embed.add_field(name=f'For Sure {boss_name} Soon', value=f'Upcoming: {msg}\nRecent: {recent_msg}', inline = False)
            pinged = True
            ping_role = True
        elif (minutes < 15 and hours == 0 and int(weather_list[soonest][3]) == 0):
            nms_embed.add_field(name=f'Possible {boss_name} Soon', value=f'Upcoming: {msg}\nRecent: {recent_msg}', inline = False)
            pinged = True

        # does this even work...? should recheck before updating
        if ping_role:
            nms_embed.add_field(name=f'ping!', value=f'<@207194133717057538>', inline=False)

        if pinged:

            monster = True

            for row in data:
                if f"{row[0]}" == f"{zone}" and f"{row[1]}" == f"{weather}" and f"{row[2]}" == f"{weather_list[soonest][2]}":
                    row[3] = 1
                    break

            fields = ['zone','weather','time','pinged']

            # write to the csv
            with open(csv_file, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields)
                csvwriter.writerows(data)

    monster_list.append(monster)
    return data, nms_embed, monster_list

# checker
def check_near_event():

    monster_list = []

    nms_embed = discord.Embed(
            title = 'NM ALERT',
            description = 'Notorius Monster Approaching!',
            color = discord.Color.red(),
            timestamp = (datetime.datetime.now())
    )

    data = []

    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            data.append(row)

    pagos_fog, c_pagos_fog, s_pagos_fog, r_pagos_fog = check_weather('Eureka Pagos', 'Fog')
    pagos_blizz, c_pagos_blizz, s_pagos_blizz, r_pagos_blizz = check_weather('Eureka Pagos', 'Blizzards')
    pyros_blizz, c_pyros_blizz, s_pyros_blizz, r_pyros_blizz = check_weather('Eureka Pyros', 'Blizzards')

    # for some reason im sure this overwrites two pings occurring at the same time, which can happen in the case of pyros vs pagos mobs
    data, nms_embed, monster_list = parse_nm_times(pagos_fog, s_pagos_fog, r_pagos_fog, data, monster_list, nms_embed, 'Crab', 'Eureka Pagos', 'Fog')
    data, nms_embed, monster_list = parse_nm_times(pagos_blizz, s_pagos_blizz, r_pagos_blizz, data, monster_list, nms_embed, 'Cassie', 'Eureka Pagos', 'Blizzards')
    data, nms_embed, monster_list = parse_nm_times(pyros_blizz, s_pyros_blizz, r_pyros_blizz, data, monster_list, nms_embed, 'Skoll', 'Eureka Pyros', 'Blizzards')

    if True in monster_list:
        monster = True
    else:
        monster = False

    return nms_embed, monster

# todo
def status_updater(weather, zone):
    
    data = []

    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            data.append(row)
    
    weather_list, current, soonest, recent = check_weather(zone, weather)
