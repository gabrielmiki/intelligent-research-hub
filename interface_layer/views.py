from django.shortcuts import render
from django.http import HttpResponse

def make_summary_request(request):
    # TODO: query url

    # TODO: verify weather url is valid

    # TODO: Save to DB (Summary(url=..., status='PENDING')).
    # ⛔ STOP: You must not fetch the URL content inside the Django view. If the target website is slow or times out 
    # (e.g., takes 10 seconds to load), your Django server will hang for 10 seconds. If 5 users do this at once, your 
    # API becomes unresponsive.

    # ✅ The Fix: The View should only save the URL to the DB (status: PENDING) and fire the Celery task. 
    # The Celery Worker (background process) is responsible for fetching the content.

    # TODO: Enqueue Task (process_summary.delay(summary_id))

    # TODO: Return HTTP 202 Accepted (with the summary_id)

def get_summary_status(request, summary_id):
    # TODO: query database for summary status by summary_id

    # TODO: if summary exists, return status
    # ⛔ STOP: Do not query Redis/Celery directly from the View to check status. It is slow, complex, and unnecessary. 
    
    # ✅ The Fix: When you receive the request, you immediately save a record in Postgres with status='PENDING'. 
    # The Database is your Single Source of Truth. If the record exists in the DB, you know the status. 
    # If it doesn't, it's a 404.

    # TODO: return response to user

def get_summaries(request, status):
    # TODO: query database for summaries with given status

    # TODO: return list of summaries to user