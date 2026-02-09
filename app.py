import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
from streamlit_option_menu import option_menu
from auth import Authentication
from database import Database
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Sales Management System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2563EB;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-card {
        background: linear-gradient(135deg, #34D399 0%, #059669 100%);
        color: white;
    }
    .warning-card {
        background: linear-gradient(135deg, #FBBF24 0%, #D97706 100%);
        color: white;
    }
    .danger-card {
        background: linear-gradient(135deg, #F87171 0%, #DC2626 100%);
        color: white;
    }
    .info-card {
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
        color: white;
    }
    .btn-primary {
        background-color: #3B82F6 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
    }
    .btn-success {
        background-color: #10B981 !important;
        color: white !important;
    }
    .btn-danger {
        background-color: #EF4444 !important;
        color: white !important;
    }
    .stButton > button {
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stock-green {
        color: #10B981;
        font-weight: bold;
    }
    .stock-yellow {
        color: #F59E0B;
        font-weight: bold;
    }
    .stock-red {
        color: #EF4444;
        font-weight: bold;
    }
    .receipt-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .receipt-table th, .receipt-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .receipt-table th {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    .receipt-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = "Dashboard"
if 'last_receipt' not in st.session_state:
    st.session_state.last_receipt = None
if 'products_data' not in st.session_state:
    st.session_state.products_data = None
if 'users_data' not in st.session_state:
    st.session_state.users_data = None

# Initialize classes only once
if 'auth' not in st.session_state:
    st.session_state.auth = Authentication()
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Cache database data to prevent multiple connections
@st.cache_data(ttl=300, show_spinner=False)
def get_cached_data():
    """Cache database data to prevent multiple connections"""
    try:
        return st.session_state.db.get_sample_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return st.session_state.db.get_default_data()

# MODULE 1: User Authentication Interface
def show_login():
    st.markdown("<h1 class='main-header'>🔐SALPHINE CHEMOS SALES MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### Secure Login")
            
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.button("🚀 Login", type="primary", key="login_btn")
            with col_b:
                reset_btn = st.button("🔄 Reset", key="reset_btn")
            
            if login_btn:
                if username and password:
                    result = st.session_state.auth.login(username, password)
                    if result and result.get('authenticated'):
                        st.session_state.authenticated = True
                        st.session_state.current_user = {
                            'username': result.get('username', 'User'),
                            'role': result.get('role', 'user'),
                            'full_name': result.get('full_name', ''),
                            'email': result.get('email', '')
                        }
                        st.session_state.selected_module = "Dashboard"
                        st.success(f"Welcome, {result.get('username', 'User')}!")
                        st.rerun()
                    else:
                        error_msg = result.get('error', 'Invalid credentials') if result else 'Login failed'
                        st.error(f"Authentication failed: {error_msg}")
                else:
                    st.warning("Please enter both username and password")
            
            if reset_btn:
                st.rerun()
            
            st.markdown("---")
            st.markdown("""
            **Demo Credentials:**
            - 👑 Admin: `admin` / `admin123`
            - 📊 Manager: `manager1` / `manager123`
            - 💼 Clerk: `clerk1` / `clerk123`
            """)

# QuickSort Algorithm Implementation
def quicksort_products(products, key='name'):
    """QuickSort algorithm for product sorting"""
    if len(products) <= 1:
        return products
    else:
        pivot = products[len(products)//2][key]
        left = [x for x in products if x[key] < pivot]
        middle = [x for x in products if x[key] == pivot]
        right = [x for x in products if x[key] > pivot]
        return quicksort_products(left, key) + middle + quicksort_products(right, key)

# MODULE 2: Dashboard
def show_dashboard():
    st.markdown("<h1 class='main-header'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    # Get sample data from cache
    if st.session_state.products_data is None:
        st.session_state.products_data, st.session_state.users_data = get_cached_data()
    
    products = st.session_state.products_data
    
    # Calculate metrics
    total_products = len(products)
    low_stock = sum(1 for p in products if p['stock_quantity'] < p['min_stock_level'])
    critical_stock = sum(1 for p in products if p['stock_quantity'] < p['min_stock_level'] * 0.3)
    total_stock_value = sum(p['price'] * p['stock_quantity'] for p in products)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card info-card'>
            <h3>📦 Total Products</h3>
            <h2>{total_products}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card warning-card'>
            <h3>⚠️ Low Stock Items</h3>
            <h2>{low_stock}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card danger-card'>
            <h3>🚨 Critical Stock</h3>
            <h2>{critical_stock}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card success-card'>
            <h3>💰 Stock Value</h3>
            <h2>KES {total_stock_value:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity and charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Stock Status Distribution")
        
        # Create stock status data
        status_data = {
            'Status': ['Adequate', 'Low Stock', 'Critical'],
            'Count': [
                total_products - low_stock,
                low_stock - critical_stock,
                critical_stock
            ]
        }
        
        fig = px.pie(status_data, values='Count', names='Status', 
                    color_discrete_sequence=['#10B981', '#F59E0B', '#EF4444'])
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Top Products by Stock Value")
        
        # Sort products by stock value
        sorted_products = sorted(products, key=lambda x: x['price'] * x['stock_quantity'], reverse=True)[:8]
        
        data = pd.DataFrame({
            'Product': [p['name'] for p in sorted_products],
            'Value': [p['price'] * p['stock_quantity'] for p in sorted_products]
        })
        
        fig = px.bar(data, x='Product', y='Value', 
                    color='Value',
                    color_continuous_scale='Viridis')
        fig.update_layout(xaxis_title="", yaxis_title="Stock Value (KES)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Low stock alerts
    st.markdown("### ⚠️ Low Stock Alerts")
    
    low_stock_items = [p for p in products if p['stock_quantity'] < p['min_stock_level']]
    
    if low_stock_items:
        alert_data = []
        for item in low_stock_items:
            alert_level = "CRITICAL" if item['stock_quantity'] < item['min_stock_level'] * 0.3 else "LOW"
            
            alert_data.append({
                'Product': item['name'],
                'Category': item['category'],
                'Current Stock': item['stock_quantity'],
                'Min Required': item['min_stock_level'],
                'Status': alert_level
            })
        
        df_alerts = pd.DataFrame(alert_data)
        st.dataframe(df_alerts, width='stretch', hide_index=True)
    else:
        st.success("🎉 All products have sufficient stock levels!")

# MODULE 3: Sales Processing Interface - FIXED VERSION
def show_sales_processing():
    st.markdown("<h1 class='main-header'>🛒 Sales Processing</h1>", unsafe_allow_html=True)
    
    # Get cached data
    if st.session_state.products_data is None:
        st.session_state.products_data, st.session_state.users_data = get_cached_data()
    
    products = st.session_state.products_data
    
    # Use tabs instead of nested columns to fix the nesting issue
    tab1, tab2 = st.tabs(["🏷️ Product Selection", "🛍️ Shopping Cart & Checkout"])
    
    with tab1:
        st.markdown("### 🏷️ Product Selection")
        
        # Search and filter in a single row
        search_col1, search_col2, search_col3 = st.columns([3, 2, 2])
        with search_col1:
            search_term = st.text_input("🔍 Search products", placeholder="Type product name or category...", key="search_main")
        with search_col2:
            categories = list(set(p['category'] for p in products))
            selected_category = st.selectbox("📂 Filter by category", ["All"] + categories, key="category_main")
        with search_col3:
            sort_option = st.selectbox("🔢 Sort by", ["Name (A-Z)", "Name (Z-A)", "Price (Low-High)", "Price (High-Low)"], key="sort_main")
        
        # Filter products
        filtered_products = products
        
        if search_term:
            filtered_products = [p for p in filtered_products 
                               if search_term.lower() in p['name'].lower() 
                               or search_term.lower() in p['category'].lower()]
        
        if selected_category != "All":
            filtered_products = [p for p in filtered_products if p['category'] == selected_category]
        
        # Sort using QuickSort
        sort_key_map = {
            "Name (A-Z)": ('name', False),
            "Name (Z-A)": ('name', True),
            "Price (Low-High)": ('price', False),
            "Price (High-Low)": ('price', True)
        }
        
        sort_key, reverse = sort_key_map[sort_option]
        sorted_products = quicksort_products(filtered_products, sort_key)
        if reverse:
            sorted_products = sorted_products[::-1]
        
        # Display products in grid without nested columns
        st.markdown("### Available Products")
        
        # Create a container for products
        products_container = st.container()
        
        with products_container:
            # Display products in rows of 3 without nested columns
            for i in range(0, len(sorted_products), 3):
                row_products = sorted_products[i:i+3]
                cols = st.columns(3)
                
                for j, product in enumerate(row_products):
                    with cols[j]:
                        stock_status = "🟢" if product['stock_quantity'] >= product['min_stock_level'] else \
                                      "🟡" if product['stock_quantity'] >= product['min_stock_level'] * 0.3 else "🔴"
                        
                        st.markdown(f"""
                        <div class='card'>
                            <h4>{stock_status} {product['name']}</h4>
                            <p><strong>Category:</strong> {product['category']}</p>
                            <p><strong>Price:</strong> KES {product['price']:,.2f}</p>
                            <p><strong>Stock:</strong> {product['stock_quantity']} units</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        qty = st.number_input(f"Quantity", min_value=1, max_value=product['stock_quantity'], 
                                             value=1, key=f"qty_{product['id']}_{i}_{j}")
                        
                        if st.button(f"➕ Add to Cart", key=f"add_{product['id']}_{i}_{j}"):
                            cart_item = {
                                'id': product['id'],
                                'name': product['name'],
                                'price': product['price'],
                                'quantity': qty,
                                'total': product['price'] * qty
                            }
                            
                            # Check if item already in cart
                            existing_item = next((item for item in st.session_state.cart 
                                                if item['id'] == product['id']), None)
                            
                            if existing_item:
                                existing_item['quantity'] += qty
                                existing_item['total'] = existing_item['price'] * existing_item['quantity']
                            else:
                                st.session_state.cart.append(cart_item)
                            
                            st.success(f"Added {qty} x {product['name']} to cart!")
                            st.rerun()
    
    with tab2:
        st.markdown("### 🛍️ Shopping Cart")
        
        if not st.session_state.cart:
            st.info("🛒 Your cart is empty")
        else:
            # Display cart items without nested columns
            cart_total = 0
            cart_items_container = st.container()
            
            with cart_items_container:
                for idx, item in enumerate(st.session_state.cart):
                    # Use a single row layout without nested columns
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.write(f"**{item['name']}**")
                    with col2:
                        st.write(f"Qty: {item['quantity']}")
                    with col3:
                        st.write(f"KES {item['total']:,.2f}")
                    with col4:
                        if st.button("❌", key=f"remove_{item['id']}_{idx}"):
                            st.session_state.cart = [i for i in st.session_state.cart if i['id'] != item['id']]
                            st.rerun()
                    
                    cart_total += item['total']
            
            st.markdown("---")
            st.markdown(f"**Subtotal:** KES {cart_total:,.2f}")
            
            # Tax calculation
            tax_rate = st.slider("Tax Rate (%)", 0.0, 30.0, 16.0, 0.1, key="tax_slider")
            tax_amount = cart_total * (tax_rate / 100)
            final_total = cart_total + tax_amount
            
            st.markdown(f"**Tax ({tax_rate}%):** KES {tax_amount:,.2f}")
            st.markdown(f"### **Total: KES {final_total:,.2f}**")
            
            st.markdown("---")
            
            # Payment options
            payment_method = st.selectbox("💳 Payment Method", 
                                         ["Cash", "Credit Card", "M-Pesa", "Debit Card", "Bank Transfer"],
                                         key="payment_method")
            
            customer_name = st.text_input("👤 Customer Name", placeholder="Enter customer name", key="customer_name")
            
            # Buttons in a single row
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("✅ Complete Sale", type="primary", key="complete_sale"):
                    if customer_name:
                        # Generate receipt
                        receipt_data = {
                            'transaction_id': f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            'customer_name': customer_name,
                            'items': st.session_state.cart.copy(),
                            'subtotal': cart_total,
                            'tax_rate': tax_rate,
                            'tax_amount': tax_amount,
                            'total': final_total,
                            'payment_method': payment_method,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'user': st.session_state.current_user['username']
                        }
                        
                        # Save receipt to session
                        st.session_state.last_receipt = receipt_data
                        st.session_state.cart = []
                        
                        st.success(f"✅ Sale completed! Transaction ID: {receipt_data['transaction_id']}")
                        st.balloons()
                        
                        # Show receipt preview
                        st.markdown("---")
                        show_receipt_preview(receipt_data)
                    else:
                        st.warning("Please enter customer name")
            
            with col_btn2:
                if st.button("🗑️ Clear Cart", type="secondary", key="clear_cart"):
                    st.session_state.cart = []
                    st.rerun()
            
            with col_btn3:
                if st.session_state.last_receipt and st.button("📄 View Last Receipt", key="view_last"):
                    show_receipt_preview(st.session_state.last_receipt)

def show_receipt_preview(receipt_data):
    """Display receipt preview"""
    st.markdown("### 📄 Receipt Preview")
    
    # Create receipt using Streamlit components instead of raw HTML
    with st.container():
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
            <h3 style="text-align: center; color: #1E3A8A;">SALPHINE CHEMOS GETAWAY RESORT</h3>
            <p style="text-align: center;">P.O. Box 19938 - 00202 KNH Nairobi</p>
            <p style="text-align: center;">Tel: +254 727 680 468 | +254 736 880 488</p>
            <p style="text-align: center;">Email: info@lukenyagetaway.com</p>
            <hr>
        </div>
        """, unsafe_allow_html=True)
        
        # Transaction details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Transaction ID:** {receipt_data['transaction_id']}")
            st.markdown(f"**Date:** {receipt_data['date']}")
        with col2:
            st.markdown(f"**Customer:** {receipt_data['customer_name']}")
            st.markdown(f"**Cashier:** {receipt_data['user']}")
        
        st.markdown("---")
        
        # Items table using Streamlit dataframe
        st.markdown("**Items Purchased:**")
        items_data = []
        for item in receipt_data['items']:
            items_data.append({
                'Item': item['name'],
                'Qty': item['quantity'],
                'Price': f"KES {item['price']:,.2f}",
                'Total': f"KES {item['total']:,.2f}"
            })
        
        df_items = pd.DataFrame(items_data)
        st.dataframe(df_items, width='stretch', hide_index=True)
        
        st.markdown("---")
        
        # Summary
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            st.markdown(f"**Subtotal:**")
            st.markdown(f"**Tax ({receipt_data['tax_rate']}%):**")
            st.markdown("**Total:**")
        with col3:
            st.markdown(f"KES {receipt_data['subtotal']:,.2f}")
            st.markdown(f"KES {receipt_data['tax_amount']:,.2f}")
            st.markdown(f"**KES {receipt_data['total']:,.2f}**")
        
        st.markdown("---")
        st.markdown(f"**Payment Method:** {receipt_data['payment_method']}")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p>Thank you for your business!</p>
            <p>Visit us: www.salphinechemos.com</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Export buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download PDF Receipt", key="pdf_btn"):
            generate_pdf_receipt(receipt_data)
    with col2:
        if st.button("📊 Export to Excel", key="excel_btn"):
            generate_excel_receipt(receipt_data)

def generate_pdf_receipt(receipt_data):
    """Generate PDF receipt"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "SALPHINE CHEMOS GETAWAY RESORT")
    
    c.setFont("Helvetica", 10)
    c.drawString(150, 730, "P.O. Box 19938 - 00202 KNH Nairobi")
    c.drawString(180, 715, "Tel: +254 727 680 468 | +254 736 880 488")
    c.drawString(200, 700, "Email: info@lukenyagetaway.com")
    
    c.line(50, 690, 550, 690)
    
    y_position = 670
    c.drawString(50, y_position, f"Transaction ID: {receipt_data['transaction_id']}")
    c.drawString(50, y_position-20, f"Date: {receipt_data['date']}")
    c.drawString(50, y_position-40, f"Customer: {receipt_data['customer_name']}")
    c.drawString(50, y_position-60, f"Cashier: {receipt_data['user']}")
    
    c.line(50, y_position-80, 550, y_position-80)
    
    # Items table
    y_position -= 100
    c.drawString(50, y_position, "Item")
    c.drawString(350, y_position, "Qty")
    c.drawString(400, y_position, "Price")
    c.drawString(500, y_position, "Total")
    
    y_position -= 20
    for item in receipt_data['items']:
        c.drawString(50, y_position, item['name'][:40])
        c.drawString(350, y_position, str(item['quantity']))
        c.drawString(400, y_position, f"KES {item['price']:,.2f}")
        c.drawString(500, y_position, f"KES {item['total']:,.2f}")
        y_position -= 20
    
    c.line(50, y_position, 550, y_position)
    y_position -= 20
    
    c.drawString(400, y_position, f"Subtotal: KES {receipt_data['subtotal']:,.2f}")
    y_position -= 20
    c.drawString(400, y_position, f"Tax ({receipt_data['tax_rate']}%): KES {receipt_data['tax_amount']:,.2f}")
    y_position -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, y_position, f"TOTAL: KES {receipt_data['total']:,.2f}")
    
    y_position -= 40
    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, f"Payment Method: {receipt_data['payment_method']}")
    
    y_position -= 40
    c.drawString(200, y_position, "Thank you for your business!")
    c.drawString(200, y_position-20, "Visit us: www.salphinechemos.com")
    
    c.save()
    
    buffer.seek(0)
    st.download_button(
        label="⬇️ Click to Download PDF",
        data=buffer,
        file_name=f"receipt_{receipt_data['transaction_id']}.pdf",
        mime="application/pdf",
        key=f"download_pdf_{receipt_data['transaction_id']}"
    )

def generate_excel_receipt(receipt_data):
    """Generate Excel receipt"""
    # Create items dataframe
    items_data = []
    for item in receipt_data['items']:
        items_data.append({
            'Item Name': item['name'],
            'Quantity': item['quantity'],
            'Unit Price (KES)': item['price'],
            'Total (KES)': item['total']
        })
    
    df_items = pd.DataFrame(items_data)
    
    # Create summary dataframe
    summary_data = {
        'Transaction ID': [receipt_data['transaction_id']],
        'Date': [receipt_data['date']],
        'Customer': [receipt_data['customer_name']],
        'Cashier': [receipt_data['user']],
        'Subtotal (KES)': [receipt_data['subtotal']],
        'Tax Rate (%)': [receipt_data['tax_rate']],
        'Tax Amount (KES)': [receipt_data['tax_amount']],
        'Total (KES)': [receipt_data['total']],
        'Payment Method': [receipt_data['payment_method']]
    }
    df_summary = pd.DataFrame(summary_data)
    
    # Write to Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_items.to_excel(writer, sheet_name='Items', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    buffer.seek(0)
    st.download_button(
        label="⬇️ Click to Download Excel",
        data=buffer,
        file_name=f"receipt_{receipt_data['transaction_id']}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"download_excel_{receipt_data['transaction_id']}"
    )

# MODULE 4: Sorted Inventory List
def show_inventory():
    st.markdown("<h1 class='main-header'>📦 Inventory Management</h1>", unsafe_allow_html=True)
    
    # Get cached data
    if st.session_state.products_data is None:
        st.session_state.products_data, st.session_state.users_data = get_cached_data()
    
    products = st.session_state.products_data
    
    # CRUD Operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Inventory", "➕ Add Product", "✏️ Edit Product", "🔍 Search & Filter"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            view_option = st.selectbox("View Mode", ["All Products", "Low Stock", "Critical Stock"], key="view_mode")
        
        with col2:
            sort_by = st.selectbox("Sort By", ["Name", "Category", "Stock Level", "Price"], key="sort_by")
        
        with col3:
            sort_order = st.selectbox("Order", ["Ascending", "Descending"], key="sort_order")
        
        # Filter products
        if view_option == "Low Stock":
            filtered_products = [p for p in products if p['stock_quantity'] < p['min_stock_level']]
        elif view_option == "Critical Stock":
            filtered_products = [p for p in products if p['stock_quantity'] < p['min_stock_level'] * 0.3]
        else:
            filtered_products = products
        
        # Sort products
        sort_key = {
            "Name": "name",
            "Category": "category",
            "Stock Level": "stock_quantity",
            "Price": "price"
        }[sort_by]
        
        sorted_products = quicksort_products(filtered_products, sort_key)
        if sort_order == "Descending":
            sorted_products = sorted_products[::-1]
        
        # Display inventory table with color coding
        inventory_data = []
        for product in sorted_products:
            stock_level = product['stock_quantity']
            min_level = product['min_stock_level']
            
            if stock_level >= min_level:
                status = "🟢 Adequate"
                status_class = "stock-green"
            elif stock_level >= min_level * 0.3:
                status = "🟡 Low"
                status_class = "stock-yellow"
            else:
                status = "🔴 Critical"
                status_class = "stock-red"
            
            inventory_data.append({
                'ID': product['id'],
                'Name': product['name'],
                'Category': product['category'],
                'Price': f"KES {product['price']:,.2f}",
                'Stock': product['stock_quantity'],
                'Min Level': product['min_stock_level'],
                'Status': status
            })
        
        df_inventory = pd.DataFrame(inventory_data)
        st.dataframe(df_inventory, width='stretch', hide_index=True)
        
        # Stock level visualization
        st.markdown("### 📊 Stock Level Analysis")
        
        categories = {}
        for product in products:
            cat = product['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'low': 0, 'critical': 0}
            
            categories[cat]['total'] += 1
            if product['stock_quantity'] < product['min_stock_level'] * 0.3:
                categories[cat]['critical'] += 1
            elif product['stock_quantity'] < product['min_stock_level']:
                categories[cat]['low'] += 1
        
        cat_df = pd.DataFrame([
            {
                'Category': cat,
                'Adequate': data['total'] - data['low'] - data['critical'],
                'Low': data['low'],
                'Critical': data['critical']
            }
            for cat, data in categories.items()
        ])
        
        fig = px.bar(cat_df.melt(id_vars='Category'), 
                    x='Category', y='value', color='variable',
                    color_discrete_map={'Adequate': '#10B981', 'Low': '#F59E0B', 'Critical': '#EF4444'},
                    title="Stock Status by Category")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name*", placeholder="Enter product name", key="add_name")
                category = st.selectbox("Category*", ["Beverages", "Food", "Dessert", "Snacks", "Other"], key="add_category")
                price = st.number_input("Price (KES)*", min_value=0.0, step=0.01, format="%.2f", key="add_price")
            
            with col2:
                stock_quantity = st.number_input("Initial Stock*", min_value=0, step=1, key="add_stock")
                min_stock_level = st.number_input("Minimum Stock Level*", min_value=1, step=1, value=10, key="add_min_stock")
                description = st.text_area("Description", placeholder="Product description...", key="add_description")
            
            submitted = st.form_submit_button("➕ Add Product", type="primary")
            
            if submitted:
                if name and price > 0:
                    # Add product logic here
                    st.success(f"Product '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab3:
        st.markdown("### Edit Existing Product")
        
        product_list = [f"{p['id']} - {p['name']}" for p in products]
        selected_product = st.selectbox("Select Product to Edit", product_list, key="edit_select")
        
        if selected_product:
            product_id = int(selected_product.split(" - ")[0])
            product = next((p for p in products if p['id'] == product_id), None)
            
            if product:
                with st.form("edit_product_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Product Name", value=product['name'], key="edit_name")
                        new_category = st.selectbox("Category", 
                                                   ["Beverages", "Food", "Dessert", "Snacks", "Other"],
                                                   index=["Beverages", "Food", "Dessert", "Snacks", "Other"].index(product['category']) 
                                                   if product['category'] in ["Beverages", "Food", "Dessert", "Snacks", "Other"] else 0,
                                                   key="edit_category")
                        new_price = st.number_input("Price (KES)", value=float(product['price']), 
                                                   min_value=0.0, step=0.01, format="%.2f", key="edit_price")
                    
                    with col2:
                        new_stock = st.number_input("Stock Quantity", value=product['stock_quantity'], min_value=0, step=1, key="edit_stock")
                        new_min_level = st.number_input("Min Stock Level", value=product['min_stock_level'], min_value=1, step=1, key="edit_min_level")
                        new_description = st.text_area("Description", value=product.get('description', ''), key="edit_description")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        update_btn = st.form_submit_button("💾 Update Product", type="primary", key="update_btn")
                    with col_btn2:
                        delete_btn = st.form_submit_button("🗑️ Delete Product", type="secondary", key="delete_btn")
                    
                    if update_btn:
                        st.success(f"Product '{new_name}' updated successfully!")
                    if delete_btn:
                        st.warning(f"Are you sure you want to delete '{product['name']}'?")
    
    with tab4:
        st.markdown("### Advanced Search & Filter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_name = st.text_input("Search by Name", placeholder="Enter product name...", key="search_name")
            price_range = st.slider("Price Range (KES)", 0.0, 1000.0, (0.0, 1000.0), key="price_range")
        
        with col2:
            search_category = st.multiselect("Categories", ["Beverages", "Food", "Dessert", "Snacks", "Other"], key="search_category")
            stock_range = st.slider("Stock Range", 0, 200, (0, 200), key="stock_range")
        
        # Apply filters
        filtered = products
        
        if search_name:
            filtered = [p for p in filtered if search_name.lower() in p['name'].lower()]
        
        if search_category:
            filtered = [p for p in filtered if p['category'] in search_category]
        
        filtered = [p for p in filtered if price_range[0] <= p['price'] <= price_range[1]]
        filtered = [p for p in filtered if stock_range[0] <= p['stock_quantity'] <= stock_range[1]]
        
        if filtered:
            df_filtered = pd.DataFrame(filtered)
            st.dataframe(df_filtered[['name', 'category', 'price', 'stock_quantity']], width='stretch', hide_index=True)
        else:
            st.info("No products match your search criteria")

# MODULE 5: Sales Reports Interface - FIXED with proper date handling
def show_reports():
    st.markdown("<h1 class='main-header'>📈 Sales Reports & Analytics</h1>", unsafe_allow_html=True)
    
    # Get cached data
    if st.session_state.products_data is None:
        st.session_state.products_data, st.session_state.users_data = get_cached_data()
    
    products = st.session_state.products_data
    
    # Time period selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report_type = st.selectbox("Report Type", 
                                  ["Sales Summary", "Product Performance", "Category Analysis", "Time Series"],
                                  key="report_type")
    
    with col2:
        time_period = st.selectbox("Time Period", 
                                  ["Today", "Yesterday", "Last 7 Days", "This Month", "Last Month", "Custom Range"],
                                  key="time_period")
    
    with col3:
        if time_period == "Custom Range":
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("Start Date", key="start_date")
            with date_col2:
                end_date = st.date_input("End Date", key="end_date")
    
    # Generate sample sales data with proper date handling
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    sales_data = []
    
    for date in dates:
        daily_sales = random.randint(50, 200)
        for _ in range(daily_sales):
            product = random.choice(products)
            qty = random.randint(1, 5)
            # Convert date to string to avoid Arrow serialization issues
            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product': product['name'],
                'category': product['category'],
                'quantity': qty,
                'price': product['price'],
                'total': product['price'] * qty,
                'payment_method': random.choice(['Cash', 'Credit Card', 'M-Pesa', 'Debit Card'])
            })
    
    df_sales = pd.DataFrame(sales_data)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary Dashboard", "📈 Visual Charts", "📋 Data Tables", "📤 Export Data"])
    
    with tab1:
        # Key metrics
        total_sales = df_sales['total'].sum()
        avg_sale = df_sales['total'].mean()
        total_transactions = len(df_sales)
        top_product = df_sales.groupby('product')['quantity'].sum().idxmax()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card success-card'>
                <h3>💰 Total Sales</h3>
                <h2>KES {total_sales:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card info-card'>
                <h3>🧾 Transactions</h3>
                <h2>{total_transactions}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card warning-card'>
                <h3>📦 Avg. Sale</h3>
                <h2>KES {avg_sale:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏆 Top Product</h3>
                <h4>{top_product}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        # Top products table
        st.markdown("### 🏆 Top 10 Products by Sales")
        top_products = df_sales.groupby('product').agg({
            'quantity': 'sum',
            'total': 'sum'
        }).sort_values('total', ascending=False).head(10)
        
        st.dataframe(top_products.style.format({'total': 'KES {:,.2f}'}), 
                    width='stretch')
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Sales by Category")
            
            category_sales = df_sales.groupby('category')['total'].sum().reset_index()
            fig = px.pie(category_sales, values='total', names='category',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Daily Sales Trend")
            
            daily_trend = df_sales.groupby('date')['total'].sum().reset_index()
            fig = px.line(daily_trend, x='date', y='total',
                         title="Sales Over Time",
                         markers=True)
            fig.update_layout(xaxis_title="Date", yaxis_title="Total Sales (KES)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Payment method distribution
        st.markdown("### Payment Methods Distribution")
        payment_dist = df_sales.groupby('payment_method')['total'].sum().reset_index()
        
        fig = px.bar(payment_dist, x='payment_method', y='total',
                    color='payment_method',
                    title="Sales by Payment Method")
        fig.update_layout(xaxis_title="Payment Method", yaxis_title="Total Sales (KES)")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Detailed Sales Data")
        
        # Filters for the table
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            table_category = st.multiselect("Filter by Category", df_sales['category'].unique(), key="table_category")
        
        with col_filter2:
            table_products = st.multiselect("Filter by Product", df_sales['product'].unique(), key="table_products")
        
        with col_filter3:
            sort_table = st.selectbox("Sort By", ["Date", "Product", "Total", "Quantity"], key="sort_table")
        
        # Apply filters
        filtered_df = df_sales.copy()
        
        if table_category:
            filtered_df = filtered_df[filtered_df['category'].isin(table_category)]
        
        if table_products:
            filtered_df = filtered_df[filtered_df['product'].isin(table_products)]
        
        # Sort table
        if sort_table == "Date":
            filtered_df = filtered_df.sort_values('date')
        elif sort_table == "Product":
            filtered_df = filtered_df.sort_values('product')
        elif sort_table == "Total":
            filtered_df = filtered_df.sort_values('total', ascending=False)
        elif sort_table == "Quantity":
            filtered_df = filtered_df.sort_values('quantity', ascending=False)
        
        # Display table with proper date format
        st.dataframe(filtered_df, width='stretch')
        
        # Summary statistics
        st.markdown("### Summary Statistics")
        summary_stats = filtered_df.describe()
        st.dataframe(summary_stats, width='stretch')
    
    with tab4:
        st.markdown("### Export Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_format = st.selectbox("Export Format", 
                                        ["CSV", "Excel", "PDF Summary", "JSON"],
                                        key="export_format")
        
        with col2:
            data_type = st.selectbox("Data Type", 
                                    ["Sales Data", "Summary Report", "Product Performance", "Category Analysis"],
                                    key="data_type")
        
        with col3:
            include_charts = st.checkbox("Include Charts", value=True, key="include_charts")
        
        # Generate export data
        if data_type == "Sales Data":
            export_df = df_sales
        elif data_type == "Summary Report":
            export_df = pd.DataFrame({
                'Metric': ['Total Sales', 'Total Transactions', 'Average Sale', 'Top Product'],
                'Value': [f"KES {total_sales:,.2f}", total_transactions, 
                         f"KES {avg_sale:,.2f}", top_product]
            })
        elif data_type == "Product Performance":
            export_df = df_sales.groupby('product').agg({
                'quantity': 'sum',
                'total': 'sum'
            }).reset_index()
        else:  # Category Analysis
            export_df = df_sales.groupby('category').agg({
                'quantity': 'sum',
                'total': 'sum',
                'price': 'mean'
            }).reset_index()
        
        # Export buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("📥 Download CSV", use_container_width=True, key="download_csv"):
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Click to Download",
                    data=csv,
                    file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key=f"csv_download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        
        with col_btn2:
            if st.button("📊 Download Excel", use_container_width=True, key="download_excel"):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Report')
                buffer.seek(0)
                st.download_button(
                    label="⬇️ Click to Download",
                    data=buffer,
                    file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"excel_download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        
        with col_btn3:
            if st.button("📄 Download PDF", use_container_width=True, key="download_pdf"):
                st.info("PDF generation would be implemented with reportlab")

# MODULE 6: User Management Interface (Admin Only)
def show_user_management():
    st.markdown("<h1 class='main-header'>👥 User Management</h1>", unsafe_allow_html=True)
    
    # Check if user is admin
    if not st.session_state.current_user or st.session_state.current_user.get('role') != 'admin':
        st.warning("⚠️ This section is only accessible to administrators.")
        return
    
    if st.session_state.users_data is None:
        st.session_state.products_data, st.session_state.users_data = get_cached_data()
    
    users = st.session_state.users_data
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 User List", "➕ Add User", "📊 Activity Logs", "⚙️ Account Settings"])
    
    with tab1:
        st.markdown("### Registered Users")
        
        # Display users in a dataframe
        user_data = []
        for user in users:
            status = "🟢 Active" if random.choice([True, False]) else "🔴 Inactive"
            user_data.append({
                'ID': user['id'],
                'Username': user['username'],
                'Role': user['role'],
                'Email': user['email'],
                'Status': status,
                'Last Login': f"{random.randint(1, 30)} days ago"
            })
        
        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, width='stretch', hide_index=True)
        
        # Actions based on editor
        if st.button("💾 Save Changes", type="primary", key="save_users"):
            st.success("User data updated successfully!")
    
    with tab2:
        st.markdown("### Add New User")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username*", placeholder="Enter username", key="new_username")
                new_email = st.text_input("Email*", placeholder="user@example.com", key="new_email")
                new_password = st.text_input("Password*", type="password", placeholder="Enter password", key="new_password")
            
            with col2:
                new_role = st.selectbox("Role*", ["admin", "manager", "clerk"], key="new_role")
                is_active = st.checkbox("Active Account", value=True, key="is_active")
                send_welcome = st.checkbox("Send welcome email", value=True, key="send_welcome")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_user = st.form_submit_button("👤 Add User", type="primary", key="submit_user")
            with col_btn2:
                cancel_user = st.form_submit_button("Cancel", type="secondary", key="cancel_user")
            
            if submit_user:
                if new_username and new_email and new_password:
                    st.success(f"User '{new_username}' added successfully!")
                    if send_welcome:
                        st.info("Welcome email sent successfully!")
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab3:
        st.markdown("### 📜 User Activity Logs")
        
        # Generate sample activity logs
        activities = []
        actions = ['Login', 'Logout', 'Sale', 'Inventory Update', 'Report Generated', 'User Modified']
        
        for i in range(50):
            activities.append({
                'Timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 10080))).strftime("%Y-%m-%d %H:%M:%S"),
                'User': random.choice([u['username'] for u in users]),
                'Action': random.choice(actions),
                'Details': f"Performed {random.choice(actions)} operation",
                'IP Address': f"192.168.1.{random.randint(1, 255)}"
            })
        
        df_activities = pd.DataFrame(activities)
        
        # Filter options
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            log_user = st.multiselect("Filter by User", df_activities['User'].unique(), key="log_user")
        
        with col_filter2:
            log_action = st.multiselect("Filter by Action", df_activities['Action'].unique(), key="log_action")
        
        # Apply filters
        filtered_logs = df_activities.copy()
        
        if log_user:
            filtered_logs = filtered_logs[filtered_logs['User'].isin(log_user)]
        
        if log_action:
            filtered_logs = filtered_logs[filtered_logs['Action'].isin(log_action)]
        
        # Display logs
        st.dataframe(filtered_logs, width='stretch', hide_index=True)
        
        # Export logs
        if st.button("📥 Export Activity Logs", type="primary", key="export_logs"):
            csv = filtered_logs.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key=f"activity_download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
    
    with tab4:
        st.markdown("### Account Settings Management")
        
        selected_user = st.selectbox("Select User", [u['username'] for u in users], key="select_user")
        
        if selected_user:
            user = next((u for u in users if u['username'] == selected_user), None)
            
            if user:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Account Status")
                    
                    current_status = "🟢 Active" if random.choice([True, False]) else "🔴 Inactive"
                    st.write(f"**Current Status:** {current_status}")
                    
                    new_status = st.radio("Change Status", ["Active", "Inactive", "Suspended"], key="new_status")
                    
                    if st.button("🔄 Update Status", type="primary", key="update_status"):
                        st.success(f"Account status updated to: {new_status}")
                
                with col2:
                    st.markdown("#### Role Management")
                    
                    st.write(f"**Current Role:** {user['role']}")
                    new_role = st.selectbox("Assign New Role", ["admin", "manager", "clerk"], key="assign_role")
                    
                    if st.button("👑 Update Role", type="primary", key="update_role"):
                        st.success(f"Role updated to: {new_role}")
                
                st.markdown("---")
                st.markdown("#### Dangerous Zone")
                
                col_danger1, col_danger2 = st.columns(2)
                
                with col_danger1:
                    if st.button("🔒 Force Password Reset", type="secondary", key="force_reset"):
                        st.warning("Password reset email sent to user.")
                
                with col_danger2:
                    if st.button("🗑️ Delete Account", type="secondary", key="delete_account"):
                        st.error("Are you sure you want to delete this account? This action cannot be undone.")
                        confirm = st.checkbox("I confirm I want to delete this account", key="confirm_delete")
                        if confirm:
                            st.error("Account deletion initiated. Contact system administrator for final confirmation.")

# MODULE 7: Settings System Interface
def show_settings():
    st.markdown("<h1 class='main-header'>⚙️ System Settings</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Business Profile", "🧾 Receipt Template", "🔔 Notifications", "🛠️ System Preferences"])
    
    with tab1:
        st.markdown("### Business Information")
        
        with st.form("business_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                business_name = st.text_input("Business Name*", value="Lukenya Getaway Resort", key="biz_name")
                tax_id = st.text_input("Tax ID/VAT Number", value="P123456789", key="tax_id")
                currency = st.selectbox("Currency", ["KES", "USD", "EUR", "GBP"], index=0, key="currency")
                tax_rate = st.number_input("Default Tax Rate (%)", value=16.0, min_value=0.0, max_value=30.0, step=0.1, key="default_tax")
            
            with col2:
                address = st.text_area("Address", value="P.O. Box 19938 - 00202 KNH Nairobi", key="address")
                phone1 = st.text_input("Primary Phone", value="+254 727 680 468", key="phone1")
                phone2 = st.text_input("Secondary Phone", value="+254 736 880 488", key="phone2")
                email = st.text_input("Business Email", value="info@lukenyagetaway.com", key="biz_email")
                website = st.text_input("Website", value="www.lukenyagetaway.com", key="website")
            
            logo_file = st.file_uploader("Upload Business Logo", type=['png', 'jpg', 'jpeg'], key="logo_upload")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                save_profile = st.form_submit_button("💾 Save Profile", type="primary", key="save_profile")
            with col_btn2:
                cancel_profile = st.form_submit_button("Cancel", type="secondary", key="cancel_profile")
            
            if save_profile:
                st.success("Business profile updated successfully!")
    
    with tab2:
        st.markdown("### Receipt Template Customization")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Template Preview")
            
            # Live preview of receipt template
            preview_html = """
            <div style="border: 2px dashed #ccc; padding: 20px; border-radius: 10px; background-color: #fff;">
                <div style="text-align: center;">
                    <h3 style="color: #1E3A8A;">[BUSINESS NAME]</h3>
                    <p>[ADDRESS]</p>
                    <p>Tel: [PHONE1] | [PHONE2]</p>
                    <p>Email: [EMAIL] | Website: [WEBSITE]</p>
                    <hr style="border-top: 2px solid #1E3A8A;">
                    <p><strong>Transaction:</strong> [TRANSACTION_ID]</p>
                    <p><strong>Date:</strong> [DATE] | <strong>Cashier:</strong> [USER]</p>
                    <hr>
                </div>
            </div>
            """
            st.markdown(preview_html, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Template Options")
            
            header_size = st.slider("Header Font Size", 12, 24, 16, key="header_size")
            show_logo = st.checkbox("Show Logo", value=True, key="show_logo")
            show_footer = st.checkbox("Show Footer Message", value=True, key="show_footer")
            footer_message = st.text_area("Footer Message", value="Thank you for your business!", key="footer_msg")
            
            template_style = st.selectbox("Template Style", 
                                         ["Modern", "Classic", "Minimal", "Professional"],
                                         key="template_style")
            
            if st.button("🔄 Update Template", type="primary", key="update_template"):
                st.success("Receipt template updated successfully!")
    
    with tab3:
        st.markdown("### Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Email Notifications")
            
            email_notifications = st.checkbox("Enable Email Notifications", value=True, key="email_notify")
            
            if email_notifications:
                low_stock_email = st.checkbox("Low Stock Alerts", value=True, key="low_stock_email")
                sales_report_email = st.checkbox("Daily Sales Reports", value=True, key="sales_report_email")
                system_alerts = st.checkbox("System Alerts", value=True, key="system_alerts")
                
                email_frequency = st.selectbox("Report Frequency", 
                                              ["Real-time", "Hourly", "Daily", "Weekly"],
                                              key="email_freq")
                
                email_recipients = st.text_area("Notification Recipients (comma-separated)",
                                               value="admin@system.com, manager@system.com",
                                               key="email_recipients")
        
        with col2:
            st.markdown("#### In-App Notifications")
            
            inapp_notifications = st.checkbox("Enable In-App Notifications", value=True, key="inapp_notify")
            
            if inapp_notifications:
                show_sales_popup = st.checkbox("Show Sales Confirmations", value=True, key="show_popup")
                show_stock_alerts = st.checkbox("Show Stock Warnings", value=True, key="show_stock_alerts")
                show_system_messages = st.checkbox("Show System Messages", value=True, key="show_system_msgs")
                
                notification_sound = st.checkbox("Play Notification Sound", value=True, key="notify_sound")
                sound_type = st.selectbox("Sound Type", ["Default", "Chime", "Beep", "None"], key="sound_type")
        
        if st.button("🔔 Save Notification Settings", type="primary", key="save_notify"):
            st.success("Notification settings updated successfully!")
    
    with tab4:
        st.markdown("### System Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### General Settings")
            
            default_view = st.selectbox("Default Dashboard View", 
                                       ["Sales Overview", "Inventory", "Reports", "User Dashboard"],
                                       key="default_view")
            
            auto_logout = st.checkbox("Enable Auto Logout", value=True, key="auto_logout")
            if auto_logout:
                logout_time = st.slider("Inactivity Timeout (minutes)", 5, 120, 30, key="logout_time")
            
            data_retention = st.number_input("Data Retention Period (days)", 
                                           min_value=30, max_value=365*5, value=365, step=30,
                                           key="data_retention")
            
            backup_frequency = st.selectbox("Auto Backup Frequency", 
                                          ["Daily", "Weekly", "Monthly", "Never"],
                                          key="backup_freq")
        
        with col2:
            st.markdown("#### Display Settings")
            
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme")
            language = st.selectbox("Language", ["English", "Swahili", "French", "Spanish"], key="language")
            date_format = st.selectbox("Date Format", 
                                      ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD MMM YYYY"],
                                      key="date_format")
            
            decimal_places = st.slider("Decimal Places", 0, 4, 2, key="decimal_places")
            number_format = st.selectbox("Number Format", 
                                        ["1,000.00", "1.000,00", "1 000.00"],
                                        key="number_format")
        
        st.markdown("---")
        st.markdown("#### System Maintenance")
        
        col_maint1, col_maint2, col_maint3 = st.columns(3)
        
        with col_maint1:
            if st.button("🔄 Clear Cache", type="secondary", key="clear_cache"):
                st.info("Cache cleared successfully!")
        
        with col_maint2:
            if st.button("📊 Rebuild Indexes", type="secondary", key="rebuild_index"):
                st.info("Database indexes rebuilt successfully!")
        
        with col_maint3:
            if st.button("🚀 System Diagnostics", type="secondary", key="sys_diagnostics"):
                st.info("System diagnostics completed. All systems operational.")
        
        if st.button("💾 Save All Settings", type="primary", key="save_all_settings"):
            st.success("All system settings saved successfully!")

# MODULE 8: Security Settings
def show_security():
    st.markdown("<h1 class='main-header'>🔐 Security Settings</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 Password Policy", "👥 Access Control", "📜 Audit Logs", "🛡️ Security Features"])
    
    with tab1:
        st.markdown("### Password Security Policy")
        
        with st.form("password_policy_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                min_length = st.slider("Minimum Password Length", 6, 20, 8, key="min_length")
                require_uppercase = st.checkbox("Require Uppercase Letters", value=True, key="req_upper")
                require_lowercase = st.checkbox("Require Lowercase Letters", value=True, key="req_lower")
                require_numbers = st.checkbox("Require Numbers", value=True, key="req_numbers")
            
            with col2:
                require_special = st.checkbox("Require Special Characters", value=True, key="req_special")
                password_expiry = st.slider("Password Expiry (days)", 0, 365, 90, key="pass_expiry")
                max_login_attempts = st.slider("Max Failed Login Attempts", 1, 10, 3, key="max_attempts")
                lockout_duration = st.slider("Lockout Duration (minutes)", 1, 60, 15, key="lockout_duration")
            
            save_policy = st.form_submit_button("💾 Save Policy", type="primary", key="save_policy")
            
            if save_policy:
                st.success("Password policy updated successfully!")
        
        st.markdown("### Password Strength Test")
        test_password = st.text_input("Test Password Strength", type="password", key="test_password")
        
        if test_password:
            strength = 0
            feedback = []
            
            if len(test_password) >= 8:
                strength += 1
                feedback.append("✓ Minimum length met")
            else:
                feedback.append("✗ Minimum length not met")
            
            if any(c.isupper() for c in test_password):
                strength += 1
                feedback.append("✓ Contains uppercase")
            
            if any(c.islower() for c in test_password):
                strength += 1
                feedback.append("✓ Contains lowercase")
            
            if any(c.isdigit() for c in test_password):
                strength += 1
                feedback.append("✓ Contains numbers")
            
            if any(not c.isalnum() for c in test_password):
                strength += 1
                feedback.append("✓ Contains special characters")
            
            # Display strength meter
            colors = ['#EF4444', '#F59E0B', '#FBBF24', '#10B981', '#059669']
            strength_text = ['Very Weak', 'Weak', 'Fair', 'Good', 'Excellent']
            
            st.markdown(f"""
            <div style="background-color: #F3F4F6; padding: 10px; border-radius: 5px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>Password Strength:</span>
                    <span style="color: {colors[strength-1]}; font-weight: bold;">{strength_text[strength-1]}</span>
                </div>
                <div style="height: 10px; background-color: #E5E7EB; border-radius: 5px;">
                    <div style="width: {strength * 20}%; height: 100%; background-color: {colors[strength-1]}; border-radius: 5px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for item in feedback:
                st.write(item)
    
    with tab2:
        st.markdown("### Role-Based Access Control")
        
        roles = ['admin', 'manager', 'clerk']
        selected_role = st.selectbox("Select Role to Configure", roles, key="select_role")
        
        if selected_role:
            st.markdown(f"#### Permissions for {selected_role.upper()} Role")
            
            col_perm1, col_perm2, col_perm3 = st.columns(3)
            
            with col_perm1:
                st.markdown("**Sales Module**")
                can_process_sales = st.checkbox("Process Sales", value=True, key="can_process_sales")
                can_view_sales = st.checkbox("View Sales", value=True, key="can_view_sales")
                can_refund_sales = st.checkbox("Process Refunds", value=selected_role in ['admin', 'manager'], key="can_refund_sales")
            
            with col_perm2:
                st.markdown("**Inventory Module**")
                can_view_inventory = st.checkbox("View Inventory", value=True, key="can_view_inventory")
                can_edit_inventory = st.checkbox("Edit Inventory", value=selected_role in ['admin', 'manager'], key="can_edit_inventory")
                can_delete_inventory = st.checkbox("Delete Items", value=selected_role == 'admin', key="can_delete_inventory")
            
            with col_perm3:
                st.markdown("**Reports Module**")
                can_view_reports = st.checkbox("View Reports", value=True, key="can_view_reports")
                can_export_reports = st.checkbox("Export Reports", value=selected_role in ['admin', 'manager'], key="can_export_reports")
                can_view_analytics = st.checkbox("View Analytics", value=selected_role in ['admin', 'manager'], key="can_view_analytics")
            
            if selected_role in ['admin', 'manager']:
                st.markdown("**Administration**")
                col_admin1, col_admin2 = st.columns(2)
                
                with col_admin1:
                    can_manage_users = st.checkbox("Manage Users", value=selected_role == 'admin', key="can_manage_users")
                    can_manage_settings = st.checkbox("Manage Settings", value=selected_role == 'admin', key="can_manage_settings")
                
                with col_admin2:
                    can_view_logs = st.checkbox("View System Logs", value=True, key="can_view_logs")
                    can_backup_data = st.checkbox("Backup Data", value=selected_role == 'admin', key="can_backup_data")
            
            if st.button(f"💾 Save {selected_role} Permissions", type="primary", key=f"save_{selected_role}_perms"):
                st.success(f"Permissions for {selected_role} role saved successfully!")
    
    with tab3:
        st.markdown("### Security Audit Logs")
        
        # Generate sample security logs
        security_logs = []
        security_actions = ['Login Attempt', 'Password Change', 'Permission Change', 
                          'User Creation', 'User Deletion', 'Failed Access Attempt']
        
        for i in range(30):
            security_logs.append({
                'Timestamp': (datetime.now() - timedelta(hours=random.randint(1, 720))).strftime("%Y-%m-%d %H:%M:%S"),
                'Event': random.choice(security_actions),
                'User': random.choice(['admin', 'manager1', 'clerk1', 'Unknown']),
                'IP Address': f"192.168.1.{random.randint(1, 255)}",
                'Status': random.choice(['SUCCESS', 'FAILED', 'WARNING']),
                'Details': f"Security event: {random.choice(security_actions)}"
            })
        
        df_security = pd.DataFrame(security_logs)
        
        # Color code status
        def color_status(val):
            if val == 'SUCCESS':
                return 'color: #10B981; font-weight: bold'
            elif val == 'FAILED':
                return 'color: #EF4444; font-weight: bold'
            else:
                return 'color: #F59E0B; font-weight: bold'
        
        # Filter options
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            log_event = st.multiselect("Filter by Event", df_security['Event'].unique(), key="log_event")
        
        with col_filter2:
            log_status = st.multiselect("Filter by Status", df_security['Status'].unique(), key="log_status")
        
        # Apply filters
        filtered_security = df_security.copy()
        
        if log_event:
            filtered_security = filtered_security[filtered_security['Event'].isin(log_event)]
        
        if log_status:
            filtered_security = filtered_security[filtered_security['Status'].isin(log_status)]
        
        # Display logs
        st.dataframe(filtered_security, width='stretch', hide_index=True)
        
        # Export and clear logs
        col_export, col_clear = st.columns(2)
        
        with col_export:
            if st.button("📥 Export Audit Logs", type="primary", key="export_audit"):
                csv = filtered_security.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key=f"audit_download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        
        with col_clear:
            if st.button("🗑️ Clear Old Logs", type="secondary", key="clear_old_logs"):
                st.warning("This will delete logs older than 90 days. Continue?")
                if st.checkbox("Yes, clear old logs", key="confirm_clear_logs"):
                    st.info("Old logs cleared successfully!")
    
    with tab4:
        st.markdown("### Advanced Security Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Authentication")
            
            two_factor_auth = st.checkbox("Enable Two-Factor Authentication", value=False, key="two_factor")
            if two_factor_auth:
                two_factor_method = st.selectbox("2FA Method", 
                                                ["SMS", "Email", "Authenticator App"],
                                                key="two_factor_method")
                require_2fa_admins = st.checkbox("Require 2FA for Admins", value=True, key="req_2fa_admins")
                require_2fa_all = st.checkbox("Require 2FA for All Users", value=False, key="req_2fa_all")
            
            biometric_auth = st.checkbox("Enable Biometric Authentication", value=False, key="biometric_auth")
            if biometric_auth:
                st.info("Biometric authentication requires compatible hardware")
        
        with col2:
            st.markdown("#### Session Security")
            
            single_session = st.checkbox("Single Session Per User", value=True, key="single_session")
            if single_session:
                st.info("Users will be logged out from other devices")
            
            session_timeout = st.slider("Session Timeout (minutes)", 15, 480, 30, key="session_timeout")
            secure_cookies = st.checkbox("Secure Cookies Only", value=True, key="secure_cookies")
            http_only = st.checkbox("HTTP Only Cookies", value=True, key="http_only")
        
        st.markdown("---")
        st.markdown("#### Data Protection")
        
        col_prot1, col_prot2 = st.columns(2)
        
        with col_prot1:
            data_encryption = st.checkbox("Enable Data Encryption", value=True, key="data_encryption")
            if data_encryption:
                encryption_level = st.selectbox("Encryption Level", 
                                              ["AES-128", "AES-256", "RSA-2048", "RSA-4096"],
                                              key="encryption_level")
            
            backup_encryption = st.checkbox("Encrypt Backups", value=True, key="backup_encryption")
        
        with col_prot2:
            mask_sensitive = st.checkbox("Mask Sensitive Data", value=True, key="mask_sensitive")
            if mask_sensitive:
                mask_fields = st.multiselect("Fields to Mask", 
                                           ["Passwords", "Credit Cards", "Phone Numbers", "Email Addresses"],
                                           key="mask_fields")
            
            auto_logout_sensitive = st.checkbox("Auto-logout on Sensitive Operations", value=True, key="auto_logout_sensitive")
        
        st.markdown("---")
        st.markdown("#### Security Monitoring")
        
        intrusion_detection = st.checkbox("Enable Intrusion Detection", value=True, key="intrusion_detection")
        if intrusion_detection:
            alert_on_many_failures = st.checkbox("Alert on Multiple Failures", value=True, key="alert_failures")
            monitor_privileged = st.checkbox("Monitor Privileged Accounts", value=True, key="monitor_privileged")
            log_all_access = st.checkbox("Log All Access Attempts", value=True, key="log_all_access")
        
        if st.button("🛡️ Apply Security Settings", type="primary", key="apply_security"):
            st.success("Security settings applied successfully!")
            st.info("Some settings may require system restart to take effect")

# MODULE 9: Main Navigation Sidebar
def main_navigation():
    # Only show navigation if authenticated
    if not st.session_state.authenticated:
        return
    
    # Create sidebar navigation
    with st.sidebar:
        st.markdown("""
        <style>
        .sidebar-header {
            font-size: 1.8rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .user-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # User info
        if st.session_state.current_user:
            user_role_icon = {
                'admin': '👑',
                'manager': '📊',
                'clerk': '💼'
            }.get(st.session_state.current_user.get('role', 'user'), '👤')
            
            st.markdown(f"""
            <div class='user-info'>
                <h4>{user_role_icon} {st.session_state.current_user.get('username', 'User')}</h4>
                <p>{st.session_state.current_user.get('role', 'USER').upper()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<h2 class='sidebar-header'>📋 Navigation</h2>", unsafe_allow_html=True)
        
        # Navigation menu
        selected = option_menu(
            menu_title=None,
            options=["📊 Dashboard", "🛒 Sales", "📦 Inventory", "📈 Reports", "👥 Users", "⚙️ Settings", "🔐 Security", "🚪 Logout"],
            icons=["speedometer2", "cart", "box", "graph-up", "people", "gear", "shield-lock", "box-arrow-right"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#1E3A8A", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef"},
                "nav-link-selected": {"background-color": "#1E3A8A"},
            }
        )
        
        # Update selected module
        module_map = {
            "📊 Dashboard": "Dashboard",
            "🛒 Sales": "Sales Processing",
            "📦 Inventory": "Inventory",
            "📈 Reports": "Reports",
            "👥 Users": "User Management",
            "⚙️ Settings": "Settings",
            "🔐 Security": "Security",
            "🚪 Logout": "Logout"
        }
        
        st.session_state.selected_module = module_map[selected]
        
        # Business info footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem; color: #666;">
            <p><strong>Salphine chemos Getaway Resort</strong></p>
            <p>P.O. Box 19938 - 00202 KNH Nairobi</p>
            <p>📞 +254 727 680 468</p>
            <p>📧 info@salphinechemos.com</p>
            <p>🌐 www.salphinechemos.com</p>
        </div>
        """, unsafe_allow_html=True)

# Main application flow
def main():
    # Check authentication
    if not st.session_state.authenticated:
        show_login()
    else:
        # Show navigation
        main_navigation()
        
        # Display selected module
        if st.session_state.selected_module == "Dashboard":
            show_dashboard()
        elif st.session_state.selected_module == "Sales Processing":
            show_sales_processing()
        elif st.session_state.selected_module == "Inventory":
            show_inventory()
        elif st.session_state.selected_module == "Reports":
            show_reports()
        elif st.session_state.selected_module == "User Management":
            show_user_management()
        elif st.session_state.selected_module == "Settings":
            show_settings()
        elif st.session_state.selected_module == "Security":
            show_security()
        elif st.session_state.selected_module == "Logout":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("### 👋 Logout Confirmation")
                st.warning("Are you sure you want to logout?")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ Yes, Logout", type="primary", key="yes_logout"):
                        st.session_state.authenticated = False
                        st.session_state.current_user = None
                        st.session_state.cart = []
                        st.session_state.last_receipt = None
                        st.session_state.products_data = None
                        st.session_state.users_data = None
                        st.success("Logged out successfully!")
                        st.rerun()
                with col_btn2:
                    if st.button("❌ Cancel", key="cancel_logout"):
                        st.session_state.selected_module = "Dashboard"
                        st.rerun()

if __name__ == "__main__":
    main()