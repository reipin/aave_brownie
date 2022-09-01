from scripts.helpful_scripts import get_account
from brownie import interface, network, config


def main():
    get_weth()


def get_weth():
    # To interact with a contract, we always need an ABI and an address (account + contcat)
    # 1. Account address
    account = get_account()
    # 2. ABI
    # contract = interface.YourInterface(contract_address)
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print("Recieved 0.1 WETH!")
    return tx
