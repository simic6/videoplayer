from flask import Flask, render_template, redirect, make_response
import subprocess

app = Flask(__name__)

# Route for home page (rendering index.html)
@app.route('/')
def index():
    return render_template('index.html')  # This will render your HTML page

# Route to run merged.py script
@app.route('/run')
def run_python_script():
    # Run the Python script 'merged.py' using subprocess without error handling
    subprocess.run(['python', 'merged.py'], capture_output=True, text=True)

    # Create a response to redirect to Google and add cache-control headers
    response = make_response(redirect('https://www.youtube.com'))
    
    # Prevent caching and history in the browser
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
