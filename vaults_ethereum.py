import requests
import datetime
import time
from twitter import tweet

VAULT_MAPPING = {
    '0x25751853eab4d0eb3652b5eb6ecb102a2789644b': {'name': 'Ribbon ETH Theta Vault', 'threshold': '100', 'decimals': 18},
    '0x53773e034d9784153471813dacaff53dbbb78e8c': {'name': 'Ribbon stETH Theta Vault', 'threshold': '100', 'decimals': 18},
    '0xa1da0580fa96129e753d736a5901c31df5ec5edf': {'name': 'Ribbon rETH Theta Vault', 'threshold': '100', 'decimals': 18},
    '0x65a833afdc250d9d38f8cd9bc2b1e3132db13b2f': {'name': 'Ribbon BTC Theta Vault', 'threshold': '5', 'decimals': 8},
    '0xcc323557c71c0d1d20a1861dc69c06c5f3cc9624': {'name': 'Ribbon yvUSDC Theta Vault ETH Put', 'threshold': '100000', 'decimals': 6},
    '0xe63151a0ed4e5fafdc951d877102cf0977abd365': {'name': 'Ribbon Aave Theta Vault', 'threshold': '1000', 'decimals': 18}
}


def convert_threshold_underlying(vault_id):
    threshold_string = VAULT_MAPPING[vault_id]['threshold']
    decimals = VAULT_MAPPING[vault_id]['decimals']
    threshold_int = int(threshold_string) * (10**decimals)
    return str(threshold_int)


def run_query(q, v):
    request = requests.post(
        'https://api.thegraph.com/subgraphs/name/ribbon-finance/ribbon-v2', json={'query': q, 'variables': v})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}'.format(
            request.status_code, q))


def get_all_vaults():
    query = """
      {
        vaults {
          id
          name
        }
      }
    """
    return run_query(query, {})


def get_all_deposits(vault, time, minSize):
    query = """
    query($time: Int, $vault: String, $minSize: String){
      vaultTransactions(
        orderBy: timestamp
        orderDirection: desc
        where: {type: "deposit", timestamp_gte: $time, amount_gte: $minSize, vault_: { id: $vault }}
      ) {
        id
        type
        timestamp
        txhash
        address
        amount
        vault {
          name
          underlyingSymbol
          underlyingDecimals
        }
      }
    }
    """
    return run_query(query, {'time': time, 'vault': vault, 'minSize': minSize})


def trigger():
    vaults = VAULT_MAPPING.keys()
    for vault in vaults:
        vault_name = VAULT_MAPPING[vault]['name']

        time_elapsed = 10
        ten_mins_ago = (datetime.datetime.now() -
                        datetime.timedelta(minutes=time_elapsed)).timestamp()

        deposit_threshold = convert_threshold_underlying(vault)
        deposits = get_all_deposits(
            vault, int(ten_mins_ago), deposit_threshold)

        for deposit in deposits['data']['vaultTransactions']:
            address = deposit['address']
            currency = deposit['vault']['underlyingSymbol']
            value = int(int(deposit['amount']) / 10 **
                        deposit['vault']['underlyingDecimals'])
            value_string = f'{value:,}'
            txhash = deposit['txhash']
            text = """\
New @ribbonfinance Vault Deposit 🎀: 
          
    Address: {address} 

    Vault: {vault}

    Amount: {amount} {currency} 

    TxHash: {txhash} \
            """.format(length='multi-line', address=address, vault=vault_name, amount=value_string, currency=currency, txhash=txhash)

            tweet(text)
            time.sleep(1)
