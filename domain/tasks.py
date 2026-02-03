# Celery Tasks (The bridge between Queue and Service)
from celery import shared_task
from interface_layer.models import Summary  # <--- IMPORTING THE MODEL
from domain.services import ResearchAgent

@shared_task
def process_summary_task(summary_id):
    """
    This runs inside the Celery Worker container.
    """
    try:
        # 1. READ: Use the Model to get data from Postgres
        summary_instance = Summary.objects.get(id=summary_id)
        
        # 2. PROCESS: Pass pure data (strings/ints) to the Service
        # We pass the URL string, not the whole model object.
        agent = ResearchAgent()
        result_text = agent.generate_summary(url=summary_instance.url)
        
        # 3. WRITE: Use the Model to save the result back to Postgres
        summary_instance.content = result_text
        summary_instance.status = 'COMPLETED'
        summary_instance.save() # <--- WRITING TO DB

    except Summary.DoesNotExist:
        print(f"Summary with id {summary_id} not found!")
    except Exception as e:
        # Handle failure
        summary_instance = Summary.objects.get(id=summary_id)
        summary_instance.status = 'FAILED'
        summary_instance.save()