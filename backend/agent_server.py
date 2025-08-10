from flask import Flask, request, jsonify
from flask_cors import CORS
from thread_safe_browser import thread_safe_browser

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.json
        command = data.get('command')
        
        print(f"Received command: {command}")  
        
        # Use your execute function
        result = thread_safe_browser.execute_task(command)
        
        print(f"Result: {result}") 
        
        return jsonify({
            'success': True,
            'message': result
        })
    except Exception as e:
        print(f"Error: {str(e)}")  
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    print("Starting Browser Agent Server on http://localhost:3000")
    app.run(debug=True, port=3000)