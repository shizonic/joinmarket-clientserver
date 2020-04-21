#! /usr/bin/env python
'''Test of psbt creation, update, signing and finalizing
   using the functionality of the PSBT Wallet Mixin.
   Note that Joinmarket's PSBT code is a wrapper around
   bitcointx.core.psbt, and the basic test vectors for
   BIP174 are tested there, not here.
   '''

import time
import binascii
import struct
from commontest import make_wallets, make_sign_and_push

import jmbitcoin as bitcoin
import pytest
from jmbase import get_log, bintohex, hextobin
from jmclient import load_test_config, jm_single,\
     get_p2pk_vbyte

log = get_log()

@pytest.mark.parametrize('unowned_utxo', [
    True,
    False,
])
def test_create_psbt_and_sign(setup_psbt_wallet, unowned_utxo):
    """ Plan of test:
    1. Create a wallet and source 3 destination addresses.
    2. Make, and confirm, transactions that fund the 3 addrs.
    3. Create a new tx spending 2 of those 3 utxos and spending
       another utxo we don't own (extra is optional per `unowned_utxo`).
    4. Create a psbt using the above transaction and corresponding
       `spent_outs` field to fill in the redeem script.
    5. Compare resulting PSBT with expected structure.
    6. Use the wallet's sign_psbt method to sign the whole psbt, which
       means signing each input we own.
    7. Check that each input is finalized as per expected. Check that the whole
       PSBT is or is not finalized as per whether there is an unowned utxo.
    8. In case where whole psbt is finalized, attempt to broadcast the tx.
    """
    # steps 1 and 2:
    wallet_service = make_wallets(1, [[3,0,0,0,0]], 1)[0]['wallet']
    wallet_service.sync_wallet(fast=True)
    utxos = wallet_service.select_utxos(0, bitcoin.coins_to_satoshi(1.5))
    assert len(utxos) == 2
    if unowned_utxo:
        # note: tx creation uses the key only; psbt creation uses the value,
        # which can be fake here; we do not intend to attempt to fully
        # finalize a psbt with an unowned input. See
        # https://github.com/Simplexum/python-bitcointx/issues/30
        # for whether this redeemscript construction can be avoided.
        priv = b"\xaa"*32 + b"\x01"
        pub = bitcoin.privkey_to_pubkey(priv)
        script = bitcoin.pubkey_to_p2sh_p2wpkh_script(pub)
        redeem_script = bitcoin.pubkey_to_p2wpkh_script(pub)
        utxos[(b"\xaa"*32, 12)] = {"value": 1000, "script": script}
    # outputs aren't interesting for this test (we selected 1.5 but will get 2):
    outs = [{"value": bitcoin.coins_to_satoshi(1.999),
             "address": wallet_service.get_addr(0,0,0)}]
    tx = bitcoin.mktx(list(utxos.keys()), outs)

    newpsbt = wallet_service.create_psbt_from_tx(tx,
                    wallet_service.witness_utxos_to_psbt_utxos(utxos))
    # see note above
    if unowned_utxo:
        newpsbt.inputs[-1].redeem_script = redeem_script
    print(bintohex(newpsbt.serialize()))
    # we cannot compare with a fixed expected result due to wallet randomization, but we can
    # check psbt structure:
    expected_inputs_length = 3 if unowned_utxo else 2
    assert len(newpsbt.inputs) == expected_inputs_length
    assert len(newpsbt.outputs) == 1
    # note: redeem_script field is a CScript which is a bytes instance,
    # so checking length is best way to check for existence (comparison
    # with None does not work):
    assert len(newpsbt.inputs[0].redeem_script) != 0
    assert len(newpsbt.inputs[1].redeem_script) != 0
    if unowned_utxo:
        assert newpsbt.inputs[2].redeem_script == redeem_script

    signed_psbt_and_signresult, err = wallet_service.sign_psbt(
        newpsbt.serialize(), with_sign_result=True)
    assert err is None
    signresult, signed_psbt = signed_psbt_and_signresult
    expected_signed_inputs = len(utxos) if not unowned_utxo else len(utxos)-1
    assert signresult.num_inputs_signed == expected_signed_inputs
    assert signresult.num_inputs_final == expected_signed_inputs

    if not unowned_utxo:
        assert signresult.is_final
        # only in case all signed do we try to broadcast:
        extracted_tx = signed_psbt.extract_transaction().serialize()
        assert jm_single().bc_interface.pushtx(extracted_tx)
    else:
        # transaction extraction must fail for not-fully-signed psbts:
        with pytest.raises(ValueError) as e:
            extracted_tx = signed_psbt.extract_transaction()
        
  
@pytest.fixture(scope="module")
def setup_psbt_wallet():
    load_test_config()
