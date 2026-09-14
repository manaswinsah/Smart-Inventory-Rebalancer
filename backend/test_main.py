import pytest

from fastapi.testclient import TestClient

from main import app
from database import Base
from test_database import (
    test_engine,
    TestingSessionLocal,
    setup_test_database,
    teardown_test_database,
    get_test_db,
)


# ============================================================
# TEST DATABASE SETUP
# ============================================================

@pytest.fixture(scope="function")
def test_db():

    setup_test_database()

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        teardown_test_database()


# ============================================================
# FASTAPI TEST CLIENT
# ============================================================

@pytest.fixture(scope="function")
def client(test_db):

    def override_get_db():
        yield test_db

    from main import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================
# BASIC API TESTS
# ============================================================

def test_root(client):

    response = client.get("/")

    assert response.status_code == 200


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200


# ============================================================
# PRODUCT TESTS
# ============================================================

def test_create_product(client):

    response = client.post(
        "/products",
        json={
            "name": "Test Laptop",
            "sku": "TEST-LAP-001",
            "reorder_threshold": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Laptop"
    assert data["sku"] == "TEST-LAP-001"
    assert data["reorder_threshold"] == 10


def test_get_products(client):

    client.post(
        "/products",
        json={
            "name": "Test Laptop",
            "sku": "TEST-LAP-002",
            "reorder_threshold": 10
        }
    )

    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Laptop"


# ============================================================
# WAREHOUSE TESTS
# ============================================================

def test_create_warehouse(client):

    response = client.post(
        "/warehouses",
        json={
            "name": "Test Warehouse",
            "location": "Dehradun"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Warehouse"
    assert data["location"] == "Dehradun"


# ============================================================
# INVENTORY TESTS
# ============================================================

def test_create_inventory(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Inventory Laptop",
            "sku": "INV-LAP-001",
            "reorder_threshold": 10
        }
    )

    warehouse_response = client.post(
        "/warehouses",
        json={
            "name": "Inventory Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    warehouse_id = warehouse_response.json()["id"]

    response = client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 50
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity"] == 50


# ============================================================
# TRANSACTION TESTS
# ============================================================

def test_inventory_in_transaction(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Transaction Laptop",
            "sku": "TRANS-LAP-001",
            "reorder_threshold": 10
        }
    )

    warehouse_response = client.post(
        "/warehouses",
        json={
            "name": "Transaction Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    warehouse_id = warehouse_response.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 20
        }
    )

    response = client.post(
        "/inventory/transactions",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 10,
            "transaction_type": "IN"
        }
    )

    assert response.status_code == 200

    inventory = client.get("/inventory").json()

    assert inventory[0]["quantity"] == 30


def test_inventory_out_transaction(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Transaction Mouse",
            "sku": "TRANS-MOU-001",
            "reorder_threshold": 5
        }
    )

    warehouse_response = client.post(
        "/warehouses",
        json={
            "name": "Transaction Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    warehouse_id = warehouse_response.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 20
        }
    )

    response = client.post(
        "/inventory/transactions",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 5,
            "transaction_type": "OUT"
        }
    )

    assert response.status_code == 200

    inventory = client.get("/inventory").json()

    assert inventory[0]["quantity"] == 15


def test_insufficient_stock_rejected(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Limited Mouse",
            "sku": "LIMIT-MOU-001",
            "reorder_threshold": 5
        }
    )

    warehouse_response = client.post(
        "/warehouses",
        json={
            "name": "Limited Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    warehouse_id = warehouse_response.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 10
        }
    )

    response = client.post(
        "/inventory/transactions",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 20,
            "transaction_type": "OUT"
        }
    )

    assert response.status_code == 400


# ============================================================
# INVENTORY STATUS TEST
# ============================================================

def test_inventory_status(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Status Laptop",
            "sku": "STATUS-LAP-001",
            "reorder_threshold": 10
        }
    )

    warehouse_response = client.post(
        "/warehouses",
        json={
            "name": "Status Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    warehouse_id = warehouse_response.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 5
        }
    )

    response = client.get("/inventory/status")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "LOW"


# ============================================================
# REBALANCING TEST
# ============================================================

def test_rebalancing_recommendation(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Rebalance Laptop",
            "sku": "REBAL-LAP-001",
            "reorder_threshold": 10
        }
    )

    warehouse_1 = client.post(
        "/warehouses",
        json={
            "name": "Source Warehouse",
            "location": "Dehradun"
        }
    )

    warehouse_2 = client.post(
        "/warehouses",
        json={
            "name": "Destination Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    source_id = warehouse_1.json()["id"]
    destination_id = warehouse_2.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": source_id,
            "quantity": 30
        }
    )

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": destination_id,
            "quantity": 5
        }
    )

    response = client.get("/rebalancing/recommendations")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["quantity"] == 5


# ============================================================
# TRANSFER TEST
# ============================================================

def test_successful_transfer(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Transfer Laptop",
            "sku": "TRANSFER-LAP-001",
            "reorder_threshold": 10
        }
    )

    warehouse_1 = client.post(
        "/warehouses",
        json={
            "name": "Transfer Source",
            "location": "Dehradun"
        }
    )

    warehouse_2 = client.post(
        "/warehouses",
        json={
            "name": "Transfer Destination",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    source_id = warehouse_1.json()["id"]
    destination_id = warehouse_2.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": source_id,
            "quantity": 30
        }
    )

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": destination_id,
            "quantity": 5
        }
    )

    response = client.post(
        "/rebalancing/transfer",
        json={
            "product_id": product_id,
            "from_warehouse_id": source_id,
            "to_warehouse_id": destination_id,
            "quantity": 5
        }
    )

    assert response.status_code == 200

    inventory = client.get("/inventory").json()

    source_inventory = next(
        item for item in inventory
        if item["warehouse_id"] == source_id
    )

    destination_inventory = next(
        item for item in inventory
        if item["warehouse_id"] == destination_id
    )

    assert source_inventory["quantity"] == 25
    assert destination_inventory["quantity"] == 10


# ============================================================
# ANALYTICS TEST
# ============================================================

def test_analytics(client):

    product_response = client.post(
        "/products",
        json={
            "name": "Analytics Laptop",
            "sku": "ANALYTICS-LAP-001",
            "reorder_threshold": 10
        }
    )

    warehouse_response = client.post(
        "/warehouses",
        json={
            "name": "Analytics Warehouse",
            "location": "Delhi"
        }
    )

    product_id = product_response.json()["id"]
    warehouse_id = warehouse_response.json()["id"]

    client.post(
        "/inventory",
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 25
        }
    )

    response = client.get("/analytics")

    assert response.status_code == 200

    data = response.json()

    assert data["summary"]["total_products"] == 1
    assert data["summary"]["total_warehouses"] == 1
    assert data["summary"]["total_stock"] == 25