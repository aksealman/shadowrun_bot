#!/usr/bin/python3
#TODO user logging
#TODO start.py should only contain the bot configuration and launch logic. Need to seperate command logic
import discord
from discord.ext import commands
import sys
import asyncio
import random
from random import randint
from config_parser import config_parse
import consts

config_values=config_parse()
fchan=None
version_info=0.1
#cmd list roll,info, exit, help 
CMD_LIST={
          "help": "Usage: {0}help Description: Displays this text".format(config_values[consts.command_prefix_key]),
          "info": "Usage: {0}info Description: Displays author, version info and source code links".format(config_values[consts.command_prefix_key]),
          "exit": "Usage: {0}exit Description: Exits the bot, can only be ran by owner of the bot".format(config_values[consts.command_prefix_key]),
          "roll": "Usage: {0}roll X <Y> Description: Rolls X dice, and counts all \"hits\" aka rolls of 5 or 6 on the dice. If edge <Y> parmater is provided then will re-roll all 6's and continue to cumulate hits.".format(config_values[consts.command_prefix_key])
         }


class WrongChan(commands.CheckFailure):
    pass

def rollin(dice_num, curr_hits, compute_edge):
    #Base case
    if dice_num==0:
        return "Number of hits for your roll is {0}".format(curr_hits)
    dice_str="("
    edge_ctr=0
    hit_ctr=curr_hits
    for loop_iter in range(0, dice_num):
        num = random.randint(1,6)
        dice_str+=str(num)
        if loop_iter==dice_num-1:
            dice_str+=")\n"
        else:
            dice_str+=","
        if num == 5 or num == 6:
            hit_ctr += 1
        if num == 6 and compute_edge: 
            edge_ctr+=1
    dice_str+=rollin(edge_ctr, hit_ctr, compute_edge)
    return dice_str
#Could also just manage permissions for the bot, on the discord channel but I think this is cooler

bot = commands.Bot(command_prefix=config_values[consts.command_prefix_key])
print(str(discord.__version__))

#TODO look into refining the random seed.
random.seed()

#Remove the default help command
bot.remove_command('help')

@bot.event
async def on_ready():
    global fchan
    for chan in bot.get_all_channels():
        if str(chan.name) == config_values[consts.channel_name_key]:
            fchan = chan
            break
    if fchan == None:
        print("Unable to find channel {0} in discord server exiting".format(config_values[consts.channel_name_key]))
        sys.exit()  
    await bot.send_message(fchan, consts.MTOD)
    
#TODO find a way to clean this up
@bot.event
async def on_command_error(error, ctx):
    global fchan
    if isinstance(error, type(commands.errors.CommandNotFound())):
        await bot.send_message(fchan, "Invalid Command, please check **{0}help** for list of valid commands".format(config_values[consts.command_prefix_key]))
    elif isinstance(error, type(commands.errors.CommandInvokeError(discord.errors.HTTPException))):
        await bot.send_message(fchan,"Likely roll overflow detected, please try again with lower number")
        #TODO this is far more accurate, probally need a function that just handles type of error
        #if type(error.original) == type(discord.errors.HTTPException):
            #await bot.send_message(fchan, "Likely roll overflow detected, please try again with lower number")
    elif isinstance(error, type(WrongChan())):
        pass
    else:
        raise error

@bot.check
def is_channel(ctx):
   if not (str(ctx.message.channel) == config_values[consts.channel_name_key]):
       raise WrongChan()
   return True


@bot.command(pass_context=True)
async def roll(ctx, num_dice : int, edge=None):
    edge_compute=edge != None
    await bot.say(rollin(num_dice, 0, edge_compute))

#TODO is authoer check
@bot.command()
async def exit():
    print("Exiting bot")
    sys.exit()

@bot.command()
#Author/Source
async def info():
    await bot.say("Shadowrun Bot version {0} created by aksealboy source at :<github here>".format(version_info))    

#TODO help <cmd>
@bot.command()
async def help():
    embed=discord.Embed(title="Shadowrun Bot Help Command", description="The help command")
    for key, c_value in CMD_LIST.items():
        embed.add_field(name=key, value=c_value, inline=True)
    await bot.say(embed=embed)

#TODO suggest command

def main():
    #TODO if we want to keep exit, without huge amounts of stacktrace puke we need
    #more refined control so cannot use bot.run waiting for SystemExit Exception
    bot.run(config_values[consts.bot_token_key])

if __name__ == "__main__":
        main()
