# Deployment Instructions

## Local Deployment

1. Install Python 3.10 or higher
2. Clone the repository or extract the deployment package
3. Navigate to the application directory
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Copy `.env.sample` to `.env` and configure with your credentials
6. Run the application:
   ```
   python start.py
   ```
7. Access the web interface at http://localhost:7860

## Server Deployment

### Using Docker

1. Install Docker on your server
2. Build the Docker image:
   ```
   docker build -t agentic-insurtech .
   ```
3. Run the container:
   ```
   docker run -p 7860:7860 -e SUPABASE_URL=your_url -e SUPABASE_KEY=your_key agentic-insurtech
   ```

### Using a Web Server (Nginx + Gunicorn)

1. Install Nginx and Gunicorn
2. Install application dependencies:
   ```
   pip install -r requirements.txt gunicorn
   ```
3. Configure Nginx to proxy requests to Gunicorn:
   ```
   server {
       listen 80;
       server_name your_domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
4. Start Gunicorn:
   ```
   gunicorn -w 4 -b 127.0.0.1:8000 app.ui.app:app
   ```
5. Set up a systemd service for automatic startup

## Cloud Deployment

### Using Heroku

1. Install Heroku CLI
2. Login to Heroku:
   ```
   heroku login
   ```
3. Create a new Heroku app:
   ```
   heroku create agentic-insurtech
   ```
4. Set environment variables:
   ```
   heroku config:set SUPABASE_URL=your_url SUPABASE_KEY=your_key
   ```
5. Deploy the application:
   ```
   git push heroku main
   ```

### Using AWS

1. Create an EC2 instance with Ubuntu
2. Install dependencies:
   ```
   sudo apt update
   sudo apt install python3-pip nginx
   ```
3. Clone the repository and install requirements
4. Configure Nginx and set up a systemd service
5. Set up environment variables in a .env file

## Troubleshooting

- If the application fails to start, check the logs for errors
- Ensure all environment variables are correctly set
- Verify that the required ports are open in your firewall
- Check that the database connection is working properly
