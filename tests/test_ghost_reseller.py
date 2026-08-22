import pytest
from unittest.mock import patch, MagicMock
from ghost_reseller.services.supplier_client import SupplierClient
from ghost_reseller.services.wallet_ledger import WalletLedger
from ghost_reseller.services.web3_wallet import Web3WalletSecurity
from ghost_reseller.services.gas_database import GASDatabaseConnector
from ghost_reseller.services.multi_supplier_manager import MultiSupplierManager

def test_supplier_client_products():
    client = SupplierClient(api_key="test_key", default_markup_usdt=3.0)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "success": True,
        "products": [{"id": 1, "name": "Gemini Pro", "your_cost": 1.0}]
    }
    with patch("requests.get", return_value=mock_resp):
        res = client.fetch_products()
        assert res["success"] is True
        assert res["products"][0]["retail_price_usdt"] == 4.0

def test_wallet_ledger(tmp_path):
    db_file = str(tmp_path / "test.db")
    ledger = WalletLedger(db_path=db_file)
    u = ledger.get_or_create_user(user_id=123)
    assert u["balance_usdt"] == 0.0
    
    bal = ledger.credit_balance(user_id=123, amount_usdt=10.0)
    assert bal == 10.0
    
    ok = ledger.deduct_balance(user_id=123, amount_usdt=4.0, description="Test")
    assert ok is True

def test_web3_wallet_encryption():
    sec = Web3WalletSecurity()
    secret = "my_private_key_or_seed"
    enc = sec.encrypt_secret(secret)
    assert enc != secret
    dec = sec.decrypt_secret(enc)
    assert dec == secret

def test_gas_database_connector():
    gas = GASDatabaseConnector(gas_webapp_url="https://script.google.com/macros/s/test/exec")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"balance_usdt": 25.0}
    with patch("requests.get", return_value=mock_resp):
        data = gas.get_user_data(123)
        assert data["balance_usdt"] == 25.0

def test_multi_supplier_manager():
    mgr = MultiSupplierManager()
    item = mgr.get_cheapest_product("gemini_18m", default_markup_usdt=3.0)
    assert item["best_supplier"] == "Prism1 Bot"
    assert item["supplier_cost_usdt"] == 0.65 # $0.65 vs $1.00 de Bunny
    assert item["retail_price_usdt"] == 3.65
    assert item["profit_margin_usdt"] == 3.0


