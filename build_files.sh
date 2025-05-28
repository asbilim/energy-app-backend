#!/bin/bash

# Install Node.js dependencies (including Tailwind CSS)
npm install

# Compile Tailwind CSS (using the script from package.json)
npm run build:css

# Install Python dependencies
pip install -r requirements.txt

# Collect Django static files
python manage.py collectstatic --noinput