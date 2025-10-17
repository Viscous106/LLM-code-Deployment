from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_task():
    """
    Handles incoming task requests.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print("Received task:", data)

    # Secret verification
    app_secret = os.environ.get('APP_SECRET')
    if not app_secret:
        return jsonify({"error": "Application secret not configured"}), 500

    request_secret = data.get('secret')
    if request_secret != app_secret:
        return jsonify({"error": "Invalid secret"}), 401

    # Application Generation
    brief = data.get('brief')
    if not brief:
        return jsonify({"error": "Brief not provided"}), 400

    app_code = generate_app_code(brief)
    print("Generated app code:", app_code)

    # GitHub Deployment
    task_id = data.get('task')
    if not task_id:
        return jsonify({"error": "Task ID not provided"}), 400

    repo_details = deploy_to_github(task_id, app_code)
    print("Deployment details:", repo_details)

    # Evaluation Notification
    evaluation_url = data.get('evaluation_url')
    if not evaluation_url:
        return jsonify({"error": "Evaluation URL not provided"}), 400

    notification_status = notify_evaluation_service(evaluation_url, data, repo_details)
    print("Notification status:", notification_status)

    return jsonify({"message": "Request received successfully"}), 200

def generate_app_code(brief: str) -> str:
    """
    Generates application code based on the brief.
    Currently, a placeholder.
    """
    # In the future, this will use an LLM to generate code.
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
</head>
<body>
    <h1>Application Brief</h1>
    <p>{brief}</p>
</body>
</html>
"""

def deploy_to_github(task_id: str, app_code: str) -> dict:
    """
    Deploys the application code to GitHub.
    Currently, a placeholder.
    """
    # In the future, this will use the GitHub API.
    print(f"Deploying app for task {task_id}...")
    print(app_code)

    # Placeholder details
    return {
        "repo_url": f"https://github.com/user/{task_id}",
        "commit_sha": "abc1234",
        "pages_url": f"https://user.github.io/{task_id}/"
    }

def notify_evaluation_service(evaluation_url: str, request_data: dict, repo_details: dict) -> str:
    """
    Notifies the evaluation service about the deployment.
    Currently, a placeholder.
    """
    payload = {
        "email": request_data.get('email'),
        "task": request_data.get('task'),
        "round": request_data.get('round'),
        "nonce": request_data.get('nonce'),
        "repo_url": repo_details.get('repo_url'),
        "commit_sha": repo_details.get('commit_sha'),
        "pages_url": repo_details.get('pages_url'),
    }

    # In the future, this will send a POST request.
    print(f"Notifying {evaluation_url} with payload:")
    import json
    print(json.dumps(payload, indent=2))

    return "Notification sent (simulated)"

if __name__ == '__main__':
    app.run(debug=True, port=5000)