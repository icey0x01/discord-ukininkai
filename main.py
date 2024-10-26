import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load data from JSON file
def load_data():
    if not os.path.exists('employee_data.json'):
        return {}
    with open('employee_data.json', 'r') as file:
        return json.load(file)

# Save data to JSON file
def save_data(data):
    with open('employee_data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Set up bot with command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Global variable to store employee contributions
employee_data = load_data()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def darbas(ctx, item_name: str, amount: int):
    user_id = str(ctx.author.id)

    # Ensure user record exists
    if user_id not in employee_data:
        employee_data[user_id] = {"items": {}}

    # Log item
    if item_name in employee_data[user_id]["items"]:
        employee_data[user_id]["items"][item_name] += amount
    else:
        employee_data[user_id]["items"][item_name] = amount

    # Save data
    save_data(employee_data)

    await ctx.send(f'Successfully logged {amount} units of "{item_name}".')

@bot.command()
async def atlyginimas(ctx):
    if not employee_data:
        await ctx.send("No contributions recorded.")
        return

    contributions = "Employee Contributions:\n"
    for user_id, data in employee_data.items():
        contributions += f'<@{user_id}>:\n'
        for item_name, amount in data["items"].items():
            contributions += f'  - {item_name}: {amount}\n'
    
    await ctx.send(contributions)

@bot.command()
async def reset(ctx):
    global employee_data
    employee_data = {}
    save_data(employee_data)
    await ctx.send("All contributions have been successfully reset.")

@darbas.error
async def darbas_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Please enter a valid integer for amount.")
    else:
        await ctx.send("An error occurred while logging the item.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send("An unexpected error occurred. Please try again.")

# Replace 'YOUR_BOT_TOKEN' with your bot's token from environment variables
bot.run(os.getenv('DISCORD_TOKEN'))

