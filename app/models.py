
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel


class SignMessageRequest(BaseModel):
    message: str
    wallet_address: str


class GenKeyRequest(BaseModel):
    wallet_address: str


class SaveMessageRequest(BaseModel):
    message: str
    wallet_address: str


class GenProofRequest(BaseModel):
    count: int
    message: str


class PKeys(BaseModel):
    public_key: str
    private_key: str


class Validator(BaseModel):
    public_key: str
    private_key: str
    weight: int
    wallet_address: str

    def __eq__(self, other: object) -> bool:
        if hasattr(other, "wallet_address"):
            return self.wallet_address == other.wallet_address
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.wallet_address)


class Signature(BaseModel):
    r: List[str]
    s: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Validator):
            return self.r == other.r and self.s == other.s
        return NotImplemented


class Message(BaseModel):
    message: str
    signed_validators: Dict[Validator, Signature] = {}
    created_at: datetime
    created_by: str

    def __getitem__(self, item):
        return getattr(self, item)
