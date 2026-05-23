from flask import Flask, render_template, request
import cv2 as cv

from generate_qr_image import generate_qr_image
from get_categories import get_categories, Category
from db_communication.get_free_qr import get_free_qr
from db_communication.update_database import update_database

app = Flask(__name__)


@app.route('/')
def home():
	categories = get_categories()
	
	return render_template('index.html', categories = categories)


@app.route('/submit', methods = ['POST'])
def handle_data():
	category_string = request.form.get('category_dropdown')
	category_parts = category_string.strip().split()
	category = Category(
		name = category_parts[0],
		max_mass = float(category_parts[1]),
		max_x = float(category_parts[2]),
		max_y = float(category_parts[3]),
		max_z = float(category_parts[4]),
	)
	destination = request.form.get('destination_input')
	
	qr_code = get_free_qr()
	update_database(
		qr_code = qr_code,
		max_mass = category.max_mass,
		max_x = category.max_x,
		max_y = category.max_y,
		max_z = category.max_z,
		destination = destination
	)
	
	qr_image = generate_qr_image(qr_code)
	cv.imwrite('static/latest_qr.png', qr_image)
	
	return render_template('submitted.html', category = category, destination = destination, qr_code = qr_code)


if __name__ == '__main__':
	app.run(debug = True)
