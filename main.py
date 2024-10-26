import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv  # Import for loading .env files

# Load environment variables from .env file if present
load_dotenv()

# Get the bot token from an environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Load employee work data if it exists
if os.path.exists("employee_data.json"):
    with open("employee_data.json", "r") as f:
        employee_data = json.load(f)
else:
    employee_data = {}

# Command for employees to log collected items
@bot.command(name="darbas")
async def add_work(ctx, item_name: str, amount: int):
    employee = str(ctx.author)
    if employee not in employee_data:
        employee_data[employee] = []
    # Add the work entry for this employee
    employee_data[employee].append({"item": item_name, "amount": amount})
    save_employee_data()  # Save data after adding entry
    await ctx.send(f"{employee} added {amount} of {item_name}.")

# Command for employer to check all employee contributions
@bot.command(name="atlyginimas")
async def calculate_salaries(ctx):
    if not employee_data:
        await ctx.send("No data to display.")
        return
    
    report = "Items to be paid:\n"
    for employee, entries in employee_data.items():
        report += f"\n**{employee}**\n"
        for entry in entries:
            report += f"{entry['amount']} of {entry['item']}\n"
    
    await ctx.send(report)

# Command to reset employee contributions (e.g., after paying salaries)
@bot.command(name="reset")
async def reset_data(ctx):
    global employee_data
    employee_data = {}
    save_employee_data()
    await ctx.send("All employee contributions have been reset.")

def save_employee_data():
    with open("employee_data.json", "w") as f:
        json.dump(employee_data, f)

# Run the bot with the token from the environment
bot.run(TOKEN)

