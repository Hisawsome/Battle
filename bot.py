# ===============================================
#                  FROM RIDI
#        Automated Battle Games Script
# ===============================================

import requests
import time
import json
import random
from datetime import datetime, timedelta

def read_accounts(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def read_tasks(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tasks": [], "last_run": "1970-01-01T00:00:00"}

def write_tasks(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def should_run_tasks(last_run):
    last_run_time = datetime.fromisoformat(last_run)
    return datetime.now() - last_run_time >= timedelta(days=1)

def fetch_tasks(api_url, authorization):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0',
        'authorization': authorization
    }
    response = requests.get(api_url, headers=headers)
    response_json = response.json()

    if "state" in response_json and response_json["state"] == "success" and "data" in response_json:
        return response_json["data"]  # Extract the task list
    else:
        print("Unexpected response format:", response_json)
        return []

def complete_task(api_url, authorization, task_id, code=None):
    task_url = f"{api_url}/{task_id}/complete"
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0',
        'authorization': authorization,
        'content-type': 'application/json'
    }
    payload = {"code": code} if code else {}
    response = requests.post(task_url, json=payload, headers=headers)
    return response.json()

def send_tap_request(auth_token, taps=1000, available_energy=1000):
    url = "https://api.battle-games.com:8443/api/api/v1/taps"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Origin": "https://tg.battle-games.com",
        "Referer": "https://tg.battle-games.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "authorization": auth_token,
        "content-type": "application/json",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }
    payload = {
        "taps": taps,
        "availableEnergy": available_energy,
        "requestedAt": int(time.time() * 1000)  # Current timestamp in milliseconds
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()


def get_cards_data(auth_header):
    url = 'https://api.battle-games.com:8443/api/api/v1/cards'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://tg.battle-games.com',
        'Referer': 'https://tg.battle-games.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'authorization': auth_header,
        'content-type': 'application/json',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def buy_card(auth_header, card_id):
    url = 'https://api.battle-games.com:8443/api/api/v1/cards/buy'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://tg.battle-games.com',
        'Referer': 'https://tg.battle-games.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'authorization': auth_header,
        'content-type': 'application/json',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    payload = {
        'cardId': card_id,
        'requestedAt': int(time.time()*1000)  # Use the current timestamp or any required value
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def calculate_best_cards(data):
    cards = data.get('data', [])
    card_ratios = []
    
    for card in cards:
        profit_per_hour = card.get('profitPerHour')
        next_level_cost = card.get('nextLevel', {}).get('cost')
        
        if profit_per_hour and next_level_cost:
            ratio = next_level_cost / profit_per_hour
            card_ratios.append((card['id'], ratio, next_level_cost))
    
    # Sort by the best cost-to-profit ratio (lowest ratio first)
    sorted_cards = sorted(card_ratios, key=lambda x: x[1])
    return sorted_cards

def process_all_accounts(auth_header, data_file='datas.txt'):
    # Read all account details
    with open(data_file, 'r') as f:
        accounts = f.readlines()
    
    for account in accounts:
        account = account.strip()
        print(f'Processing account: {account}')
        
        # Fetch the card data
        data = get_cards_data(auth_header)
        
        if data.get('state') == 'success':
            sorted_cards = calculate_best_cards(data)
            for card_id, ratio, cost in sorted_cards:
                # Here you need logic to check if the account has enough money to buy the card
                print(f'Buying card {card_id} with cost {cost} and ratio {ratio}')
                buy_card(auth_header, card_id)
        else:
            print('Error fetching card data.')

def main():
    accounts = read_accounts("datas.txt")
    tasks_data = read_tasks("tasks.txt")
    tasks_api = "https://api.battle-games.com:8443/api/api/v1/tasks"
    
    if should_run_tasks(tasks_data["last_run"]):
        print("Fetching new tasks...")
        sample_account = accounts[0]  # Use the first account to fetch tasks
        tasks_list = fetch_tasks(tasks_api, sample_account)

        if not tasks_list:
            print("No tasks found or error occurred.")
            return

        tasks_data = {
            "tasks": [{"id": t.get("id"), "code": t.get("code")} for t in tasks_list],
            "last_run": datetime.now().isoformat()
        }
        write_tasks("tasks.txt", tasks_data)
        for account in accounts:
            print(f"Using account: {account}")
            for task in tasks_data["tasks"]:
                task_id = task["id"]
                code = task["code"]
                print(f"Completing task: {task_id}")
                response = complete_task(tasks_api, account, task_id, code)
                print(response)
            time.sleep(5)  # Short delay between accounts

        


    while True:
        for account in accounts:
            print(f"Sending taps for account: {account[:30]}...")
            response = send_tap_request(account)
            print("Response:", response)
            time.sleep(1)  # Small delay between accounts
            # Fetch the card data
            data = get_cards_data(account)
            
            if data.get('state') == 'success':
                sorted_cards = calculate_best_cards(data)
                for card_id, ratio, cost in sorted_cards:
                    # Here you need logic to check if the account has enough money to buy the card
                    print(f'Buying card {card_id} with cost {cost} and ratio {ratio}')
                    buy_card(account, card_id)
                    time.sleep(random.randint(1,5))
            else:
                print('Error fetching card data.')
        
        print("Waiting 2 minutes before next round...")
        time.sleep(random.randint(100,130))    

if __name__ == "__main__":
    main()
