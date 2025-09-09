# Setup Instructions

This document provides detailed steps for setting up the ProScan application for development or deployment.

## Local Development Setup

1. **Python Environment Setup**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Unix/MacOS
   pip install -r requirements.txt
   ```

2. **Google API Setup**
   - Visit Google Cloud Console
   - Create a new project or select existing
   - Enable Generative AI API
   - Create credentials (API key)
   - Copy the API key

3. **Environment Configuration**
   - Create a `.env` file in the backend directory
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

4. **Running the Application**
   ```bash
   streamlit run app.py
   ```

## Deployment Steps

### AWS Deployment

1. **EC2 Setup**
   - Launch EC2 instance (t2.micro or larger)
   - Configure security group (open port 8501)
   - SSH into instance

2. **Environment Setup**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv
   git clone https://github.com/your-username/ProScan.git
   cd ProScan
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   - Set up `.env` file as in local setup
   - Or use AWS Parameter Store/Secrets Manager

4. **Running in Production**
   ```bash
   # Install PM2 for process management
   sudo npm install -g pm2
   # Start the application
   pm2 start "streamlit run app.py" --name proscan
   ```

### Streamlit Cloud Deployment

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy

## Common Issues and Solutions

1. **ModuleNotFoundError**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

2. **API Key Issues**
   - Verify .env file location
   - Check API key validity
   - Ensure API is enabled in Google Cloud Console

3. **PDF Processing Issues**
   - Check PDF file permissions
   - Ensure PyMuPDF is properly installed

4. **Image Upload Issues**
   - Verify Tesseract OCR installation
   - Check file permissions

## Maintenance

1. **Regular Updates**
   ```bash
   pip freeze > requirements.txt  # Update dependencies
   git add .
   git commit -m "Update dependencies"
   git push
   ```

2. **Monitoring**
   - Check Streamlit Cloud dashboard
   - Monitor API usage in Google Cloud Console
   - Review application logs

3. **Backup**
   - Regularly backup .env files
   - Document any custom configurations
