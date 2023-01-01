import pytest
from brownie import NftMarketplace, BasicNft, config, network, reverts
from scripts.helpers import call_contract_method, custom_error
from scripts.deploy_nft_marketplace import deploy as deploy_nft_marketplace
from scripts.deploy_basic_nft import deploy as deploy_basic_nft
from web3 import Web3


@pytest.fixture(scope='module')
def nft_marketplace():
    if not (NftMarketplace):
        deploy_nft_marketplace()
    return NftMarketplace[-1]


@pytest.fixture(scope='module')
def basic_nft():
    if not (BasicNft):
        deploy_basic_nft()
    return BasicNft[-1]


# @pytest.fixture(scope=)
# def listed_item_tx(nft_marketplace, basic_nft, accounts):


def test_list_item(nft_marketplace, basic_nft, accounts):
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': accounts[0]})
    list_item_tx.wait(1)
    assert 'ItemListed' in list_item_tx.events
    assert nft_marketplace.getListing(basic_nft.address, token_id)['price'] > 0
    assert nft_marketplace.getListing(basic_nft.address, token_id)[
        'seller'] == accounts[0].address


def test_listed_item_cant_listed_again(nft_marketplace, basic_nft, accounts):
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': accounts[0]})
    list_item_tx.wait(1)
    # errMsg = Web3.keccak(text='AlreadyListed' +
    #                      '("'+str(basic_nft.address)+'",'+str(token_id)+')')[:4].hex()
    with reverts():
        call_contract_method(
            nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': accounts[0]})

    # call_contract_method(
        # nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': accounts[0]})


def test_just_owner_can_list(nft_marketplace, basic_nft, accounts):
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})

    errMsg = Web3.keccak(text='NotOwner()')[:4].hex()
    with reverts('typed error: '+errMsg):
        call_contract_method(
            nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': accounts[1]})


def test_nft_must_be_approved(nft_marketplace, basic_nft, accounts):
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()
    errMsg = Web3.keccak(text='NotApprovedForMarketplace()')[:4].hex()
    with reverts('typed error: '+errMsg):
        call_contract_method(
            nft_marketplace, 'listItem', basic_nft.address, token_id, "0.01 ether", {'from': accounts[0]})


def test_buy_item(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)

    buy_tx = call_contract_method(nft_marketplace, 'buyItem', basic_nft.address, token_id, {
                                  'from': accounts[1], 'value': nft_price})
    buy_tx.wait(1)

    listing = nft_marketplace.getListing(basic_nft.address, token_id)
    assert nft_marketplace.getProceeds(accounts[0].address) == nft_price
    assert listing['price'] == 0
    assert basic_nft.ownerOf(token_id) == accounts[1].address
    assert 'ItemBought' in buy_tx.events


def test_not_allowed_to_buy_not_listed_item(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})

    with reverts():
        buy_tx = call_contract_method(nft_marketplace, 'buyItem', basic_nft.address, token_id, {
            'from': accounts[1], 'value': nft_price})


def test_value_must_be_higher_or_equal_to_token_price(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)
    with reverts():
        buy_tx = call_contract_method(nft_marketplace, 'buyItem', basic_nft.address, token_id, {
            'from': accounts[1], 'value': '0.001 ether'})


def test_cancel_listing(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)

    cancel_tx = call_contract_method(nft_marketplace, 'cancelListing',
                                     basic_nft.address, token_id, {'from': accounts[0]})
    listing = nft_marketplace.getListing(basic_nft.address, token_id)
    assert listing['price'] == 0
    assert 'ItemCanceled' in cancel_tx.events


def test_not_allowed_to_cancel_not_listed_item(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})

    with reverts():
        buy_tx = call_contract_method(nft_marketplace, 'cancelListing', basic_nft.address, token_id, {
            'from': accounts[0]})


def test_just_owner_can_cancel_list(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})

    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)

    errMsg = Web3.keccak(text='NotOwner()')[:4].hex()
    with reverts('typed error: '+errMsg):
        call_contract_method(
            nft_marketplace, 'cancelListing', basic_nft.address, token_id,  {'from': accounts[1]})


def test_update_listing(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    new_price = '0.015 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)

    cancel_tx = call_contract_method(nft_marketplace, 'updateListing',
                                     basic_nft.address, token_id, new_price, {'from': accounts[0]})
    listing = nft_marketplace.getListing(basic_nft.address, token_id)
    assert listing['price'] == new_price
    assert 'ItemListed' in cancel_tx.events


def test_not_allowed_to_update_not_listed_item(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    new_price = '0.015 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})

    with reverts():
        buy_tx = call_contract_method(nft_marketplace, 'updateListing', basic_nft.address, token_id, new_price, {
            'from': accounts[0]})


def test_just_owner_can_update_list(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    new_price = '0.015 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})

    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)

    errMsg = Web3.keccak(text='NotOwner()')[:4].hex()
    with reverts('typed error: '+errMsg):
        call_contract_method(
            nft_marketplace, 'updateListing', basic_nft.address, token_id, new_price,  {'from': accounts[1]})


def test_new_price_must_be_higher_zero(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    new_price = '0 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)
    errMsg = Web3.keccak(text='PriceMustBeAboveZero()')[:4].hex()
    with reverts('typed error: '+errMsg):
        buy_tx = call_contract_method(nft_marketplace, 'updateListing', basic_nft.address, token_id, new_price, {
            'from': accounts[0]})


def test_withdraw_proceeds(nft_marketplace, basic_nft, accounts):
    nft_price = '0.01 ether'
    mint_nft_tx = call_contract_method(
        basic_nft, 'mintNft', {'from': accounts[0]})
    mint_nft_tx.wait(1)

    token_id = basic_nft.getTokenCounter()

    call_contract_method(basic_nft, 'approve',
                         nft_marketplace.address, token_id, {'from': accounts[0]})
    list_item_tx = call_contract_method(
        nft_marketplace, 'listItem', basic_nft.address, token_id, nft_price, {'from': accounts[0]})
    list_item_tx.wait(1)

    buy_tx = call_contract_method(nft_marketplace, 'buyItem', basic_nft.address, token_id, {
                                  'from': accounts[1], 'value': nft_price})
    buy_tx.wait(1)

    withdraw_tx = call_contract_method(
        nft_marketplace, 'withdrawProceeds', {'from': accounts[0]})
    assert nft_marketplace.getProceeds(accounts[0].address) == 0


def test_cant_withdraw_with_zero_proceeds(nft_marketplace, accounts):
    errMsg = Web3.keccak(text='NoProceeds()')[:4].hex()
    with reverts('typed error: '+errMsg):
        call_contract_method(
            nft_marketplace, 'withdrawProceeds', {'from': accounts[0]})
