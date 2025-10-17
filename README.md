# LLM Code Deployment Project

This project is an automated system for building, deploying, and revising web applications based on dynamic tasks. It's designed to simulate the "student" side of a coding assignment, where an application receives a task, generates the code, deploys it, and notifies an evaluation service.

## Features

- **Automated Application Generation:** Dynamically generates web applications from task briefs.
- **GitHub Integration:** Automatically creates a new GitHub repository for each task.
- **GitHub Pages Deployment:** Deploys the generated application to GitHub Pages, making it live on the web.
- **Evaluation Notification:** Notifies an external evaluation service with the deployment details.
- **Secure:** Uses environment variables to handle sensitive information like secrets and API tokens.
- **Extensible:** Can be extended to support new task templates and more complex application generation logic.

## How it Works

The application is a Flask-based web server that listens for POST requests containing a task in JSON format. When a task is received, it performs the following steps:

1.  **Secret Verification:** It verifies a secret in the request to ensure it's from an authorized source.
2.  **Application Generation:** It parses the task `brief` and generates the necessary HTML, CSS, and JavaScript files.
3.  **GitHub Deployment:** It creates a new public repository on GitHub, uploads the generated files, and enables GitHub Pages.
4.  **Evaluation Notification:** It sends a POST request to the specified `evaluation_url` with the details of the deployed application.

## Getting Started

### Prerequisites

- Python 3.8+
- A GitHub account and a [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `repo` and `workflow` scopes.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r student_app/requirements.txt
    ```

3.  **Create a `.env` file:**
    Create a file named `.env` inside the `student_app` directory and add the following content:
    ```
    APP_SECRET=your_secret_here
    GITHUB_TOKEN=your_github_token_here
    ```
    - Replace `your_secret_here` with your chosen secret.
    - Replace `your_github_token_here` with your GitHub Personal Access Token.

### Running the Application Locally

To run the application locally, use `gunicorn`:
```bash
gunicorn student_app.app:app
```
The server will start on `http://127.0.0.1:8000`.

## Usage

You can test the application by sending a POST request to the `/` endpoint. Here is an example using `curl`:

```bash
curl -X POST http://127.0.0.1:5000/ \
-H "Content-Type: application/json" \
-d '{
    "email": "student@example.com",
    "secret": "your_secret_here",
    "task": "sum-of-sales-test",
    "round": 1,
    "nonce": "ab12-cde3-45fg-67hi",
    "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to \"Sales Summary ${test-seed}\", displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
    "attachments": [{
        "name": "data.csv",
        "url": "data:text/csv;base64,c2FsZXMsYWRtaW4scHJvZHVjdApzYWxlMSwxMCxwcm9kdWN0MQpzYWxlMixyZWNvcmQsMjAKc2FsZTMsNDUscHJvZHVjdDM="
    }],
    "evaluation_url": "https://httpbin.org/post"
}'
```

Replace `your_secret_here` with the secret you defined in your `.env` file. If successful, this will create a new repository on your GitHub account named `sum-of-sales-test` with a deployed GitHub Pages site.

## Deployment

The application is configured for deployment on platforms like Heroku or Render. Once deployed, the live application will be available at:

[https://your-app-name.onrender.com](https://your-app-name.onrender.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.