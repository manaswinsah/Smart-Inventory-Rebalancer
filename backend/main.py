from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import Base, engine, get_db
import models

from schemas import (
    ProductCreate,
    ProductResponse,
    WarehouseCreate,
    WarehouseResponse,
    InventoryCreate,
    InventoryResponse,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
    RebalancingTransferRequest
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

# Database tables are managed separately.
# This prevents tests from modifying the production database.


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Smart Inventory Management System",
    description=(
        "Backend API for inventory management, "
        "stock monitoring and intelligent rebalancing"
    ),
    version="1.0.0"
)


# ============================================================
# ROOT & HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Smart Inventory Management System API is running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# PRODUCTS
# ============================================================

@app.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Product
    ).all()


@app.post(
    "/products",
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = (
        db.query(models.Product)
        .filter(
            models.Product.sku == product.sku
        )
        .first()
    )

    if existing_product:

        raise HTTPException(
            status_code=400,
            detail="A product with this SKU already exists"
        )

    new_product = models.Product(
        name=product.name.strip(),
        sku=product.sku.strip(),
        reorder_threshold=product.reorder_threshold
    )

    try:

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create product"
        )

    return new_product


# ============================================================
# WAREHOUSES
# ============================================================

@app.get(
    "/warehouses",
    response_model=list[WarehouseResponse]
)
def get_warehouses(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Warehouse
    ).all()


@app.post(
    "/warehouses",
    response_model=WarehouseResponse
)
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db)
):

    new_warehouse = models.Warehouse(
        name=warehouse.name.strip(),
        location=warehouse.location.strip()
    )

    try:

        db.add(new_warehouse)
        db.commit()
        db.refresh(new_warehouse)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create warehouse"
        )

    return new_warehouse


# ============================================================
# INVENTORY
# ============================================================

@app.get(
    "/inventory",
    response_model=list[InventoryResponse]
)
def get_inventory(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Inventory
    ).all()


@app.post(
    "/inventory",
    response_model=InventoryResponse
)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check product
    # --------------------------------------------------------

    product = (
        db.query(models.Product)
        .filter(
            models.Product.id == inventory.product_id
        )
        .first()
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    # --------------------------------------------------------
    # Check warehouse
    # --------------------------------------------------------

    warehouse = (
        db.query(models.Warehouse)
        .filter(
            models.Warehouse.id == inventory.warehouse_id
        )
        .first()
    )

    if not warehouse:

        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )


    # --------------------------------------------------------
    # Prevent duplicate inventory records
    # --------------------------------------------------------

    existing_inventory = (
        db.query(models.Inventory)
        .filter(
            models.Inventory.product_id
            == inventory.product_id,

            models.Inventory.warehouse_id
            == inventory.warehouse_id
        )
        .first()
    )

    if existing_inventory:

        raise HTTPException(
            status_code=400,
            detail=(
                "Inventory already exists for "
                "this product and warehouse"
            )
        )


    new_inventory = models.Inventory(
        product_id=inventory.product_id,
        warehouse_id=inventory.warehouse_id,
        quantity=inventory.quantity
    )


    try:

        db.add(new_inventory)
        db.commit()
        db.refresh(new_inventory)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create inventory record"
        )

    return new_inventory


# ============================================================
# INVENTORY TRANSACTIONS
# ============================================================

@app.get(
    "/inventory/transactions",
    response_model=list[InventoryTransactionResponse]
)
def get_inventory_transactions(
    db: Session = Depends(get_db)
):

    return db.query(
        models.InventoryTransaction
    ).order_by(
        models.InventoryTransaction.id.desc()
    ).all()


@app.post(
    "/inventory/transactions",
    response_model=InventoryTransactionResponse
)
def create_inventory_transaction(
    transaction: InventoryTransactionCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check product
    # --------------------------------------------------------

    product = (
        db.query(models.Product)
        .filter(
            models.Product.id
            == transaction.product_id
        )
        .first()
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    # --------------------------------------------------------
    # Check warehouse
    # --------------------------------------------------------

    warehouse = (
        db.query(models.Warehouse)
        .filter(
            models.Warehouse.id
            == transaction.warehouse_id
        )
        .first()
    )

    if not warehouse:

        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )


    # --------------------------------------------------------
    # Find inventory
    # --------------------------------------------------------

    inventory = (
        db.query(models.Inventory)
        .filter(
            models.Inventory.product_id
            == transaction.product_id,

            models.Inventory.warehouse_id
            == transaction.warehouse_id
        )
        .first()
    )

    if not inventory:

        raise HTTPException(
            status_code=404,
            detail=(
                "Inventory record not found for "
                "this product and warehouse"
            )
        )


    # --------------------------------------------------------
    # Apply transaction
    # --------------------------------------------------------

    if transaction.transaction_type == "IN":

        inventory.quantity += transaction.quantity


    else:

        if inventory.quantity < transaction.quantity:

            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )

        inventory.quantity -= transaction.quantity


    # --------------------------------------------------------
    # Record transaction
    # --------------------------------------------------------

    new_transaction = models.InventoryTransaction(
        product_id=transaction.product_id,
        warehouse_id=transaction.warehouse_id,
        quantity=transaction.quantity,
        transaction_type=transaction.transaction_type
    )


    try:

        db.add(new_transaction)

        db.commit()

        db.refresh(new_transaction)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Transaction failed and was rolled back"
        )

    return new_transaction


