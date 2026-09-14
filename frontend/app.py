import streamlit as st
import requests
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Smart Inventory Rebalancer",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(99, 102, 241, 0.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 95% 10%,
            rgba(14, 165, 233, 0.10),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #f8fafc 0%,
            #eef2ff 48%,
            #f8fafc 100%
        );

    background-attachment: fixed;
}


/* Main content */

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            rgba(248, 250, 252, 0.97),
            rgba(238, 242, 255, 0.97)
        );

    border-right:
        1px solid rgba(148, 163, 184, 0.25);
}


.brand-box {
    padding:
        10px 4px 18px 4px;
}


.brand-title {

    font-size:
        1.45rem;

    font-weight:
        800;

    letter-spacing:
        -0.5px;

    color:
        #0f172a;
}


.brand-subtitle {

    color:
        #64748b;

    font-size:
        0.82rem;

    margin-top:
        4px;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    position:
        relative;

    overflow:
        hidden;

    padding:
        2.5rem 2.7rem;

    margin-bottom:
        1.8rem;

    border-radius:
        26px;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.82),
            rgba(238,242,255,0.68)
        );

    border:
        1px solid rgba(255,255,255,0.9);

    box-shadow:
        0 22px 55px rgba(15,23,42,0.09);

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);

    animation:
        fadeUp 0.7s ease-out;
}


.hero::after {

    content:
        "";

    position:
        absolute;

    width:
        300px;

    height:
        300px;

    right:
        -90px;

    top:
        -120px;

    border-radius:
        50%;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.20),
            rgba(14,165,233,0.12)
        );

    filter:
        blur(5px);

    animation:
        floatBlob 8s ease-in-out infinite;
}


.hero-title {

    position:
        relative;

    z-index:
        2;

    font-size:
        2.55rem;

    font-weight:
        850;

    letter-spacing:
        -1.5px;

    color:
        #0f172a;

    margin-bottom:
        0.45rem;
}


.hero-subtitle {

    position:
        relative;

    z-index:
        2;

    color:
        #64748b;

    font-size:
        1.05rem;

    max-width:
        760px;

    line-height:
        1.6;
}


/* ============================================================
   KPI CARDS
   ============================================================ */

div[data-testid="metric-container"] {

    background:
        rgba(255,255,255,0.66);

    border:
        1px solid rgba(255,255,255,0.88);

    border-radius:
        18px;

    padding:
        1.15rem 1.25rem;

    box-shadow:
        0 12px 30px rgba(15,23,42,0.055);

    backdrop-filter:
        blur(14px);

    -webkit-backdrop-filter:
        blur(14px);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;
}


div[data-testid="metric-container"]:hover {

    transform:
        translateY(-4px);

    box-shadow:
        0 18px 40px rgba(15,23,42,0.11);
}


div[data-testid="stMetricLabel"] {

    color:
        #64748b;

    font-weight:
        600;
}


div[data-testid="stMetricValue"] {

    color:
        #0f172a;

    font-weight:
        800;
}


/* ============================================================
   GLASS PANELS
   ============================================================ */

.glass-panel {

    background:
        rgba(255,255,255,0.62);

    border:
        1px solid rgba(255,255,255,0.86);

    border-radius:
        20px;

    padding:
        1.4rem;

    margin:
        0.6rem 0 1.2rem 0;

    box-shadow:
        0 12px 35px rgba(15,23,42,0.055);

    backdrop-filter:
        blur(15px);

    -webkit-backdrop-filter:
        blur(15px);

    animation:
        fadeUp 0.55s ease-out;
}


/* ============================================================
   SECTION TITLES
   ============================================================ */

.section-title {

    font-size:
        1.35rem;

    font-weight:
        800;

    color:
        #0f172a;

    margin-bottom:
        0.25rem;
}


.section-description {

    color:
        #64748b;

    font-size:
        0.92rem;

    margin-bottom:
        1rem;
}


/* ============================================================
   REBALANCING CARDS
   ============================================================ */

