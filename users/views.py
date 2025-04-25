import json
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserRegistration
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')

user_threads = {}

from .models import UserThread

import markdown2, pdfkit
from django.conf import settings
from .models import ChatMessage

from django.core.mail import EmailMessage, get_connection

from fpdf import FPDF

def text_to_pdf(text_file_path, pdf_file_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    with open(text_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            pdf.multi_cell(0, 10, line.strip())

    pdf.output(pdf_file_path)
    print(f"PDF generated at: {pdf_file_path}")


def send_basic_email_with_attachment(file_path, subject, body, from_email, to_email):
    subject = "Sample Subject with Attachment"
    body = "Hi,\n\nPlease find the attached file.\n\nBest regards,\nYour Team"

    # Create the email
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to_email
    )

    # Attach a file
    email.attach_file(file_path)  # Replace with actual file path

    # Send it
    try:
        email.send()
        print("Email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)


def generate_pdf_from_thread(thread_id):
    messages = ChatMessage.objects.filter(thread_id=thread_id).order_by('timestamp')
    markdown = ""
    for msg in messages:
        prefix = "**User:**" if msg.role == "user" else "**Assistant:**"
        markdown += f"{prefix}\n\n{msg.content}\n\n---\n"
    print(markdown)
    html = markdown2.markdown(markdown)
    output_path = f"/tmp/ai_roadmap_{thread_id}.pdf"
    pdfkit.from_string(html, output_path)
    return output_path

def send_email_with_pdf(thread_id, pdf_path, recipient_email):
    email = EmailMessage(
        subject="Your AI Roadmap Discussion Summary",
        body="Hi there,\n\nAttached is the PDF summary of your AI roadmap discussion.\n\nBest,\nAryng AI",
        to=[recipient_email]
    )
    email.attach_file(pdf_path)
    email.send()

def get_user_threads(request):
    session_key = request.session.session_key or request.session.create()

    threads = UserThread.objects.filter(session_key=session_key).values(
        'id', 'title', 'created_at'
    )

    return JsonResponse(list(threads), safe=False)


@csrf_exempt
def chat_with_assistant(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        body = json.loads(request.body)
        user_id = body.get('user_id')
        message = body.get('message')
        email = body.get('email')

        if not user_id or not message:
            return JsonResponse({'error': 'Missing user_id or message'}, status=400)

        thread_id = user_threads.get(user_id)
        if not thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
            user_threads[user_id] = thread_id

        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            run_check = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_check.status == "completed":
                break


        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value
        print(response)
        if "finalized ai roadmap" in response.lower():
            with open('media/roadmap.txt', "w") as f:
                f.write(response)

                text_to_pdf('media/roadmap.txt', 'media/roadmap.pdf')

                send_basic_email_with_attachment('media/roadmap.pdf', 'Hello', 'Testing','MS_sjxLym@test-68zxl277vwm4j905.mlsender.net',['mkgganesh@gmail.com'])


        return JsonResponse({'reply': response})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            email = data.get("email")
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({"error": "Invalid email address"}, status=400)

            # Optional: Check if the email already exists
            if UserRegistration.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already registered"}, status=409)

            user = UserRegistration.objects.create(
                first_name=data.get("firstName"),
                last_name=data.get("lastName"),
                email=email,
                company_name=data.get("companyName"),
                industry=data.get("industry"),
                company_size=data.get("companySize"),
                job_title=data.get("jobTitle")
            )

            return JsonResponse({"message": "User registered successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_user(request):

    users = UserRegistration.objects.all()
    for user in users:
        print(user.email)
    
    return HttpResponse(users)