# ============================================================
# STOCK STATUS
# ============================================================

@app.get("/inventory/status")
def get_inventory_status(
    db: Session = Depends(get_db)
):

    inventory_records = (
        db.query(models.Inventory)
        .all()
    )

    products = {
        product.id: product
        for product in db.query(
            models.Product
        ).all()
    }

    warehouses = {
        warehouse.id: warehouse
        for warehouse in db.query(
            models.Warehouse
        ).all()
    }

    result = []


    for inventory in inventory_records:

        product = products.get(
            inventory.product_id
        )

        warehouse = warehouses.get(
            inventory.warehouse_id
        )

        if not product or not warehouse:
            continue


        if inventory.quantity < product.reorder_threshold:

            status = "LOW"

        elif inventory.quantity == product.reorder_threshold:

            status = "NORMAL"

        else:

            status = "SURPLUS"


        result.append({

            "product_id":
                product.id,

            "product_name":
                product.name,

            "warehouse_id":
                warehouse.id,

            "warehouse_name":
                warehouse.name,

            "quantity":
                inventory.quantity,

            "reorder_threshold":
                product.reorder_threshold,

            "status":
                status
        })


    return result


# ============================================================
# REBALANCING RECOMMENDATIONS
# ============================================================

@app.get("/rebalancing/recommendations")
def get_rebalancing_recommendations(
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Load everything once
    # --------------------------------------------------------

    products = (
        db.query(models.Product)
        .all()
    )

    warehouses = {
        warehouse.id: warehouse
        for warehouse in db.query(
            models.Warehouse
        ).all()
    }

    inventory_records = (
        db.query(models.Inventory)
        .all()
    )


    # --------------------------------------------------------
    # Group inventory by product
    # --------------------------------------------------------

    inventory_by_product = {}


    for inventory in inventory_records:

        inventory_by_product.setdefault(
            inventory.product_id,
            []
        ).append(inventory)


    recommendations = []


    # ========================================================
    # PROCESS EACH PRODUCT
    # ========================================================

    for product in products:

        product_inventory = (
            inventory_by_product.get(
                product.id,
                []
            )
        )


        shortages = []
        surpluses = []


        # ----------------------------------------------------
        # Identify shortages and surpluses
        # ----------------------------------------------------

        for inventory in product_inventory:

            warehouse = warehouses.get(
                inventory.warehouse_id
            )

            if not warehouse:
                continue


            # -----------------------------------------------
            # LOW STOCK
            # -----------------------------------------------

            if (
                inventory.quantity
                < product.reorder_threshold
            ):

                shortages.append({

                    "inventory": inventory,

                    "warehouse": warehouse,

                    "shortage":
                        product.reorder_threshold
                        - inventory.quantity
                })


            # -----------------------------------------------
            # SURPLUS STOCK
            # -----------------------------------------------

            elif (
                inventory.quantity
                > product.reorder_threshold
            ):

                surpluses.append({

                    "inventory": inventory,

                    "warehouse": warehouse,

                    "surplus":
                        inventory.quantity
                        - product.reorder_threshold
                })


        # ----------------------------------------------------
        # Sort largest shortages first
        # ----------------------------------------------------

        shortages.sort(
            key=lambda item:
                item["shortage"],
            reverse=True
        )


        # ----------------------------------------------------
        # Sort largest surpluses first
        # ----------------------------------------------------

        surpluses.sort(
            key=lambda item:
                item["surplus"],
            reverse=True
        )


        # ====================================================
        # MATCH SURPLUS → SHORTAGE
        # ====================================================

        for shortage_data in shortages:

            remaining_shortage = (
                shortage_data["shortage"]
            )


            for surplus_data in surpluses:

                if remaining_shortage <= 0:
                    break


                if surplus_data["surplus"] <= 0:
                    continue


                transfer_quantity = min(

                    remaining_shortage,

                    surplus_data["surplus"]
                )


                recommendations.append({

                    "product_id":
                        product.id,

                    "product_name":
                        product.name,

                    "from_warehouse_id":
                        surplus_data[
                            "warehouse"
                        ].id,

                    "from_warehouse":
                        surplus_data[
                            "warehouse"
                        ].name,

                    "to_warehouse_id":
                        shortage_data[
                            "warehouse"
                        ].id,

                    "to_warehouse":
                        shortage_data[
                            "warehouse"
                        ].name,

                    "quantity":
                        transfer_quantity,

                    "source_stock":
                        surplus_data[
                            "inventory"
                        ].quantity,

                    "destination_stock":
                        shortage_data[
                            "inventory"
                        ].quantity,

                    "reorder_threshold":
                        product.reorder_threshold,

                    "source_status":
                        "SURPLUS",

                    "destination_status":
                        "LOW",

                    "reason":
                        (
                            f"{shortage_data['warehouse'].name} "
                            f"is below the reorder threshold"
                        )
                })


                remaining_shortage -= (
                    transfer_quantity
                )

                surplus_data["surplus"] -= (
                    transfer_quantity
                )


    return recommendations


# ============================================================
# ACTUAL STOCK TRANSFER
# ============================================================

@app.post("/rebalancing/transfer")
def transfer_inventory(
    transfer: RebalancingTransferRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Prevent same warehouse transfer
    # --------------------------------------------------------

    if (
        transfer.from_warehouse_id
        == transfer.to_warehouse_id
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Source and destination warehouses "
                "must be different"
            )
        )


    # --------------------------------------------------------
    # Check product
    # --------------------------------------------------------

    product = (
        db.query(models.Product)
        .filter(
            models.Product.id
            == transfer.product_id
        )
        .first()
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    # --------------------------------------------------------
    # Check source warehouse
    # --------------------------------------------------------

    source_warehouse = (
        db.query(models.Warehouse)
        .filter(
            models.Warehouse.id
            == transfer.from_warehouse_id
        )
        .first()
    )

    if not source_warehouse:

        raise HTTPException(
            status_code=404,
            detail="Source warehouse not found"
        )


    # --------------------------------------------------------
    # Check destination warehouse
    # --------------------------------------------------------

    destination_warehouse = (
        db.query(models.Warehouse)
        .filter(
            models.Warehouse.id
            == transfer.to_warehouse_id
        )
        .first()
    )

    if not destination_warehouse:

        raise HTTPException(
            status_code=404,
            detail="Destination warehouse not found"
        )


    # --------------------------------------------------------
    # Find source inventory
    # --------------------------------------------------------

    source_inventory = (
        db.query(models.Inventory)
        .filter(
            models.Inventory.product_id
            == transfer.product_id,

            models.Inventory.warehouse_id
            == transfer.from_warehouse_id
        )
        .first()
    )

    if not source_inventory:

        raise HTTPException(
            status_code=404,
            detail="Source inventory record not found"
        )


    # --------------------------------------------------------
    # Find destination inventory
    # --------------------------------------------------------

    destination_inventory = (
        db.query(models.Inventory)
        .filter(
            models.Inventory.product_id
            == transfer.product_id,

            models.Inventory.warehouse_id
            == transfer.to_warehouse_id
        )
        .first()
    )

    if not destination_inventory:

        raise HTTPException(
            status_code=404,
            detail="Destination inventory record not found"
        )


    # --------------------------------------------------------
    # Check source stock
    # --------------------------------------------------------

    if (
        source_inventory.quantity
        < transfer.quantity
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Insufficient stock in source warehouse"
            )
        )


    # --------------------------------------------------------
    # Prevent source from becoming LOW
    # --------------------------------------------------------

    remaining_source_stock = (
        source_inventory.quantity
        - transfer.quantity
    )


    if (
        remaining_source_stock
        < product.reorder_threshold
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Transfer would reduce source warehouse "
                "below its reorder threshold"
            )
        )


    # ========================================================
    # PERFORM TRANSFER
    # ========================================================

    source_inventory.quantity -= (
        transfer.quantity
    )

    destination_inventory.quantity += (
        transfer.quantity
    )


    # --------------------------------------------------------
    # Record OUT transaction
    # --------------------------------------------------------

    source_transaction = (
        models.InventoryTransaction(

            product_id=
                transfer.product_id,

            warehouse_id=
                transfer.from_warehouse_id,

            quantity=
                transfer.quantity,

            transaction_type=
                "OUT"
        )
    )


    # --------------------------------------------------------
    # Record IN transaction
    # --------------------------------------------------------

    destination_transaction = (
        models.InventoryTransaction(

            product_id=
                transfer.product_id,

            warehouse_id=
                transfer.to_warehouse_id,

            quantity=
                transfer.quantity,

            transaction_type=
                "IN"
        )
    )


    # --------------------------------------------------------
    # Commit entire operation together
    # --------------------------------------------------------

    try:

        db.add(source_transaction)

        db.add(destination_transaction)

        db.commit()

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Transfer failed. "
                "All database changes were rolled back."
            )
        )


    return {

        "message":
            "Inventory transferred successfully",

        "product_id":
            transfer.product_id,

        "product_name":
            product.name,

        "from_warehouse":
            source_warehouse.name,

        "to_warehouse":
            destination_warehouse.name,

        "quantity_transferred":
            transfer.quantity,

        "source_remaining_stock":
            source_inventory.quantity,

        "destination_new_stock":
            destination_inventory.quantity
    }