.recommendation-card {

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.82),
            rgba(239,246,255,0.72)
        );

    border:
        1px solid rgba(191,219,254,0.70);

    border-radius:
        18px;

    padding:
        1.35rem;

    margin:
        0.8rem 0;

    box-shadow:
        0 10px 28px rgba(30,64,175,0.065);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;

    animation:
        fadeUp 0.5s ease-out;
}


.recommendation-card:hover {

    transform:
        translateY(-3px);

    box-shadow:
        0 16px 35px rgba(30,64,175,0.11);
}


/* ============================================================
   ALERT CARDS
   ============================================================ */

.alert-card {

    border-radius:
        16px;

    padding:
        1rem 1.2rem;

    margin:
        0.6rem 0;

    background:
        rgba(255,255,255,0.70);

    border:
        1px solid rgba(255,255,255,0.85);

    box-shadow:
        0 8px 25px rgba(15,23,42,0.05);
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {

    border-radius:
        10px;

    border:
        1px solid rgba(99,102,241,0.25);

    font-weight:
        700;

    transition:
        all 0.2s ease;
}


.stButton > button:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 8px 20px rgba(15,23,42,0.10);
}


/* ============================================================
   DATA TABLE
   ============================================================ */

div[data-testid="stDataFrame"] {

    border-radius:
        14px;

    overflow:
        hidden;

    box-shadow:
        0 8px 24px rgba(15,23,42,0.05);
}


/* ============================================================
   FORMS
   ============================================================ */

div[data-testid="stForm"] {

    background:
        rgba(255,255,255,0.55);

    border:
        1px solid rgba(255,255,255,0.80);

    border-radius:
        18px;

    padding:
        1rem;

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);
}


