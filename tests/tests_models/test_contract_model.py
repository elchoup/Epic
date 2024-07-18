import pytest
from peewee import IntegrityError
from crm.models.contract import Contract


def test_create_contract(setup_db, client1, user2):
    with setup_db.atomic():
        print(client1)
        contract = Contract.create(
            client=client1,
            total_amount=15000,
            remaining_amount=5000,
            created_at="2024-06-24 17:00:00",
            commercial_contact=user2,
        )

        assert contract.client.first_name == "Tom"
        assert contract.total_amount == 15000
        assert contract.remaining_amount == 5000
        assert contract.created_at == "2024-06-24 17:00:00"
        assert contract.commercial_contact.name == "Com"


def test_create_contract_invalid_data(client1):
    with pytest.raises(IntegrityError):
        Contract.create(
            client=client1,
            total_amount=15000,
            created_at="2024-06-24 17:00:00",
        )
