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
        # Create an empty JSON file if it does not exist
        with open('employee_data.json', 'w') as file:
            json.dump({}, file)
        return {}

    with open('employee_data.json', 'r') as file:
        return json.load(file)

# Save data to JSON file
def save_data(data):
    with open('employee_data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Set up bot with command prefix
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='/', intents=intents)

# Global variable to store employee contributions
employee_data = load_data()

@bot.event
async def on_ready():
    print(f'Prisijungta kaip {bot.user}')

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

    await ctx.send(f'Sėkmingai užregistruota {amount} vnt. „{item_name}“.')  # Confirmation message

@bot.command()
async def atlyginimas(ctx):
    if not employee_data:
        await ctx.send("Nėra užregistruotų indėlių.")  # No contributions recorded
        return

    contributions = "Darbuotojų indėliai:\n"  # Employee Contributions
    for user_id, data in employee_data.items():
        contributions += f'<@{user_id}>:\n'
        for item_name, amount in data["items"].items():
            contributions += f'  {item_name}: {amount}\n'  # Adjusted formatting

    await ctx.send(contributions)

@bot.command()
@commands.has_any_role("Pavaduotoja", "Direktorius")  # Allow users with "Pavaduotoja" or "Direktorius" roles
async def ismoketi(ctx):
    global employee_data
    employee_data = {}
    save_data(employee_data)
    await ctx.send("Visi indėliai sėkmingai atstatyti.")  # Reset confirmation

@ismoketi.error
async def ismoketi_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Neturite teisės naudoti šio komandos.")  # Missing permissions
    else:
        await ctx.send("Įvyko klaida, bandant atstatyti duomenis.")  # General error

@darbas.error
async def darbas_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Prašome įvesti galiojantį sveikąjį skaičių.")  # Invalid amount message
    else:
        await ctx.send("Įvyko klaida registruojant prekę.")  # Error while logging the item

@bot.event
async def on_command_error(ctx, error):
    await ctx.send("Įvyko nenumatyta klaida. Prašome bandyti dar kartą.")  # Unexpected error

# Run the bot with the token from the environment variables
bot.run(os.getenv('DISCORD_TOKEN'))