/* ============================================================
   ANIMATIONS
   ============================================================ */

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(14px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


@keyframes floatBlob {

    0%, 100% {
        transform:
            translate(0,0);
    }

    50% {
        transform:
            translate(-20px,18px);
    }
}

</style>
""")


# ============================================================
# API HELPERS
# ============================================================

def get_data(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"API Error {response.status_code}: "
            f"{response.text}"
        )

        return None

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI. "
            "Make sure the backend server is running."
        )

        return None

    except Exception as e:

        st.error(f"Error: {e}")

        return None


def post_data(endpoint, data):

    try:

        return requests.post(
            f"{API_URL}{endpoint}",
            json=data,
            timeout=5
        )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI. "
            "Make sure the backend server is running."
        )

        return None

    except Exception as e:

        st.error(f"Error: {e}")

        return None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.html("""
<div class="brand-box">

    <div class="brand-title">
        📦 Smart Inventory
    </div>

    <div class="brand-subtitle">
        Intelligent Inventory Management
    </div>

</div>
""")


st.sidebar.divider()


page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Analytics",
        "Inventory",
        "Rebalancing",
        "Transactions",
        "Products",
        "Warehouses"
    ]
)


st.sidebar.divider()


st.sidebar.html("""
<div style="
    padding:14px;
    border-radius:14px;
    background:rgba(255,255,255,0.58);
    border:1px solid rgba(255,255,255,0.75);
">

    <div style="
        font-weight:800;
        color:#0f172a;
        margin-bottom:10px;
    ">
        System Status
    </div>

    <div style="
        color:#475569;
        line-height:1.8;
    ">
        🟢 FastAPI Backend<br>
        🟢 PostgreSQL Database<br>
        🟢 Live Inventory Data
    </div>

</div>
""")


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.html("""
    <div class="hero">

        <div class="hero-title">
            📊 Smart Inventory Dashboard
        </div>

        <div class="hero-subtitle">
            Monitor inventory levels, detect stock risks,
            and intelligently rebalance inventory across
            warehouses.
        </div>

    </div>
    """)


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    status_data = get_data(
        "/inventory/status"
    )

    products = get_data(
        "/products"
    )

    warehouses = get_data(
        "/warehouses"
    )

    recommendations_data = get_data(
        "/rebalancing/recommendations"
    )


    if (
        status_data is not None
        and products is not None
        and warehouses is not None
        and recommendations_data is not None
    ):

        inventory = status_data

        recommendations = recommendations_data


        # ----------------------------------------------------
        # KPI CALCULATIONS
        # ----------------------------------------------------

        total_products = len(products)

        total_warehouses = len(warehouses)

        total_stock = sum(
            item["quantity"]
            for item in inventory
        )

        low_stock_count = sum(
            1
            for item in inventory
            if item["status"] == "LOW"
        )


        # ----------------------------------------------------
        # TOP KPI ROW
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "📦 Total Products",
                total_products
            )


        with col2:

            st.metric(
                "🏭 Warehouses",
                total_warehouses
            )


        with col3:

            st.metric(
                "📈 Total Stock",
                total_stock
            )


        with col4:

            st.metric(
                "🔄 Recommendations",
                len(recommendations)
            )


        # ----------------------------------------------------
        # INVENTORY HEALTH
        # ----------------------------------------------------

        st.divider()


        st.html("""
        <div class="section-title">
            Inventory Intelligence
        </div>

        <div class="section-description">
            A real-time view of stock health and distribution.
        </div>
        """)


        status_counts = {
            "LOW": 0,
            "NORMAL": 0,
            "SURPLUS": 0
        }


        for item in inventory:

            status_counts[
                item["status"]
            ] += 1


        chart_col, warehouse_col = st.columns(2)


        # ----------------------------------------------------
        # HEALTH CHART
        # ----------------------------------------------------

        with chart_col:

            st.html("""
            <div class="glass-panel">

                <div class="section-title">
                    🩺 Inventory Health
                </div>

                <div class="section-description">
                    Distribution of inventory health states.
                </div>

            </div>
            """)


            health_df = pd.DataFrame(
                {
                    "Status": [
                        "Low",
                        "Normal",
                        "Surplus"
                    ],

                    "Items": [
                        status_counts["LOW"],
                        status_counts["NORMAL"],
                        status_counts["SURPLUS"]
                    ]
                }
            )


            st.bar_chart(
                health_df.set_index("Status"),
                use_container_width=True
            )


        # ----------------------------------------------------
        # WAREHOUSE STOCK
        # ----------------------------------------------------

        with warehouse_col:

            st.html("""
            <div class="glass-panel">

                <div class="section-title">
                    🏭 Stock by Warehouse
                </div>

                <div class="section-description">
                    Total units currently stored at each location.
                </div>

            </div>
            """)


            warehouse_stock = {}


            for item in inventory:

                warehouse_name = item[
                    "warehouse_name"
                ]

                warehouse_stock[
                    warehouse_name
                ] = (
                    warehouse_stock.get(
                        warehouse_name,
                        0
                    )
                    + item["quantity"]
                )


            warehouse_df = pd.DataFrame(
                {
                    "Warehouse":
                        list(
                            warehouse_stock.keys()
                        ),

                    "Stock":
                        list(
                            warehouse_stock.values()
                        )
                }
            )


            if not warehouse_df.empty:

                st.bar_chart(
                    warehouse_df.set_index(
                        "Warehouse"
                    ),
                    use_container_width=True
                )

            else:

                st.info(
                    "No warehouse inventory data."
                )


        # ----------------------------------------------------
        # PRODUCT STOCK
        # ----------------------------------------------------

        st.divider()


        st.html("""
        <div class="section-title">
            📦 Product Stock Distribution
        </div>

        <div class="section-description">
            See how inventory is distributed across products.
        </div>
        """)


        product_stock = {}


        for item in inventory:

            product_name = item[
                "product_name"
            ]

            product_stock[
                product_name
            ] = (
                product_stock.get(
                    product_name,
                    0
                )
                + item["quantity"]
            )


        product_df = pd.DataFrame(
            {
                "Product":
                    list(
                        product_stock.keys()
                    ),

                "Stock":
                    list(
                        product_stock.values()
                    )
            }
        )


        if not product_df.empty:

            st.bar_chart(
                product_df.set_index(
                    "Product"
                ),
                use_container_width=True
            )


        # ----------------------------------------------------
        # LOW STOCK ALERTS
        # ----------------------------------------------------

        st.divider()


        st.html("""
        <div class="section-title">
            ⚠️ Stock Risk Monitor
        </div>

        <div class="section-description">
            Products that require attention.
        </div>
        """)


        low_items = [
            item
            for item in inventory
            if item["status"] == "LOW"
        ]


        if low_items:

            for item in low_items:

                st.html(f"""
                <div class="alert-card">

                    🔴

                    <b>
                        {item['product_name']}
                    </b>

                    at

                    <b>
                        {item['warehouse_name']}
                    </b>

                    has only

                    <b>
                        {item['quantity']}
                    </b>

                    units.

                    Reorder threshold:

                    <b>
                        {item['reorder_threshold']}
                    </b>

                </div>
                """)

        else:

            st.success(
                "✓ All inventory locations are currently "
                "above or at their reorder thresholds."
            )


        # ----------------------------------------------------
        # REBALANCING OPPORTUNITIES
        # ----------------------------------------------------

        st.divider()


        st.html("""
        <div class="section-title">
            🔄 Rebalancing Opportunities
        </div>

        <div class="section-description">
            Intelligent transfer recommendations generated
            from current inventory conditions.
        </div>
        """)


        if recommendations:

            for index, recommendation in enumerate(
                recommendations
            ):

                st.html(f"""
                <div class="recommendation-card">

                    <div style="
                        font-size:1.2rem;
                        font-weight:800;
                        color:#0f172a;
                        margin-bottom:14px;
                    ">

                        📦 {recommendation['product_name']}

                    </div>

                    <div style="
                        font-size:1rem;
                        color:#475569;
                    ">

                        🟢
                        <b>
                            {recommendation['from_warehouse']}
                        </b>

                        <span style="
                            padding:0 18px;
                            font-size:1.4rem;
                        ">
                            →
                        </span>

                        🔴
                        <b>
                            {recommendation['to_warehouse']}
                        </b>

                    </div>

                    <br>

                    Suggested transfer:

                    <b>
                        {recommendation['quantity']}
                        units
                    </b>

                    &nbsp;&nbsp;•&nbsp;&nbsp;

                    Source:

                    <b>
                        {recommendation['source_stock']}
                    </b>

                    &nbsp;&nbsp;•&nbsp;&nbsp;

                    Destination:

                    <b>
                        {recommendation['destination_stock']}
                    </b>

                </div>
                """)


                if st.button(
                    "Execute Transfer",
                    key=f"dashboard_transfer_{index}"
                ):

                    transfer_data = {

                        "product_id":
                            recommendation[
                                "product_id"
                            ],

                        "from_warehouse_id":
                            recommendation[
                                "from_warehouse_id"
                            ],

                        "to_warehouse_id":
                            recommendation[
                                "to_warehouse_id"
                            ],

                        "quantity":
                            recommendation[
                                "quantity"
                            ]
                    }


                    response = post_data(
                        "/rebalancing/transfer",
                        transfer_data
                    )


                    if response is not None:

                        if response.status_code == 200:

                            st.success(
                                "✓ Transfer completed successfully."
                            )

                            st.rerun()

                        else:

                            try:

                                error = response.json()[
                                    "detail"
                                ]

                            except Exception:

                                error = response.text


                            st.error(error)

        else:

            st.success(
                "✓ No rebalancing required. "
                "Current warehouse stock is balanced."
            )


# ============================================================
# INVENTORY PAGE
# ============================================================

elif page == "Inventory":

    st.title("📦 Inventory")

    st.caption(
        "Live inventory status across all warehouses."
    )


    status_data = get_data(
        "/inventory/status"
    )


    if status_data is not None:

        inventory = status_data


        if inventory:

            st.dataframe(
                inventory,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No inventory records found."
            )


# ============================================================
# REBALANCING PAGE
# ============================================================

elif page == "Rebalancing":

    st.title("🔄 Inventory Rebalancing")

    st.caption(
        "Identify surplus stock and intelligently "
        "recommend transfers to warehouses below "
        "their reorder threshold."
    )


    recommendations_data = get_data(
        "/rebalancing/recommendations"
    )


    if recommendations_data is not None:

        recommendations = recommendations_data


        if not recommendations:

            st.success(
                "✓ No rebalancing required."
            )


        else:

            for index, recommendation in enumerate(
                recommendations
            ):

                st.html(f"""
                <div class="recommendation-card">

                    <div style="
                        font-size:1.2rem;
                        font-weight:800;
                        color:#0f172a;
                        margin-bottom:14px;
                    ">

                        Recommendation #{index + 1}

                    </div>

                    📦

                    <b>
                        {recommendation['product_name']}
                    </b>

                    <br><br>

                    🟢

                    <b>
                        {recommendation['from_warehouse']}
                    </b>

                    <span style="
                        padding:0 18px;
                        font-size:1.4rem;
                    ">
                        →
                    </span>

                    🔴

                    <b>
                        {recommendation['to_warehouse']}
                    </b>

                    <br><br>

                    Suggested transfer:

                    <b>
                        {recommendation['quantity']}
                        units
                    </b>

                    <br><br>

                    Source stock:

                    <b>
                        {recommendation['source_stock']}
                    </b>

                    &nbsp;&nbsp; | &nbsp;&nbsp;

                    Destination stock:

                    <b>
                        {recommendation['destination_stock']}
                    </b>

                    <br>

                    Reorder threshold:

                    <b>
                        {recommendation['reorder_threshold']}
                    </b>

                    <br><br>

                    💡

                    {recommendation['reason']}

                </div>
                """)


                if st.button(
                    "Execute Transfer",
                    key=f"rebalance_transfer_{index}"
                ):

                    transfer_data = {

                        "product_id":
                            recommendation[
                                "product_id"
                            ],

                        "from_warehouse_id":
                            recommendation[
                                "from_warehouse_id"
                            ],

                        "to_warehouse_id":
                            recommendation[
                                "to_warehouse_id"
                            ],

                        "quantity":
                            recommendation[
                                "quantity"
                            ]
                    }


                    response = post_data(
                        "/rebalancing/transfer",
                        transfer_data
                    )


                    if response is not None:

                        if response.status_code == 200:

                            st.success(
                                "✓ Inventory transferred successfully."
                            )

                            st.rerun()

                        else:

                            try:

                                error = response.json()[
                                    "detail"
                                ]

                            except Exception:

                                error = response.text


                            st.error(error)

# ============================================================
# ANALYTICS PAGE
# ============================================================

elif page == "Analytics":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            📈 Inventory Analytics
        </div>

        <div class="hero-subtitle">
            Analyze inventory health, stock distribution,
            and warehouse activity using live operational data.
        </div>

    </div>
    """)

    analytics = get_data(
        "/analytics"
    )

    if analytics is not None:

        summary = analytics["summary"]

        product_stock = analytics["product_stock"]

        warehouse_stock = analytics["warehouse_stock"]

        product_activity = analytics[
            "product_transaction_activity"
        ]

        recent_transactions = analytics[
            "recent_transactions"
        ]

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "📦 Total Stock",
                summary["total_stock"]
            )

        with col2:

            st.metric(
                "📝 Transactions",
                summary["total_transactions"]
            )

        with col3:

            st.metric(
                "📥 Units IN",
                summary["total_units_in"]
            )

        with col4:

            st.metric(
                "📤 Units OUT",
                summary["total_units_out"]
            )

        st.divider()

        # ----------------------------------------------------
        # INVENTORY HEALTH
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            🩺 Inventory Health
        </div>

        <div class="section-description">
            Current distribution of inventory records by stock state.
        </div>
        """)

        health_df = pd.DataFrame(
            {
                "Status": [
                    "Low",
                    "Normal",
                    "Surplus"
                ],

                "Items": [
                    summary["low_stock_items"],
                    summary["normal_stock_items"],
                    summary["surplus_stock_items"]
                ]
            }
        )

        st.bar_chart(
            health_df.set_index("Status"),
            use_container_width=True
        )

        st.divider()

        # ----------------------------------------------------
        # STOCK DISTRIBUTION
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            📊 Stock Distribution
        </div>

        <div class="section-description">
            Compare the amount of inventory held by each warehouse
            and product.
        </div>
        """)

        col1, col2 = st.columns(2)

        with col1:

            st.html("""
            <div class="glass-panel">

                <div class="section-title">
                    🏭 Stock by Warehouse
                </div>

                <div class="section-description">
                    Total units currently stored at each warehouse.
                </div>

            </div>
            """)

            warehouse_df = pd.DataFrame(
                {
                    "Warehouse":
                        list(
                            warehouse_stock.keys()
                        ),

                    "Stock":
                        list(
                            warehouse_stock.values()
                        )
                }
            )

            if not warehouse_df.empty:

                st.bar_chart(
                    warehouse_df.set_index(
                        "Warehouse"
                    ),
                    use_container_width=True
                )

            else:

                st.info(
                    "No warehouse stock data available."
                )

        with col2:

            st.html("""
            <div class="glass-panel">

                <div class="section-title">
                    📦 Stock by Product
                </div>

                <div class="section-description">
                    Total units currently held for each product.
                </div>

            </div>
            """)

            product_df = pd.DataFrame(
                {
                    "Product":
                        list(
                            product_stock.keys()
                        ),

                    "Stock":
                        list(
                            product_stock.values()
                        )
                }
            )

            if not product_df.empty:

                st.bar_chart(
                    product_df.set_index(
                        "Product"
                    ),
                    use_container_width=True
                )

            else:

                st.info(
                    "No product stock data available."
                )

        st.divider()

        # ----------------------------------------------------
        # TRANSACTION ACTIVITY
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            🔄 Transaction Activity
        </div>

        <div class="section-description">
            Total units involved in inventory movements for each product.
        </div>
        """)

        activity_df = pd.DataFrame(
            {
                "Product":
                    list(
                        product_activity.keys()
                    ),

                "Units Moved":
                    list(
                        product_activity.values()
                    )
            }
        )

        if not activity_df.empty:

            st.bar_chart(
                activity_df.set_index("Product"),
                use_container_width=True
            )

        else:

            st.info(
                "No transaction activity available."
            )

        st.divider()

        # ----------------------------------------------------
        # INVENTORY SUMMARY
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            📋 Inventory Summary
        </div>

        <div class="section-description">
            High-level operational statistics.
        </div>
        """)

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.metric(
                "🛒 Products",
                summary["total_products"]
            )

            st.metric(
                "🏭 Warehouses",
                summary["total_warehouses"]
            )

        with summary_col2:

            st.metric(
                "🔴 Low Stock",
                summary["low_stock_items"]
            )

            st.metric(
                "🟢 Surplus Stock",
                summary["surplus_stock_items"]
            )


