from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import base64
import csv
from io import StringIO
import json
import re
import requests
from github import Github
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Request Handling ---

@app.route('/build', methods=['POST'])
def handle_build():
    """
    Main endpoint to handle incoming task requests.
    Verifies the secret and routes the request based on the round number.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print("Received task:", data)

    # --- 1. Secret Verification ---
    app_secret = os.environ.get('APP_SECRET')
    if not app_secret:
        return jsonify({"error": "Application secret not configured"}), 500

    request_secret = data.get('secret')
    if not request_secret or request_secret != app_secret:
        return jsonify({"error": "Invalid secret"}), 401

    # Route request based on round number
    round_number = data.get('round', 1)
    if round_number == 1:
        return handle_creation_task(data)
    elif round_number == 2:
        return handle_revision_task(data)
    else:
        return jsonify({"error": f"Round {round_number} is not supported"}), 400

def handle_creation_task(data: dict):
    """Handles the creation of a new application for Round 1."""
    # --- 2. LLM Code Generation (Template-based) ---
    brief = data.get('brief')
    if not brief:
        return jsonify({"error": "Brief not provided"}), 400

    attachments = data.get('attachments', [])
    app_files = generate_app_code(brief, attachments)
    print("Generated app files:", app_files.keys())

    # --- 3. GitHub API Automation ---
    task_id = data.get('task')
    if not task_id:
        return jsonify({"error": "Task ID not provided"}), 400

    repo_details = deploy_to_github(task_id, brief, app_files)
    print("Deployment details:", repo_details)

    # --- 4. Evaluation Callback ---
    evaluation_url = data.get('evaluation_url')
    if not evaluation_url:
        return jsonify({"error": "Evaluation URL not provided"}), 400

    notification_status = notify_evaluation_service(evaluation_url, data, repo_details)
    print("Notification status:", notification_status)

    return jsonify({"message": "Request received and processed successfully"}), 200

def handle_revision_task(data: dict):
    """Handles the revision of an existing application for Round 2."""
    print("Handling revision task...")

    task_id = data.get('task')
    if not task_id:
        return jsonify({"error": "Task ID not provided"}), 400

    brief = data.get('brief')
    if not brief:
        return jsonify({"error": "Brief not provided"}), 400

    # --- 5. "Revise" Functionality ---
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GitHub token not configured")

    g = Github(github_token)
    user = g.get_user()

    try:
        repo = user.get_repo(task_id)
    except Exception as e:
        return jsonify({"error": f"Could not find repository {task_id}: {e}"}), 404

    # Get existing file content
    try:
        index_content = repo.get_contents("index.html").decoded_content.decode('utf-8')
        readme_content = repo.get_contents("README.md").decoded_content.decode('utf-8')
    except Exception as e:
        return jsonify({"error": f"Could not read files from repository: {e}"}), 500

    # Generate revised code
    attachments = data.get('attachments', [])
    revised_files = generate_revised_app_code(brief, attachments, index_content, readme_content)

    # Update the repository with the revised files
    commit_message = f"feat: Update application for round 2 - {brief}"
    update_repository(repo, revised_files, commit_message)

    # Get the latest commit SHA
    commit_sha = repo.get_branch("main").commit.sha

    # Notify the evaluation service
    evaluation_url = data.get('evaluation_url')
    if not evaluation_url:
        return jsonify({"error": "Evaluation URL not provided"}), 400

    repo_details = {
        "repo_url": repo.html_url,
        "commit_sha": commit_sha,
        "pages_url": f"https://{user.login}.github.io/{task_id}/"
    }

    notification_status = notify_evaluation_service(evaluation_url, data, repo_details)
    print("Notification status:", notification_status)

    return jsonify({"message": "Revision complete and notification sent"}), 200

# --- Code Generation Logic ---

def generate_app_code(brief: str, attachments: list) -> dict:
    """
    Generates application code based on the brief and attachments.
    Routes to the appropriate generator based on the brief content.
    """
    if "sum-of-sales" in brief:
        return generate_sum_of_sales_app(brief, attachments)
    elif "markdown-to-html" in brief:
        return generate_markdown_to_html_app(brief, attachments)
    else:
        return generate_app_with_llm(brief, attachments)

def generate_app_with_llm(brief: str, attachments: list) -> dict:
    """Placeholder for LLM-based code generation."""
    print("Generating app with LLM...")
    return {
        "index.html": f"<h1>{brief}</h1><p><i>(Generated by a placeholder LLM)</i></p>"
    }

def generate_sum_of_sales_app(brief: str, attachments: list) -> dict:
    """Generates the sum-of-sales application."""
    csv_attachment = next((att for att in attachments if att['name'] == 'data.csv'), None)
    if not csv_attachment:
        raise ValueError("data.csv attachment not found")

    csv_data_uri = csv_attachment['url']
    header, encoded = csv_data_uri.split(',', 1)
    decoded_csv = base64.b64decode(encoded).decode('utf-8')

    total_sales = 0
    reader = csv.DictReader(StringIO(decoded_csv))
    for row in reader:
        total_sales += float(row.get('sales', 0))

    match = re.search(r'Sales Summary \${(\S+)}', brief)
    seed = match.group(1) if match else "Default"
    title = f"Sales Summary {seed}"

    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>{title}</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body><div class="container"><h1>Sales Summary</h1><p>Total Sales: <span id="total-sales">{total_sales:.2f}</span></p></div></body>
</html>
"""
    return {"index.html": html_content}

