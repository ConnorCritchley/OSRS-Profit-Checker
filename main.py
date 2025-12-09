import requests
import time
import json
import os.path

ENDPOINT = "https://prices.runescape.wiki/api/v1/osrs/latest"

# Define headers to include the 'User-Agent', customize if you wish
headers = {'User-Agent': 'Personal Money Methods Checker'}

# Fetch the current price for an item by its ID.
def fetch_item_price(id):
    params = {'id': id}
    response = requests.get(ENDPOINT, params=params, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        try:
            # Response is high and low recent trades
            high = response_data['data'][str(id)]['high']
            low = response_data['data'][str(id)]['low']
            # Calculate the average price
            average_price = (high + low) / 2
            return average_price
        except KeyError:
            print(f"Error: Missing data for item ID {id}")
            return None
    else:
        print(f"Error: API request failed for item ID {id} with status {response.status_code}")
        return None

# Process the items, calculate the profit, and return the results.
def process_items(data):
    # List to store item data with name, current, and previous prices
    item_data = []
    
    # List of calculated profits
    profit_data = []
    
    # Loop through the data to process items
    for item in data["items"]:
        for name, details in item.items():
            item_id = details["id"]
            previous_price = details["previous"]
            
            # Fetch current price from the API
            current_price = fetch_item_price(item_id)
            
            if current_price is not None:
                # Update the previous price to the current price
                details["previous"] = current_price
                
                # Append item data (name, current price, previous price)
                item_data.append({
                    'name': name,
                    'current_price': current_price,
                    'previous_price': previous_price,
                })
        
        # Sleep for polite scraping
        time.sleep(3)

    # Profit methods must be hardcoded, but output will scale
    # 1 - Diamond necklaces (2 methods)
    profit_data.append({
        'name': "Diamond Necklace GE",
        'profit': item_data[2]['current_price'] - (item_data[0]['current_price'] + item_data[1]['current_price']),
        'prev_profit': item_data[2]['previous_price'] - (item_data[0]['previous_price'] + item_data[1]['previous_price'])
    })
    
    # High Alchemy Alternative for Diamond Necklace
    profit_data.append({
        'name': "Diamond Necklace HE",
        'profit': 2205 - (item_data[0]['current_price'] + item_data[1]['current_price'] + item_data[3]['current_price']),
        'prev_profit': 2205 - (item_data[0]['previous_price'] + item_data[1]['previous_price'] + item_data[3]['previous_price'])
    })

    # 2 - Topaz Amulet (2 methods)
    profit_data.append({
        'name': "Burning Necklace",
        'profit': item_data[5]['current_price'] - (item_data[6]['current_price'] + item_data[4]['current_price']),
        'prev_profit': item_data[5]['previous_price'] - (item_data[6]['previous_price'] + item_data[4]['previous_price'])
    })
    
    # Unfinished Amulet Alternative
    profit_data.append({
        'name': "Burning Necklace w/ Stringing",
        'profit': item_data[5]['current_price'] - (item_data[7]['current_price'] + item_data[4]['current_price'] + item_data[14]['current_price']),
        'prev_profit': item_data[5]['previous_price'] - (item_data[7]['previous_price'] + item_data[4]['previous_price'] + item_data[14]['previous_price'])
    })

    # 3 - Crystal Keys
    profit_data.append({
        'name': "Crystal Keys",
        'profit': item_data[10]['current_price'] - (item_data[9]['current_price'] + item_data[8]['current_price']),
        'prev_profit': item_data[10]['previous_price'] - (item_data[9]['previous_price'] + item_data[8]['previous_price'])
    })
    
    # 4 - Steel Bars
    profit_data.append({
        'name': "Steel Bars",
        'profit': item_data[13]['current_price'] - (item_data[12]['current_price'] + item_data[11]['current_price']),
        'prev_profit': item_data[13]['previous_price'] - (item_data[12]['previous_price'] + item_data[11]['previous_price'])
    })

    return item_data, profit_data

# Saves the previous value to the data.json file.
def update_data(data, item_data):
    # Update the 'previous' prices in the original data with the new ones
    for i, item in enumerate(data["items"]):
        for name, details in item.items():
            # Find corresponding item in item_data by name
            current_item_data = next((i for i in item_data if i['name'] == name), None)
            if current_item_data:
                # Update the 'previous' value to the current price
                details["previous"] = current_item_data['current_price']
    
    # Save the updated data back to the data.json file
    with open('./data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    print("\nResults saved to data.json")

# Main function
def main():
    # Check for data file and load it
    if os.path.isfile("./data.json"):
        with open('./data.json', 'r') as openfile:
            data = json.load(openfile)
    else:
        raise Exception("`data.json` missing!")
    
    # Process items and calculate profits
    print("Fetching prices, please wait.")
    item_data, profit_data = process_items(data)
    
    # Print profit results
    for profit in profit_data:
        # Calculate the change in profit
        profit_change = profit['profit'] - profit['prev_profit']
        
        # Set color based on whether the change is positive or negative
        if profit_change > 0:
            color = '\033[92m'  # Green for positive change
        else:
            color = '\033[91m'  # Red for negative change
        
        # Define the reset color sequence
        reset_color = '\033[0m'

        # Print the profit results with color
        print(f"{profit['name']}:")
        print(f"  Current Profit: {profit['profit']}")
        print(f"  Previous Profit: {profit['prev_profit']}")
        print(f"  Profit Change: {color}{profit_change}{reset_color}")
        print(f"  Profit Per 1k: {profit['profit'] * 1000}")
        print("-" * 40)
    
    # Ask user if they want to see all item prices
    print("\nDo you want to see all item prices? (yes/no):")
    user_input = input().strip().lower()

    if 'y' in user_input:
        print("\nItem Prices (Current and Previous):")
        print("-" * 40)
        for item in item_data:
            print(f"Item: {item['name']}")
            print(f"  Current Price: {item['current_price']}")
            print(f"  Previous Price: {item['previous_price']}")
            print("-" * 40)
    
    # Save results to file
    update_data(data, item_data)

if __name__ == '__main__':
    main()
