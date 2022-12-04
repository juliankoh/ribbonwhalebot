import requests
import datetime
import time
from twitter import tweet


def run_query(q, v):
    request = requests.post(
        'https://api.studio.thegraph.com/query/30834/ribbonlend2/v0.0.1', json={'query': q, 'variables': v})
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
          symbol
        }
      }
    """
    return run_query(query, {})


def get_all_deposits(t):
    query = """
    query($ts: Int){
      vaultTransactions(
        orderBy: timestamp
        orderDirection: desc
        where: {type: "deposit", timestamp_gte: $ts}
      ) {
        id
        type
        timestamp
        txhash
        address
        amount
      }
    }
    """
    return run_query(query, {'ts': t})


def get_all_deposits_size(ts, minSize):
    query = """
    query($ts: Int, $minSize: String){
      vaultTransactions(
        orderBy: timestamp
        orderDirection: desc
        where: {type: "deposit", timestamp_gte: $ts, amount_gte: $minSize}
      ) {
        id
        type
        timestamp
        txhash
        address
        amount
      }
    }
    """
    return run_query(query, {'ts': ts, 'minSize': minSize})


def trigger_lend():
    deposit_threshold = "100000000000"
    time_elapsed = 10
    ten_mins_ago = (datetime.datetime.now() -
                    datetime.timedelta(minutes=time_elapsed)).timestamp()

    deposits = get_all_deposits_size(int(ten_mins_ago), deposit_threshold)

    for deposit in deposits['data']['vaultTransactions']:
        address = deposit['address']
        value = int(int(deposit['amount']) / 10**6)
        value_string = f'{value:,}'
        txhash = deposit['txhash']
        text = """\
    New @ribbonfinance Lend Deposit 🎀: 

    Address: {address} 

    Amount: {amount} USDC 

    TxHash: {txhash} \
        """.format(length='multi-line', address=address, amount=value_string, txhash=txhash)

        tweet(text)
        time.sleep(1)