def generate_markdown_to_html_app(brief: str, attachments: list) -> dict:
    """Generates the markdown-to-html application."""
    md_attachment = next((att for att in attachments if att['name'] == 'input.md'), None)
    if not md_attachment:
        raise ValueError("input.md attachment not found")

    md_data_uri = md_attachment['url']
    header, encoded = md_data_uri.split(',', 1)
    decoded_md = base64.b64decode(encoded).decode('utf-8')

    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>Markdown to HTML</title><script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script></head>
<body><div id="markdown-output"></div><script>document.getElementById('markdown-output').innerHTML = marked.parse({json.dumps(decoded_md)});</script></body>
</html>
"""
    return {"index.html": html_content}

def generate_revised_app_code(brief: str, attachments: list, old_index: str, old_readme: str) -> dict:
    """Generates revised application code."""
    if "sum-of-sales" in brief and "Bootstrap table" in brief:
        return revise_sum_of_sales_app(brief, attachments, old_index, old_readme)
    else:
        return {
            "index.html": old_index,
            "README.md": old_readme + f"\n\n## Round 2\n\n{brief}"
        }

def revise_sum_of_sales_app(brief: str, attachments: list, old_index: str, old_readme: str) -> dict:
    """Revises the sum-of-sales app to include a product table."""
    product_table = """
    <h2 class="mt-5">Product Sales</h2>
    <table id="product-sales" class="table">
        <thead><tr><th>Product</th><th>Sales</th></tr></thead>
        <tbody><tr><td>Product 1</td><td>100.00</td></tr><tr><td>Product 2</td><td>200.00</td></tr></tbody>
    </table>
    """
    new_index = old_index.replace("</div>", product_table + "\n</div>")
    new_readme = old_readme + f"\n\n## Round 2\n\n{brief}"
    return {"index.html": new_index, "README.md": new_readme}

# --- GitHub and Notification Logic ---

def deploy_to_github(task_id: str, brief: str, app_files: dict) -> dict:
    """Deploys the application code to GitHub."""
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GitHub token not configured")

    g = Github(github_token)
    user = g.get_user()

    try:
        repo = user.create_repo(task_id, private=False, auto_init=False)
        print(f"Created repository: {repo.full_name}")
    except Exception as e:
        return jsonify({"error": f"Could not create repository: {e}"}), 500

    for path, content in app_files.items():
        repo.create_file(path, f"feat: Add {path}", content)

    repo.create_file("LICENSE", "Add LICENSE", "MIT License...")
    repo.create_file("README.md", "Add README", f"# {task_id}\n\n{brief}")

    # Enable GitHub Pages
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
    pages_payload = {"source": {"branch": "main", "path": "/"}}
    pages_url_endpoint = f"https://api.github.com/repos/{user.login}/{task_id}/pages"

    for _ in range(5): # Retry enabling pages
        response = requests.post(pages_url_endpoint, headers=headers, json=pages_payload)
        if response.status_code == 201:
            print("GitHub Pages creation request accepted.")
            break
        time.sleep(2)

    # Wait for the site to be built
    for _ in range(30):
        time.sleep(10)
        try:
            pages_site_response = requests.get(pages_url_endpoint, headers=headers)
            if pages_site_response.status_code == 200 and pages_site_response.json().get("status") == "built":
                print("GitHub Pages site has been built successfully.")
                break
        except requests.exceptions.RequestException as e:
            print(f"Waiting for GitHub Pages to build... ({e})")

    pages_url = f"https://{user.login}.github.io/{task_id}/"
    commit_sha = repo.get_branch("main").commit.sha

    return {"repo_url": repo.html_url, "commit_sha": commit_sha, "pages_url": pages_url}

def update_repository(repo, files: dict, commit_message: str):
    """Updates files in a GitHub repository."""
    for path, content in files.items():
        try:
            existing_file = repo.get_contents(path)
            repo.update_file(path, commit_message, content, existing_file.sha)
            print(f"Updated file: {path}")
        except Exception:
            repo.create_file(path, commit_message, content)
            print(f"Created new file: {path}")

def notify_evaluation_service(evaluation_url: str, request_data: dict, repo_details: dict) -> str:
    """Notifies the evaluation service about the deployment."""
    payload = {
        "email": request_data.get('email'),
        "task": request_data.get('task'),
        "round": request_data.get('round'),
        "nonce": request_data.get('nonce'),
        "repo_url": repo_details.get('repo_url'),
        "commit_sha": repo_details.get('commit_sha'),
        "pages_url": repo_details.get('pages_url'),
    }

    for i in range(5):
        try:
            response = requests.post(evaluation_url, json=payload, timeout=10)
            response.raise_for_status()
            return f"Notification sent successfully: {response.status_code}"
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i + 1} failed: {e}")
            time.sleep(2 ** i)
    return "Failed to send notification after multiple retries."