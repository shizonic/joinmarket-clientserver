from jmclient.configure import validate_address, load_test_config
from jmclient import jm_single
import jmbitcoin as btc
import json
import pytest
import os
testdir = os.path.dirname(os.path.realpath(__file__))

def address_valid_somewhere(addr):
    for x in ["bitcoin", "bitcoin/testnet", "bitcoin/regtest"]:
        btc.select_chain_params(x)
        if validate_address(addr)[0]:
            return True
    return False

def test_non_addresses(setup_addresses):
    #could flesh this out with other examples
    res, msg = validate_address(2)
    assert res == False, "Incorrectly accepted number"

def test_b58_invalid_addresses(setup_addresses):
    #none of these are valid as any kind of key or address
    with open(os.path.join(testdir,"base58_keys_invalid.json"), "r") as f:
        json_data = f.read()
    invalid_key_list = json.loads(json_data)
    for k in invalid_key_list:
        bad_key = k[0]
        res = address_valid_somewhere(bad_key)
        assert res == False, "Incorrectly validated address: " + bad_key

def test_b58_valid_addresses():
    with open(os.path.join(testdir,"base58_keys_valid.json"), "r") as f:
        json_data = f.read()
    valid_keys_list = json.loads(json_data)
    for a in valid_keys_list:
        addr, pubkey, prop_dict = a
        if not prop_dict["isPrivkey"]:
            if prop_dict["isTestnet"]:
                jm_single().config.set("BLOCKCHAIN", "network", "testnet")
                btc.select_chain_params("bitcoin/testnet")
            else:
                jm_single().config.set("BLOCKCHAIN", "network", "mainnet")
                btc.select_chain_params("bitcoin")
            #if using pytest -s ; sanity check to see what's actually being tested
            res, message = validate_address(addr)
            assert res == True, "Incorrectly failed to validate address: " + addr + " with message: " + message
    jm_single().config.set("BLOCKCHAIN", "network", "testnet")
    btc.select_chain_params("bitcoin/regtest")

def test_valid_bech32_addresses():
    valids = ["BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4",
    "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7",
    # TODO these are valid bech32 addresses but rejected by bitcointx
    # because they are not witness version 0; add others.
    #"bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx",
    #"BC1SW50QA3JX3S",
    #"bc1zw508d6qejxtdg4y5r3zarvaryvg6kdaj",
    "tb1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesrxh6hy"]
    for va in valids:
        if va.lower()[:2] == "bc":
            jm_single().config.set("BLOCKCHAIN", "network", "mainnet")
            btc.select_chain_params("bitcoin")
        else:
            jm_single().config.set("BLOCKCHAIN", "network", "testnet")
            btc.select_chain_params("bitcoin/testnet")
        res, message = validate_address(va)
        assert res == True, "Incorrect failed to validate address: " + va + " with message: " + message
    jm_single().config.set("BLOCKCHAIN", "network", "testnet")
    btc.select_chain_params("bitcoin/regtest")

def test_invalid_bech32_addresses():
    invalids = [
    "tc1qw508d6qejxtdg4y5r3zarvary0c5xw7kg3g4ty",
    "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5",
    "BC13W508D6QEJXTDG4Y5R3ZARVARY0C5XW7KN40WF2",
    "bc1rw5uspcuh",
    "bc10w508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kw5rljs90",
    "BC1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9P",
    "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sL5k7",
    "bc1zw508d6qejxtdg4y5r3zarvaryvqyzf3du",
    "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3pjxtptv",
    "bc1gmk9yu"]
    for iva in invalids:
        res = address_valid_somewhere(iva)
        assert res == False, "Incorrectly validated address: " + iva

@pytest.fixture(scope="module")
def setup_addresses():
    load_test_config()
