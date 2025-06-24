from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('sales_data.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product TEXT NOT NULL,
            region TEXT NOT NULL,
            sales_amount REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM sales')
    if cursor.fetchone()[0] == 0:
        # Insert sample data
        products = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Watch']
        regions = ['North', 'South', 'East', 'West', 'Central']
        
        # Generate 3 months of daily data
        start_date = datetime.now() - timedelta(days=90)
        sample_data = []
        
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            for product in products:
                for region in regions:
                    # Random sales data with some patterns
                    base_amount = random.uniform(1000, 5000)
                    seasonal_factor = 1 + 0.3 * (i / 90)  # Growing trend
                    sales_amount = base_amount * seasonal_factor
                    quantity = random.randint(10, 100)
                    
                    sample_data.append((
                        current_date.strftime('%Y-%m-%d'),
                        product,
                        region,
                        round(sales_amount, 2),
                        quantity
                    ))
        
        cursor.executemany('''
            INSERT INTO sales (date, product, region, sales_amount, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_data)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    product_filter = request.args.get('product', '')
    region_filter = request.args.get('region', '')
    
    conn = sqlite3.connect('sales_data.db')
    cursor = conn.cursor()
    
    # Build query with filters
    query = '''
        SELECT date, product, region, sales_amount, quantity
        FROM sales
        WHERE 1=1
    '''
    params = []
    
    if product_filter:
        query += ' AND product = ?'
        params.append(product_filter)
    
    if region_filter:
        query += ' AND region = ?'
        params.append(region_filter)
    
    query += ' ORDER BY date'
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    
    # Format data for JSON response
    formatted_data = []
    for row in data:
        formatted_data.append({
            'date': row[0],
            'product': row[1],
            'region': row[2],
            'sales_amount': row[3],
            'quantity': row[4]
        })
    
    return jsonify(formatted_data)

@app.route('/api/filters')
def get_filters():
    conn = sqlite3.connect('sales_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT product FROM sales ORDER BY product')
    products = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT region FROM sales ORDER BY region')
    regions = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'products': products,
        'regions': regions
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
