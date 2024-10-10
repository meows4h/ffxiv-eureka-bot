# FFXIV Eureka Bot -- 'CassBot'

'CassBot' refers to one of the bosses this project encompasses, 'Copycat Cassie'.

This is not as much of an application to use as much as it is something to show off in terms of functionality. If you wish to use my code, fork this project.

## Functions
- Interacts with a FFXIV weather API in order to parse through data to understand what is happening when as well as keeping a backlog of events
- Automatically alert to a specific Discord channel when a weather window containing a noteable boss is within the next 15 minutes, displaying time since last one
- Can display time to next weather window, time since last, as well as if there is currently an ongoing weather window with timezone sensitive timestamps
- Status updates every minute to show upcoming weather timings, including time since the previous one

## Files
- bot.py : Holds general bot operations, loops, and basic async functionality
- eureka.py : Holds all functions and commands that are used for the purposes of generating and updating Eureka data
- responses.py : Holds all functions and commands that are used for creating messages to be output to Discord
- main.py : The run command to start the app within bot.py
- past3hr.csv : CSV file that contains all the weather data (placeholder header columns in this case), enables "time since" functionality

## Work in Progress
- Update embed with next windows in active time rather than making new popups every single time
- Keep a list of channel ids to post to as well as developing a means of cataloging users to utilize the service
- Pinging a user or role when two hours have elapsed since the last time a weather window has ocurred and it is coming up soon
