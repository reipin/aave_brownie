from brownie import network, config, interface
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIROMENTS
from scripts.get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")


def main():
    # Get my account
    account = get_account()
    # Get WETH token contract depending on network
    erc20_token = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        get_weth()
    # Get lending pool contract
    lending_pool = get_lending_pool()
    # print(lending_pool)
    # print(type(lending_pool))

    # Approve sending our weth token
    approve_erc20(AMOUNT, lending_pool.address, erc20_token, account)

    # Deposit ERC20 token, which is defined in Aave funtion
    print("Depositing WETH to Aave....")
    tx = lending_pool.deposit(erc20_token, AMOUNT, account, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")

    # Get user account data from Aave function
    available_borrow_eth, total_debt_eth = get_borrowable_data(lending_pool, account)

    print("Lets borrow some DAIs!")
    # Get DAI / ETH price feed contract address
    dai_eth_price_feed = config["networks"][network.show_active()]["dai_eth_price_feed"]
    # Get latest DAI / ETH price from Linkchain
    dai_eth_price = get_asset_price(dai_eth_price_feed)
    amount_dai_to_borrow = available_borrow_eth / dai_eth_price * float(0.95)
    # borrowable_eth -> borrowable_dai * 95%
    print(f"We are going to borrow {amount_dai_to_borrow} DAIs!")

    # Borrow DAI with borrow Aave function
    borrow_tx = lending_pool.borrow(
        config["networks"][network.show_active()]["dai_asset_address"],
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)

    # Repay DAI with repay Aave function
    # repay_all(amount_dai_to_borrow, lending_pool, account)


def repay_all(amount, lending_pool, account):
    # To repay we have to first approve the trasaction
    dai_token_address = config["networks"][network.show_active()]["dai_asset_address"]
    approve_erc20(Web3.toWei(amount, "ether"), lending_pool, dai_token_address, account)

    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_asset_address"],
        Web3.toWei(amount, "ether"),
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("We repayed all the DAI borrowed!")
    get_borrowable_data(lending_pool, account)


def get_asset_price(price_feed):
    # Grab an ABI
    # Grab an address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed)
    # (/*uint80 roundID*/,int price,/*uint startedAt*/,/*uint timeStamp*/,/*uint80 answeredInRound*/)
    # Fetch only index no.1 (price)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The latest Dai/Eth price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    # By defineing you can get all the data from one line
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_eth,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    current_liquidation_eth = Web3.fromWei(current_liquidation_eth, "ether")
    # print(type(data))
    # print(data["totalCollateralETH"])
    print(f"You have {total_collateral_eth} of ETH deposited!")
    print(f"You have {total_debt_eth} of ETH in debt...")
    print(f"You can borrow {available_borrow_eth} worth of ETH!")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_token_address, account):
    # Who approves is an IERC20 contract
    # Address
    # ABI
    print("Approving ERC20 token!")
    erc20 = interface.IERC20(erc20_token_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_lending_pool_address():
    # Address
    # ABI
    # contract = interface.YourInterface(contract_address)
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    return lending_pool_address


def get_lending_pool():
    # Address
    # ABI
    lending_pool = interface.ILendingPool(get_lending_pool_address())
    return lending_pool
