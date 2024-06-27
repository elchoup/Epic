import pytest
from peewee import IntegrityError
from test_config import setup_db, client1
from crm.models.contract import Contract


def test_create_contract(setup_db, client1):
    with setup_db.atomic():
        contract = Contract.create(
            client=client1,
            total_amount=15000,
            remaining_amount=5000,
            created_at="2024-06-24 17:00:00",
        )

        assert contract.client.first_name == "Tom"
        assert contract.total_amount == 15000
        assert contract.remaining_amount == 5000
        assert contract.created_at == "2024-06-24 17:00:00"


def test_create_contract_invalid_data(client1):
    with pytest.raises(IntegrityError):
        Contract.create(
            client=client1,
            total_amount=15000,
            created_at="2024-06-24 17:00:00",
        )