# ============================================================
# INVENTORY ANALYTICS
# ============================================================

@app.get("/analytics")
def get_inventory_analytics(
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    products = db.query(
        models.Product
    ).all()

    warehouses = db.query(
        models.Warehouse
    ).all()

    inventory_records = db.query(
        models.Inventory
    ).all()

    transactions = (
        db.query(models.InventoryTransaction)
        .order_by(
            models.InventoryTransaction.id.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # BASIC INVENTORY METRICS
    # --------------------------------------------------------

    total_products = len(products)

    total_warehouses = len(warehouses)

    total_stock = sum(
        inventory.quantity
        for inventory in inventory_records
    )

    low_stock_items = 0

    normal_stock_items = 0

    surplus_stock_items = 0

    for inventory in inventory_records:

        product = next(
            (
                product
                for product in products
                if product.id == inventory.product_id
            ),
            None
        )

        if not product:
            continue

        if inventory.quantity < product.reorder_threshold:

            low_stock_items += 1

        elif inventory.quantity == product.reorder_threshold:

            normal_stock_items += 1

        else:

            surplus_stock_items += 1

    # --------------------------------------------------------
    # TRANSACTION METRICS
    # --------------------------------------------------------

    total_transactions = len(transactions)

    total_units_in = sum(
        transaction.quantity
        for transaction in transactions
        if transaction.transaction_type == "IN"
    )

    total_units_out = sum(
        transaction.quantity
        for transaction in transactions
        if transaction.transaction_type == "OUT"
    )

    # --------------------------------------------------------
    # PRODUCT STOCK
    # --------------------------------------------------------

    product_stock = {}

    for product in products:

        product_stock[product.name] = 0

    for inventory in inventory_records:

        product = next(
            (
                product
                for product in products
                if product.id == inventory.product_id
            ),
            None
        )

        if product:

            product_stock[product.name] += (
                inventory.quantity
            )

    # --------------------------------------------------------
    # WAREHOUSE STOCK
    # --------------------------------------------------------

    warehouse_stock = {}

    for warehouse in warehouses:

        warehouse_stock[warehouse.name] = (
            warehouse_stock.get(
                warehouse.name,
                0
            )
        )

    for inventory in inventory_records:

        warehouse = next(
            (
                warehouse
                for warehouse in warehouses
                if warehouse.id == inventory.warehouse_id
            ),
            None
        )

        if warehouse:

            warehouse_stock[warehouse.name] = (
                warehouse_stock.get(
                    warehouse.name,
                    0
                )
                + inventory.quantity
            )

    # --------------------------------------------------------
    # TRANSACTION ACTIVITY
    # --------------------------------------------------------

    product_transaction_activity = {}

    for product in products:

        product_transaction_activity[
            product.name
        ] = 0

    for transaction in transactions:

        product = next(
            (
                product
                for product in products
                if product.id == transaction.product_id
            ),
            None
        )

        if product:

            product_transaction_activity[
                product.name
            ] += transaction.quantity

    # --------------------------------------------------------
    # RECENT TRANSACTIONS
    # --------------------------------------------------------

    recent_transactions = []

    warehouse_lookup = {
        warehouse.id: warehouse.name
        for warehouse in warehouses
    }

    product_lookup = {
        product.id: product.name
        for product in products
    }

    for transaction in transactions[:20]:

        recent_transactions.append({

            "transaction_id":
                transaction.id,

            "product":
                product_lookup.get(
                    transaction.product_id,
                    "Unknown"
                ),

            "warehouse":
                warehouse_lookup.get(
                    transaction.warehouse_id,
                    "Unknown"
                ),

            "quantity":
                transaction.quantity,

            "type":
                transaction.transaction_type,

            "created_at":
                transaction.created_at
        })

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "summary": {

            "total_products":
                total_products,

            "total_warehouses":
                total_warehouses,

            "total_stock":
                total_stock,

            "low_stock_items":
                low_stock_items,

            "normal_stock_items":
                normal_stock_items,

            "surplus_stock_items":
                surplus_stock_items,

            "total_transactions":
                total_transactions,

            "total_units_in":
                total_units_in,

            "total_units_out":
                total_units_out
        },

        "product_stock":
            product_stock,

        "warehouse_stock":
            warehouse_stock,

        "product_transaction_activity":
            product_transaction_activity,

        "recent_transactions":
            recent_transactions
    }