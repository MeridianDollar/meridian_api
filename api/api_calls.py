import requests
import json
    
def get_coingecko_price(currency):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={currency}&vs_currencies=usd"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            price = data[currency]['usd']
            return price
        else:
            print(f"Failed to fetch data for {currency}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
def getAllCoinGeckoPrices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=telos%2Cethereum%2Cfuse-network-token&vs_currencies=usd"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            with open("json/prices.json", "w") as json_file:
                json.dump(data, json_file)
        else:
            print(f"Failed to fetch data")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None   



def get_mst_swapsicle_data():
    try:
        url = "https://api.dexscreener.com/latest/dex/tokens/0x568524DA340579887db50Ecf602Cd1BA8451b243"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Accessing the priceNative field from the first pair
        price_mst = data['pairs'][0]['priceUsd']
        liquidity_mst = data['pairs'][0]['liquidity']['usd']
        
        return float(price_mst)
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_mst_uniswap_data():
    try:
        url = "https://api.dexscreener.com/latest/dex/tokens/0x2F3b1A07E3eFb1fCc64BD09b86bD0Fa885D93552"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    
        price_mst = data['pairs'][0]['priceUsd']
        liquidity_mst = data['pairs'][0]['liquidity']['usd']

        return float(price_mst)

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def fetchOmniDexBP():
    try: 
        url = "https://omnidexbp.com/v1/chain/get_info"  
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["head_block_num"]
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def get_liquidity():
    try:
        response = requests.get("https://api.llama.fi/protocol/meridian")
        response.raise_for_status()  # This will raise an HTTPError if the response was an 'error'
        data = response.json()

        base_tvl = data['currentChainTvls']['Base']
        fuse_tvl = data['currentChainTvls']['Fuse']
        telos_tvl = data['currentChainTvls']['Telos']
        meter_tvl = data['currentChainTvls']['Meter']
        borrowed = data['currentChainTvls']['borrowed']

        total_tvl = base_tvl + fuse_tvl + telos_tvl + meter_tvl + borrowed

        return int(total_tvl)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None