# ============================================================
# TRANSACTIONS PAGE
# ============================================================

elif page == "Transactions":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            📝 Transaction Audit Log
        </div>

        <div class="hero-subtitle">
            A complete history of inventory movements,
            including stock receipts, dispatches and
            warehouse transfers.
        </div>

    </div>
    """)

    analytics = get_data(
        "/analytics"
    )

    if analytics is not None:

        transactions = analytics[
            "recent_transactions"
        ]

        # ----------------------------------------------------
        # TRANSACTION KPIs
        # ----------------------------------------------------

        summary = analytics["summary"]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📝 Total Transactions",
                summary["total_transactions"]
            )

        with col2:

            st.metric(
                "📥 Total IN",
                summary["total_units_in"]
            )

        with col3:

            st.metric(
                "📤 Total OUT",
                summary["total_units_out"]
            )

        st.divider()

        # ----------------------------------------------------
        # AUDIT TABLE
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            📋 Recent Inventory Movements
        </div>

        <div class="section-description">
            The 20 most recent inventory transactions.
        </div>
        """)

        if transactions:

            transaction_rows = []

            for transaction in transactions:

                transaction_type = transaction["type"]

                if transaction_type == "IN":

                    movement = "📥 IN"

                else:

                    movement = "📤 OUT"

                transaction_rows.append(
                    {
                        "ID":
                            transaction[
                                "transaction_id"
                            ],

                        "Product":
                            transaction[
                                "product"
                            ],

                        "Warehouse":
                            transaction[
                                "warehouse"
                            ],

                        "Movement":
                            movement,

                        "Quantity":
                            transaction[
                                "quantity"
                            ],

                        "Timestamp":
                            transaction[
                                "created_at"
                            ]
                    }
                )

            transaction_df = pd.DataFrame(
                transaction_rows
            )

            st.dataframe(
                transaction_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No inventory transactions recorded yet."
            )

        st.divider()

        # ----------------------------------------------------
        # TRANSACTION BREAKDOWN
        # ----------------------------------------------------

        st.html("""
        <div class="section-title">
            📊 Transaction Breakdown
        </div>

        <div class="section-description">
            Compare incoming and outgoing inventory activity.
        </div>
        """)

        breakdown_df = pd.DataFrame(
            {
                "Movement": [
                    "IN",
                    "OUT"
                ],

                "Units": [
                    summary["total_units_in"],
                    summary["total_units_out"]
                ]
            }
        )

        st.bar_chart(
            breakdown_df.set_index("Movement"),
            use_container_width=True
        )

