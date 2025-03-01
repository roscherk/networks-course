from flask import Flask, request, jsonify, send_file, Response
import os
import uuid
import base64
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)

products = {}

@app.route('/product', methods=['POST'])
def add_product():
    data = request.get_json()
    
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"error": "Name and description are required"}), 400
    
    product_id = len(products) + 1
    product = {
        "id": product_id,
        "name": data['name'],
        "description": data['description'],
        "icon": None
    }
    
    products[product_id] = product
    return jsonify(product), 201

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(products[product_id])

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    product = products[product_id]
    
    if 'name' in data:
        product['name'] = data['name']
    if 'description' in data:
        product['description'] = data['description']
    
    return jsonify(product)

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    product = products.pop(product_id)
    
    return jsonify(product)

@app.route('/products', methods=['GET'])
def get_all_products():
    return jsonify(list(products.values()))

@app.route('/product/<int:product_id>/image', methods=['POST'])
def upload_image(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    if 'icon' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    icon = request.files['icon']
    if icon.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if icon:
        # Read the file content
        file_data = icon.read()
        # Get the mimetype
        mimetype = icon.mimetype
        # Encode as base64
        encoded_data = base64.b64encode(file_data).decode('utf-8')
        
        # Store the base64 string and mimetype
        products[product_id]['icon'] = {
            'data': encoded_data,
            'mimetype': mimetype
        }
        
        return jsonify(products[product_id])

@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_image(product_id):
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    product = products[product_id]
    if not product['icon']:
        return jsonify({"error": "Image not found"}), 404
    
    # Decode the base64 image
    image_data = base64.b64decode(product['icon']['data'])
    
    # Return the image data with the correct mimetype
    return Response(image_data, mimetype=product['icon']['mimetype'])

if __name__ == '__main__':
    app.run(debug=True)