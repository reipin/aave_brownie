from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development", "ganache-local", "mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])
