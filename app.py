from flask import Flask, request, jsonify
from fpdf import FPDF
import os
import re
import random
import string
from datetime import datetime
from threading import Lock

app = Flask(__name__)
lock = Lock()

# Pre-stored texts for numerology numbers (example)
life_path_texts = {
    1: ["Life Path 1: You are a natural leader."],
    2: ["Life Path 2: You are a peacemaker."],
    # Add more as needed
}
expression_texts = {
    1: ["Expression 1: You are ambitious and driven."],
    2: ["Expression 2: You are diplomatic and sensitive."],
    # Add more as needed
}
hearts_desire_texts = {
    1: ["Heart's Desire 1: You desire independence."],
    2: ["Heart's Desire 2: You desire harmony."],
    # Add more as needed
}

# Numerology calculation functions
def calculate_life_path_number(birthdate):
    total = sum(map(int, re.findall(r'\d', birthdate)))
    while total > 9:
        total = sum(map(int, str(total)))
    return total

def calculate_expression_number(full_name):
    letter_values = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
    }
    total = sum(letter_values.get(char, 0) for char in full_name.upper() if char.isalpha())
    while total > 9:
        total = sum(map(int, str(total)))
    return total

def calculate_hearts_desire_number(full_name):
    vowel_values = {
        'A': 1, 'E': 5, 'I': 9, 'O': 6, 'U': 3, 'Y': 7
    }
    total = sum(vowel_values.get(char, 0) for char in full_name.upper() if char in vowel_values)
    while total > 9:
        total = sum(map(int, str(total)))
    return total

def generate_numerology_report(name, birthdate):
    life_path_number = calculate_life_path_number(birthdate)
    expression_number = calculate_expression_number(name)
    hearts_desire_number = calculate_hearts_desire_number(name)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="Numerology Report", ln=True, align='C')
    pdf.ln(10)
    
    # Personal Details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Birthdate: {birthdate}", ln=True)
    pdf.ln(10)
    
    # Life Path Number
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt=f"Life Path Number: {life_path_number}", ln=True)
    pdf.set_font("Arial", size=12)
    for line in life_path_texts[life_path_number]:
        pdf.multi_cell(0, 10, txt=line)
    pdf.ln(10)
    
    # Expression Number
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt=f"Expression Number: {expression_number}", ln=True)
    pdf.set_font("Arial", size=12)
    for line in expression_texts[expression_number]:
        pdf.multi_cell(0, 10, txt=line)
    pdf.ln(10)
    
        # Heart's Desire Number
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt=f"Heart's Desire Number: {hearts_desire_number}", ln=True)
    pdf.set_font("Arial", size=12)
    for line in hearts_desire_texts[hearts_desire_number]:
        pdf.multi_cell(0, 10, txt=line)
    pdf.ln(10)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_birthdate = re.sub(r'\W+', '', birthdate)
    filename = f"Numerology_Report_{sanitized_birthdate}_{timestamp}.pdf"
    
    # Save PDF to storage
    if not os.path.exists('storage'):
        os.makedirs('storage')
    filepath = os.path.join('storage', filename)
    pdf.output(filepath)
    
    return filepath

@app.route('/', methods=['GET'])
def home():
    return "", 204

@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    phone_number = data.get('phone_number')
    birthdate = data.get('birthdate')
    
    if not all([email, name, phone_number, birthdate]):
        return jsonify({"error": "Missing required fields"}), 400
    
    with lock:
        filepath = generate_numerology_report(name, birthdate)
    
    download_link = f"{request.url_root}download/{os.path.basename(filepath)}"
    
    response_data = {
        "email": email,
        "name": name,
        "phone_number": phone_number,
        "birthdate": birthdate,
        "download_link": download_link
    }
    
    return jsonify(response_data), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory('storage', filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=False)
