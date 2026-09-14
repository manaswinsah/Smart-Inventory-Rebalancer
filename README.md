# Smart Inventory Rebalancer



A full-stack inventory management and warehouse rebalancing system that monitors stock levels across warehouses and recommends inventory transfers when one warehouse has low stock and another has surplus inventory.



## Overview



The Smart Inventory Rebalancer helps businesses maintain balanced inventory across multiple warehouses.



The system tracks:



* Products

* Warehouses

* Inventory levels

* Inventory transactions

* Rebalancing recommendations

* Warehouse-to-warehouse stock transfers

* Inventory status and analytics



When inventory at a warehouse falls below its reorder threshold, the system can identify surplus stock at another warehouse and recommend a transfer.



## Key Features



### Inventory Management



* View inventory across warehouses

* Track product quantities

* Configure reorder thresholds

* Automatically determine inventory status



### Inventory Status



Inventory is classified based on its current quantity and reorder threshold.



For example:



* **LOW** — stock is below the reorder threshold

* **NORMAL** — stock is at or above the reorder threshold

* **SURPLUS** — stock is significantly above the required level



### Rebalancing Recommendations



The system compares inventory levels across warehouses.



If one warehouse has low stock while another has surplus stock, the system generates a recommendation containing:



* Product

* Source warehouse

* Destination warehouse

* Suggested transfer quantity

* Source stock

* Destination stock

* Reorder threshold

* Reason for the recommendation



### Warehouse Transfers



A recommended transfer can be executed through the application.



When a transfer is executed:



1. Stock is removed from the source warehouse.

2. Stock is added to the destination warehouse.

3. An `OUT` transaction is recorded for the source.

4. An `IN` transaction is recorded for the destination.

5. Inventory status is recalculated.



### Transaction Tracking



The system records inventory movements using:



* `IN` transactions

* `OUT` transactions



This provides a history of inventory changes.



### Analytics Dashboard



The Streamlit frontend provides dashboard and analytics views for monitoring inventory and warehouse activity.



## Technology Stack



### Backend



* Python

* FastAPI

* SQLAlchemy

* PostgreSQL



### Frontend



* Streamlit



### Database



* PostgreSQL



### Testing



* Pytest



### HTTP Communication



* Requests



## Project Structure



```text

smart-inventory/

│

├── backend/

│   ├── database.py

│   ├── main.py

│   ├── models.py

│   ├── schemas.py

│   ├── test_database.py

│   └── test_main.py

│

├── frontend/

│   └── app.py

│

├── .gitignore

├── README.md

└── venv/

```



## System Architecture



```text

┌─────────────────────────┐

│   Streamlit Frontend    │

│                         │

│ Dashboard / Inventory   │

│ Analytics / Rebalancing │

│ Transactions / Products │

│ Warehouses              │

└────────────┬────────────┘

&#x20;            │ HTTP Requests

&#x20;            ▼

┌─────────────────────────┐

│      FastAPI Backend    │

│                         │

│ Inventory APIs          │

│ Transaction APIs        │

│ Rebalancing Logic       │

│ Analytics APIs          │

└────────────┬────────────┘

&#x20;            │ SQLAlchemy

&#x20;            ▼

┌─────────────────────────┐

│      PostgreSQL         │

│                         │

│ Products                │

│ Warehouses              │

│ Inventory               │

│ Transactions            │

└─────────────────────────┘

```



## Rebalancing Logic



The core workflow is:



```text

Inventory Transaction

&#x20;       ↓

Inventory Quantity Updated

&#x20;       ↓

Inventory Status Calculated

&#x20;       ↓

LOW Stock Detected

&#x20;       ↓

Search for Surplus Warehouse

&#x20;       ↓

Calculate Transfer Quantity

&#x20;       ↓

Generate Recommendation

&#x20;       ↓

Execute Transfer

&#x20;       ↓

OUT + IN Transactions

&#x20;       ↓

Updated Inventory

```



## Example



Suppose a product has the following inventory:



| Warehouse       | Stock | Status  |

| --------------- | ----: | ------- |

| Main Warehouse  |    45 | SURPLUS |

| Delhi Warehouse |     5 | LOW     |



If the reorder threshold for the product is `10`, the system recommends:



```text

Transfer: 5 units



Main Warehouse → Delhi Warehouse

```



After executing the transfer:



| Warehouse       | Before | Transfer | After |

| --------------- | -----: | -------: | ----: |

| Main Warehouse  |     45 |       -5 |    40 |

| Delhi Warehouse |      5 |       +5 |    10 |



The system also records:



```text

Main Warehouse: OUT 5

Delhi Warehouse: IN 5

```



Delhi's inventory then reaches its reorder threshold and is no longer classified as LOW.



## Running the Project



### 1. Activate the virtual environment



From the project root:



```powershell

.venvScriptsActivate.ps1

```



### 2. Start the FastAPI backend



```powershell

cd backend

uvicorn main:app --reload

```



The backend runs at:



```text

http://127.0.0.1:8000

```



### 3. Start the Streamlit frontend



Open another PowerShell window and navigate to the project:



```powershell

cd C:Usersmanassmart-inventory

.venvScriptsActivate.ps1

cd frontend

streamlit run app.py

```



The Streamlit application will provide the local URL in the terminal.



## Running Tests



From the `backend` directory:



```powershell

pytest

```



The current test suite passes successfully.



## Future Improvements



Potential future enhancements include:



* Authentication and role-based access

* More advanced demand forecasting

* Automated reorder suggestions

* Historical inventory trend analysis

* More detailed reporting

* Scheduled rebalancing

* Multi-product transfer optimization

* Deployment to a cloud platform



## Project Status



**Core functionality complete and tested.**



The current implementation successfully supports inventory management, transaction tracking, stock-status detection, rebalancing recommendations, warehouse transfers, and analytics through a FastAPI + PostgreSQL backend and Streamlit frontend.



