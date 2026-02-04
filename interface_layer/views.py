from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Summary
from .serializer import SummaryRequestSerializer, SummaryDetailSerializer
from domain.tasks import process_summary_task

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Ensures request.user exists
def make_summary_request(request):
    """
    Receives a URL, saves it as PENDING, and triggers the background worker.
    """
    # 1. Validation (Verify URL is valid)
    # The serializer automatically checks if the URL format is correct.
    serializer = SummaryRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        # 2. Save to DB (Status: PENDING)
        # We attach the current user manually since it's not in the request body
        summary = serializer.save(user=request.user, status='PENDING')

        # 3. Enqueue Task
        # .delay() is the magic method that sends this to Redis/Celery
        process_summary_task.delay(summary.id)

        # 4. Return HTTP 202 Accepted
        # 202 literally means: "I have received your request but haven't finished processing it."
        return Response(
            {'id': summary.id, 'status': summary.status, 'message': 'Request queued.'},
            status=status.HTTP_202_ACCEPTED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary_status(request, summary_id):
    """
    Checks the status of a specific request.
    """
    # 1. Query Database
    # get_object_or_404 handles the "Does not exist" error automatically
    summary = get_object_or_404(Summary, id=summary_id, user=request.user)

    # 2. Return Response
    serializer = SummaryDetailSerializer(summary)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summaries(request):
    """
    Lists summaries, optionally filtering by status (e.g., ?status=COMPLETED)
    """
    # 1. Filter by Status (Optional)
    status_param = request.query_params.get('status')
    
    # Base query: Only show the logged-in user's data
    queryset = Summary.objects.filter(user=request.user)

    if status_param:
        queryset = queryset.filter(status=status_param.upper())

    # 2. Return List
    serializer = SummaryDetailSerializer(queryset, many=True)
    return Response(serializer.data)