# Student Application

This application receives a task, generates a web application, deploys it to GitHub, and notifies an evaluation service.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Create a `.env` file:**
    Create a `.env` file in this directory with the following content:
    ```
    APP_SECRET=your_secret_here
    ```
    Replace `your_secret_here` with the actual secret provided.

## Running the Application

To run the application, execute the following command:
```bash
python app.py
```
The server will start on `http://127.0.0.1:5000`.