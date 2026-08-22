"""
Web3 EVM Wallet & AES-256 Encryption Manager
System: Nexus Reseller Core
"""

import os
import json
from cryptography.fernet import Fernet
from typing import Dict, Any

class Web3WalletSecurity:
    def __init__(self, master_key: str = None):
        if master_key:
            key_bytes = master_key.encode() if isinstance(master_key, str) else master_key
            self.fernet = Fernet(key_bytes)
        else:
            self.key = Fernet.generate_key()
            self.fernet = Fernet(self.key)

    def encrypt_secret(self, secret_text: str) -> str:
        """Cifra la clave privada o semilla de MetaMask/EVM usando AES-256 Fernet."""
        return self.fernet.encrypt(secret_text.encode('utf-8')).decode('utf-8')

    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Descifra la clave privada o semilla descifrada."""
        return self.fernet.decrypt(encrypted_secret.encode('utf-8')).decode('utf-8')

    def generate_deposit_address_info(self, evm_address: str, chain: str = "USDT (BEP-20 / Polygon)") -> Dict[str, Any]:
        """Formatea la información de depósito cripto en MetaMask / EVM para el usuario."""
        return {
            "chain": chain,
            "address": evm_address,
            "instructions": f"Envía tu pago USDT en la red {chain} a esta dirección. El depósito se acreditará automáticamente tras confirmaciones en cadena."
        }
