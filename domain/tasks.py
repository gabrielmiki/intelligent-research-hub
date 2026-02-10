# Celery Tasks (The bridge between Queue and Service)
from celery import shared_task
from interface_layer.models import Summary  # <--- IMPORTING THE MODEL
from domain.services import ResearchAgent
import time

@shared_task
def debug_hello_world():
    print("🚀 HELLO FROM CELERY! The task has started.")
    time.sleep(5)  # Simulate some work
    print("✅ HELLO FROM CELERY! The task is finished.")
    return "Task Complete"

@shared_task
def process_summary_task(summary_id):
    try:
        # 1. Get the DB Record
        summary = Summary.objects.get(id=summary_id)
        summary.status = 'PROCESSING'
        summary.save()

        # 2. Instantiate the Service
        agent = ResearchAgent()

        # 3. FETCH & CLEAN
        # The service does the hard work of removing HTML tags
        clean_text = agent.get_content_from_url(summary.url)
        
        # Save the clean text so we can debug later if needed
        summary.input_content = clean_text 
        summary.save()

        # 4. SUMMARIZE
        ai_summary = agent.summarize_text(clean_text)

        # 5. Finish
        summary.output_summary = ai_summary
        summary.status = 'COMPLETED'
        summary.save()

    except Exception as e:
        summary = Summary.objects.get(id=summary_id)
        summary.status = 'FAILED'
        # Ideally, save the error message to a new field or log it
        summary.save()