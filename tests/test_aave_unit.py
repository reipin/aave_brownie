from scripts.aave_borrow import get_lending_pool_address
from brownie import interface, config, network
from scripts.helpful_scripts import get_account
from web3 import Web3


def test_get_asset_price():
    # Arrange
    price_feed = config["networks"][network.show_active()]["dai_eth_price_feed"]
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed)
    # Act
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    # Assert
    assert converted_latest_price < 0.0007
    assert converted_latest_price > 0.0005


def test_get_lending_pool_address():
    # Arrenge
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # Act & Assert
    assert lending_pool_address is not None


def test_get_lending_pool():
    # Arrange
    lending_pool = interface.ILendingPool(get_lending_pool_address())
    # Act & Assert
    assert lending_pool is not None


def test_approve_erc20():
    # Arrange
    erc20_token_address = config["networks"][network.show_active()]["weth_token"]
    spender = get_lending_pool_address()
    amount = Web3.toWei(1, "ether")
    account = get_account()
    erc20 = interface.IERC20(erc20_token_address)
    # Act
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    # Assert
    assert tx is not True
