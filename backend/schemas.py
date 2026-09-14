from pydantic import BaseModel


# =========================
# PRODUCT SCHEMAS
# =========================

class ProductCreate(BaseModel):
    name: str
    sku: str
    reorder_threshold: int


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    reorder_threshold: int

    class Config:
        from_attributes = True


# =========================
# WAREHOUSE SCHEMAS
# =========================

class WarehouseCreate(BaseModel):
    name: str
    location: str


class WarehouseResponse(BaseModel):
    id: int
    name: str
    location: str

    class Config:
        from_attributes = True


# =========================
# INVENTORY SCHEMAS
# =========================

class InventoryCreate(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: int

    class Config:
        from_attributes = True


# =========================
# TRANSACTION SCHEMAS
# =========================

class InventoryTransactionCreate(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    transaction_type: str


class InventoryTransactionResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: int
    transaction_type: str

    class Config:
        from_attributes = True


# =========================
# REBALANCING SCHEMAS
# =========================

class RebalancingTransferRequest(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int