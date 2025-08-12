from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import json
import uuid

app = Flask(__name__)
CORS(app)

# redis connection
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.json
        command = data.get('command')
        
        print(f"Received command: {command}")
        
        # create a unique task ID
        task_id = str(uuid.uuid4())
        
        # push task to agent queue
        task = {
            'id': task_id,
            'command': command
        }
        redis_client.lpush('agent_tasks', json.dumps(task))
        print(f"Pushed task {task_id} to agent queue")
        
        # essentially pauses execution until we get out final result. is of type key: [list] where 'list' is our result
        result = redis_client.blpop(f'final_result:{task_id}', timeout=30)
        
        if result:
            # result is a tuple (queue_name, data)
            result_data = json.loads(result[1])
            return jsonify({
                'success': True,
                'message': result_data.get('result', 'Command completed')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Command timed out'
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """Check task status"""
    result = redis_client.get(f'final_result:{task_id}')
    if result:
        return jsonify({
            'status': 'complete',
            'result': json.loads(result)
        })
    else:
        return jsonify({
            'status': 'pending'
        })
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    print("Starting Browser Agent Server on http://localhost:3001")
    print("Make sure Redis is running: redis-server")
    app.run(host='0.0.0.0', port=3001)