# ============================================================
# PRODUCTS PAGE
# ============================================================

elif page == "Products":

    st.title("🛒 Products")

    st.caption(
        "Manage products and their reorder thresholds."
    )


    products = get_data(
        "/products"
    )


    if products is not None:

        if products:

            st.dataframe(
                products,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No products found."
            )


    st.divider()


    st.subheader("➕ Add Product")


    with st.form("add_product_form"):

        name = st.text_input(
            "Product Name"
        )

        sku = st.text_input(
            "SKU"
        )

        reorder_threshold = st.number_input(
            "Reorder Threshold",
            min_value=0,
            value=10,
            step=1
        )


        submitted = st.form_submit_button(
            "Add Product"
        )


        if submitted:

            if not name or not sku:

                st.warning(
                    "Please enter both product name and SKU."
                )

            else:

                product_data = {

                    "name": name,

                    "sku": sku,

                    "reorder_threshold":
                        reorder_threshold
                }


                response = post_data(
                    "/products",
                    product_data
                )


                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✓ Product added successfully."
                        )

                        st.rerun()

                    else:

                        try:

                            error = response.json()[
                                "detail"
                            ]

                        except Exception:

                            error = response.text


                        st.error(error)


# ============================================================
# WAREHOUSES PAGE
# ============================================================

elif page == "Warehouses":

    st.title("🏭 Warehouses")

    st.caption(
        "Manage warehouse locations."
    )


    warehouses = get_data(
        "/warehouses"
    )


    if warehouses is not None:

        if warehouses:

            st.dataframe(
                warehouses,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No warehouses found."
            )


    st.divider()


    st.subheader("➕ Add Warehouse")


    with st.form("add_warehouse_form"):

        name = st.text_input(
            "Warehouse Name"
        )

        location = st.text_input(
            "Location"
        )


        submitted = st.form_submit_button(
            "Add Warehouse"
        )


        if submitted:

            if not name or not location:

                st.warning(
                    "Please enter warehouse name and location."
                )

            else:

                warehouse_data = {

                    "name": name,

                    "location": location
                }


                response = post_data(
                    "/warehouses",
                    warehouse_data
                )


                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✓ Warehouse added successfully."
                        )

                        st.rerun()

                    else:

                        try:

                            error = response.json()[
                                "detail"
                            ]

                        except Exception:

                            error = response.text


                        st.error(error)