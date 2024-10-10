import datetime
import ffxivweather
import csv
import discord
import math
import responses

csv_file = "data.csv"

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
def parse_nm_times(weather_list, soonest, recent, nms_embed, zone, weather, boss_name):

    curr_time = get_time_now()

    data = []

    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            data.append(row)

    # assuming it finds something
    if soonest != -1:

        # finding the time from the current moment to the next weather window
        soon_literal = parse_time_str(weather_list[soonest][2]) # this is the literal time it takes place at
        soon_time = math.floor((soon_literal - curr_time).total_seconds()) # this gets something that only contains the amount of time to the event
        soon_minutes = math.floor(soon_time / 60)

        # building output time message + the disc timestamp
        msg = f'{responses.get_disc_time(weather_list, soonest)}'

        # finding the time from recent weather window to the current moment
        if recent != -1:
            recent_literal = parse_time_str(weather_list[recent][2])
            recent_time = math.floor((curr_time - recent_literal).total_seconds() - 1400)
            recent_minutes = math.floor(recent_time / 60)
            
            recent_msg = f'{responses.get_disc_time(weather_list, recent, offset=True)}'
        else:
            recent_minutes = 0

        post_embed = False # if a new weather window is coming up
        ping_role = False # if it has been enough time for boss to 100% spawn
        needs_embed = False # whether it needs an embed

        # this is from the csv, checks whether or not something has already had an embed made
        if int(weather_list[soonest][3]) == 0:
            needs_embed = True

        # if there is less than 15 minutes to the weather and it needs embed
        if (soon_minutes < 15 and needs_embed):

            embed_msg = f'Upcoming: {msg}'
            if recent != -1:
                embed_msg += f'\nRecent: {recent_msg}'

            nms_embed.add_field(name=f'{boss_name} Soon', value=f'{embed_msg}', inline = False)
            post_embed = True

        # if there has been an hour and 36 minutes since the last one
        # reasoning: the minutes calculated stem from the end of a window, typically bosses spawn at the beginning of a window (24 minutes earlier)
        # therefore: it has usually been two hours since the last one
        if (soon_minutes < 15 and needs_embed and recent_minutes >= 96):
            ping_role = True

        if post_embed:

            fields = ['zone','weather','time','pinged']

            # updating csv information
            for row in data:
                if f"{row[0]}" == f"{zone}" and f"{row[1]}" == f"{weather}" and f"{row[2]}" == f"{weather_list[soonest][2]}":
                    row[3] = 1
                    break

            # write to the csv
            with open(csv_file, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields)
                csvwriter.writerows(data)

    return nms_embed, post_embed, ping_role


# checker for creating embeds
def check_near_event(weather_arr):

    nms_embed = discord.Embed(
            title = 'NM ALERT',
            description = 'Notorius Monster Approaching!',
            color = discord.Color.red(),
            timestamp = (datetime.datetime.now())
    )

    # just keeps track of whether or not something needs to be done
    embed_post = False
    ping_post = False

    for weather in weather_arr:
        weather_list, current, soonest, recent = check_weather(weather[0], weather[1])
        nms_embed, posting, pinging = parse_nm_times(weather_list, soonest, recent, nms_embed, weather[0], weather[1], weather[2])
        
        if posting:
            embed_post = True
        if pinging:
            ping_post = True

    return nms_embed, embed_post, ping_post


# status shown on the bot
def status_updater(zone, weather):
    
    weather_list, current, soonest, recent = check_weather(zone, weather)

    curr_time = get_time_now()

    # finding next event
    if soonest != -1:
        soon_literal = parse_time_str(weather_list[soonest][2]) # this is the literal time it takes place at
        soon_time = math.floor((soon_literal - curr_time).total_seconds()) # this gets something that only contains the amount of time to the event
        soon_minutes = math.floor(soon_time / 60)
    else:
        soon_minutes = '?' # if no upcoming

    # finding the time from recent weather window to the current moment
    if recent != -1:
        recent_literal = parse_time_str(weather_list[recent][2])
        recent_time = math.floor((curr_time - recent_literal).total_seconds() - 1400)
        recent_minutes = math.floor(recent_time / 60)
    else:
        recent_minutes = '?'

    ongoing = False

    if current != -1:
        ongoing = True

    return soon_minutes, recent_minutes, ongoing

# todo : clean up and testing -- current time needs to be added to by 24 minutes
# fixing all the problems of not accounting for missing previous data AND future data i.e. checking for -1 indexes !
# adding another data file for the 'guilds' it joins, adding a join message, channel data, setup.. etc etc

# for the main edited embed message
# passes in a list formatted such as [[zone, weather, boss_name], [zone, weather, boss_name], ...]
def message_updater(weather_arr):

    main_embed = discord.Embed(
        title = 'Weather Window Schedule',
        description = 'Updates every minute.',
        color = discord.Color.purple(),
        timestamp = (datetime.datetime.now())
    )

    for weather in weather_arr:

        weather_list, current, soonest, recent = check_weather(weather[0], weather[1])

        embed_content = ''

        if current != -1:
            timestamp_now = responses.get_disc_time(weather_list, current, offset=True)
            embed_content += f'Currently ongoing, gone {timestamp_now}!\n'

        if soonest != -1:
            timestamp_soon = responses.get_disc_time(weather_list, soonest)
            embed_content += f'Upcoming: {timestamp_soon}\n'

        if recent != -1:
            timestamp_recent = responses.get_disc_time(weather_list, recent, offset=True)
            embed_content += f'Recent: {timestamp_recent}\n'

        # cutting off the last '\n'
        str_length = len(embed_content)
        if str_length > 1:
            embed_content = embed_content[:(str_length-1)]

        # eureka -> 7: slices out 'Eureka '
        main_embed.add_field(name=f'{weather[0][7:]} {weather[1]}', value=f'{embed_content}', inline = False)

    return main_embed