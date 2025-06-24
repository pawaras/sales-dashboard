from flask import Flask, render_template, jsonify, request
import sqlite3
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Database file path
DB_FILE = 'sales.db'

def create_database():
    """Create database and populate with sample data"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            date TEXT,
            product TEXT,
            region TEXT,
            amount REAL
        )
    ''')
    
    # Check if we need to populate data
    cursor.execute('SELECT COUNT(*) FROM sales')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Sample data
        products = ['Laptop', 'Phone', 'Tablet', 'Watch', 'Headphones']
        regions = ['North', 'South', 'East', 'West']
        
        # Generate 60 days of data
        base_date = datetime.now() - timedelta(days=60)
        
        for i in range(60):
            date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            for product in products:
                for region in regions:
                    amount = round(random.uniform(500, 3000), 2)
                    cursor.execute(
                        'INSERT INTO sales (date, product, region, amount) VALUES (?, ?, ?, ?)',
                        (date, product, region, amount)
                    )
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    try:
        product = request.args.get('product', '')
        region = request.args.get('region', '')
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        query = 'SELECT date, product, region, amount FROM sales WHERE 1=1'
        params = []
        
        if product:
            query += ' AND product = ?'
            params.append(product)
            
        if region:
            query += ' AND region = ?'
            params.append(region)
            
        query += ' ORDER BY date'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'date': row[0],
                'product': row[1],
                'region': row[2],
                'amount': row[3]
            })
            
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/options')
def api_options():
    try:
        conn = sqlite3.connect(DB_FILE)
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
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database when starting
create_database()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
