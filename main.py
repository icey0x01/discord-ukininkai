import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import random
# Load environment variables from .env file
load_dotenv()


ITEM_VALUES = {
    "parduota-sultys": 5,
    "apelsinai": 0.1,
    "sultys": 1.66, # Add other items here with their respective values if needed
    "salotos": 0.1,
    "moliugai": 0.1,
    "pomidorai": 0.1,
    "grudai": 0.01,
    "avietes": 0.1,
    "pienas":0.1,
    "svogunai":0.1,
    "siuksles":0.05,
    "miltai":0.25
}



ITEM_PRICE = {
    "parduota-sultys": 0,
    "apelsinai": 60,
    "sultys": 375, # Add other items here with their respective values if needed
    "salotos": 70,
    "moliugai": 50,
    "pomidorai": 50,
    "grudai": 18,
    "avietes": 50,
    "pienas": 70,
    "svogunai":70,
    "siuksles": 0,
    "miltai": 25
}


LOTTERY_PRICE = 500

# Probability
PRIZES = ["$1 000 000","$100 000", "$10 000", "3 rinkinukus", "3 vaistineles"]
WEIGHTS = [1, 4, 25, 35, 35]

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


def load_coin_data():
    if not os.path.exists('coin_data.json'):
        with open('coin_data.json', 'w') as file:
            json.dump({}, file)
        return {}
    with open('coin_data.json', 'r') as file:
        return json.load(file)

def save_coin_data(data):
    with open('coin_data.json', 'w') as file:
        json.dump(data, file, indent=4)


# Set up bot with command prefix
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='/', intents=intents)

# Global variable to store employee contributions
employee_data = load_data()
coin_data = load_coin_data()

@bot.event
async def on_ready():
    print(f'Prisijungta kaip {bot.user}')

@bot.command()
async def darbas(ctx, item_name: str, amount: int):
    user_id = str(ctx.author.id)
    item_value = ITEM_VALUES.get(item_name.lower())

    if item_value is not None:
        coin_change = item_value * amount
        user_balance = coin_data.get(user_id, {}).get("balansas", 0)
        new_balance = user_balance + coin_change
        coin_data[user_id] = {"balansas": round(new_balance, 3)} 
        save_coin_data(coin_data)
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
async def skaiciuoti(ctx):
    if not employee_data:
        await ctx.send("Nera atliktu darbu.")
        return
    summary = "Atlyginimu suvestine: \n"
    for user_id, data in employee_data.items():
        summary += (f'<@{user_id}> atlyginimas:\n')
        sum = 0
        for item_name, item_amount in data["items"].items():
            salary_per_item = ITEM_PRICE.get(item_name, 0) * item_amount
            sum += salary_per_item
            summary+=f'{item_name} : {salary_per_item}\n'
        summary+=f'Bendra Suma: {sum}\n'   
    await ctx.send(summary) 


@bot.command()
@commands.has_any_role("Pavaduotoja", "Direktorius")  # Allow users with "Pavaduotoja" or "Direktorius" roles
async def ismoketi(ctx):
    global employee_data
    employee_data = {}
    save_data(employee_data)
    await ctx.send("Visi indėliai sėkmingai atstatyti.")  # Reset confirmation

@bot.command()
async def balansas(ctx):
    user_id = str(ctx.author.id)
    balance = coin_data.get(user_id, {}).get("balansas", 0)
    await ctx.send(f"Jūsų RanchCoin balansas yra: {balance} monetų.")

@balansas.error
async def balansas_error(ctx, error):
    await ctx.send("Ivyko klaida, bandant gauti balansa")

@bot.command()
async def loterija(ctx):
    user_id = str(ctx.author.id)
    user_balance = coin_data.get(user_id,{}).get("balansas",0)

    if user_balance >= LOTTERY_PRICE:
        new_balance = user_balance - LOTTERY_PRICE
        coin_data[user_id] = {"balansas": round(new_balance, 3)} 
        prize = random.choices(PRIZES, weights=WEIGHTS, k=1)[0]
        save_coin_data(coin_data)
        await ctx.send(f"Sveikiname laimejai {prize}! <3")
    else:
        await ctx.send(f"Nepakanka lėšų dalyvauti loterijoje. Reikia {LOTTERY_PRICE} RanchCoin. O turi {user_balance} ")

@bot.command()
@commands.has_any_role("Pavaduotoja", "Direktorius")  # Allow users with "Pavaduotoja" or "Direktorius" roles
async def dovana(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("Kiekis turi būti teigiamas skaičius")
        return
    user_id = str(member.id)
    user_balance = coin_data.get(user_id, {}).get("balansas", 0)

    # Add the specified amount to the user's balance
    new_balance = user_balance + amount
    coin_data[user_id] = {"balansas": new_balance}
    save_coin_data(coin_data)
    await ctx.send(f"Sėkmingai pridėta {amount} RanchCoins vartotojui {member.display_name}. Naujas balansas: {new_balance} RanchCoins.")



@skaiciuoti.error
async def skaiciuoti_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Neturite teisės naudoti šio komandos.")  # Missing permissions
    else:
        await ctx.send("Įvyko klaida, bandant atstatyti duomenis.")  # General error

@dovana.error
async def dovana_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Neturite teisės naudoti šio komandos.")  # Missing permissions
    else:
        await ctx.send("Įvyko klaida, bandant atstatyti duomenis.")  # General error

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

