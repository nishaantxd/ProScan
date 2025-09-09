# ProScan

A sophisticated AI-powered resume analysis tool that leverages Google's Generative AI (Gemini) to provide in-depth resume analysis and job description comparison. Built with Streamlit, the application offers modern UI with light/dark mode support and CAPTCHA verification.

## Key Features

### AI-Powered Analysis
- **Advanced Resume Analysis**: Utilizes Google's Gemini AI for sophisticated resume parsing and analysis
- **Skill Extraction**: Automatically identifies technical and soft skills from resumes
- **Job Description Matching**: Compares resumes against job descriptions with detailed scoring
- **Smart Recommendations**: Suggests relevant Udemy courses for skill gaps

### User Experience
- **Multi-Format Support**: Upload resumes in PDF or image formats
- **Real-time Analysis**: Get instant feedback on resume-job description match
- **Interactive UI**: Modern interface with light/dark mode toggle
- **Secure Access**: CAPTCHA verification for enhanced security

### Analysis Output
- Match percentage with detailed breakdown
- Technical and soft skills analysis
- Experience and project evaluation
- Customized interview questions
- Career improvement recommendations
- Relevant course suggestions

## Project Structure

```
ProScan/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Project dependencies
├── backend/
│   ├── resume_analyzer.py      # Google Gemini AI integration
│   ├── document_extractor.py   # PDF and document text extraction
│   ├── resume_parser.py        # Resume parsing logic
│   ├── jd_comparator.py        # Job description comparison logic
│   └── .env                    # Environment variables (not in git)
```

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **AI/ML**: 
  - Google Generative AI (Gemini-1.5-flash)
  - spaCy for NLP processing
- **Document Processing**: 
  - PyMuPDF
  - python-docx
  - PyPDF2
- **Security**: 
  - CAPTCHA verification
  - Environment variable management

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/ProScan.git
cd ProScan
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. Run the application:
```bash
streamlit run app.py
```

## AWS Elastic Beanstalk Deployment

1. **Prepare Your Application**
   - Ensure your repository is up to date
   - Check requirements.txt is complete
   - Verify .gitignore excludes unnecessary files

2. **AWS Console Deployment**
   - Go to AWS Elastic Beanstalk Console
   - Click "Create Application"
   - Choose Python platform
   - Upload your code as a zip file
   - Choose appropriate instance type (t2.small recommended)

3. **Environment Variables**
   - In Elastic Beanstalk Console, go to Configuration
   - Add environment variable:
     - Key: GOOGLE_API_KEY
     - Value: your_google_api_key_here

4. **Health Checks**
   - Monitor application health in EB Console
   - Check logs if any issues arise
   - Verify all dependencies are installed

## Security Notes

- Never commit .env files or API keys
- Keep Python packages updated
- Use secure HTTPS connections
- Regularly update dependencies
- Monitor API usage and costs

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
