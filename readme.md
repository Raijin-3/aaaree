The users app is a component of a Django-based web platform that allows users to register, interact with an AI assistant via OpenAI's Assistant API, generate PDF summaries, and receive automated email notifications using MailerSend.

Features
User registration and validation

Chat interaction with OpenAI Assistant API

Session-aware thread tracking

Auto PDF generation when assistant responds with specific phrases

Email delivery with PDF attachments using MailerSend

Text-to-PDF conversion via FPDF

Technology Stack
Django 4.2+

PostgreSQL or Supabase (optional integration)

OpenAI Assistant API

FPDF (for PDF creation)

MailerSend (for transactional emails)

dotenv for secure environment configuration

Setup Instructions
1. Clone the Repository
git clone https://github.com/your-org/your-repo.git
cd your-repo

2. Create a Virtual Environment
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

3. Install Dependencies
pip install -r requirements.txt

4. Environment Configuration
Create a .env file in the root directory:

API_KEY=your_openai_api_key
ASSISTANT_ID=your_openai_assistant_id
MAILERSEND_API_KEY=your_mailersend_api_key
FROM_EMAIL=your_verified_mailersend_sender@example.com

5. Apply Migrations and Run the Server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
Endpoints
POST /api/register/
Registers a new user.

Request Payload:
{
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane@example.com",
  "companyName": "Acme Corp",
  "industry": "Finance",
  "companySize": "11-50",
  "jobTitle": "Analyst"
}
POST /api/chat/
Sends a message to the assistant and returns a reply. If the assistant responds with the phrase "finalized AI roadmap", the response will be saved as text, converted to PDF, and emailed to the user.

Request Payload:
{
  "user_id": "jane@example.com",
  "email": "jane@example.com",
  "message": "Can you give me the finalized AI roadmap?"
}

GET /api/threads/
Retrieves all chat threads associated with the user's current session.

PDF Generation Workflow
When the assistant's response includes the phrase "finalized AI roadmap":

The response text is saved to media/roadmap.txt

It is converted to media/roadmap.pdf using FPDF

The PDF is emailed using Django's email backend configured with MailerSend

MailerSend Setup
Register and verify your domain with MailerSend
Generate an API key
Configure Django to use MailerSend SMTP:

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailersend.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.getenv("MAILERSEND_API_KEY")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("FROM_EMAIL")

PDF Generation with FPDF
The text_to_pdf() function uses FPDF to convert .txt files to .pdf. It supports multi-line cell formatting and auto page breaks.
