from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.models import Competition, Match, Participant
from .serializers import CompetitionSerializer, MatchSerializer, ParticipantSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_competition(request):

    if request.method == 'GET':
        competitions = Competition.objects.all().filter(created_by=request.user)
        serializer = CompetitionSerializer(competitions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CompetitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_participants(request, competition_id):
    try:
        competition = Competition.objects.get(id=competition_id)
    except Competition.DoesNotExist:
        raise NotFound('Competition not found.')
    
    if request.method == 'GET':
        # Handle GET request to list participants for a competition
        participants = Participant.objects.filter(competition_id=competition_id)
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Handle POST request to create a participant for a competition
        serializer = ParticipantSerializer(data=request.data, context={'competition': competition})
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_matches(request, competition_id):
    try:
        competition = Competition.objects.get(id=competition_id)
    except Competition.DoesNotExist:
        raise NotFound('Competition not found.')

    is_participant = Participant.objects.filter(user=request.user, competition=competition).exists()
    if request.user != competition.created_by and not is_participant:
        raise PermissionDenied("You are not authorized to view these matches.")

    if request.method == 'GET':
        matches = Match.objects.filter(competition=competition_id)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Handle POST request to create a participant for a competition
        serializer = MatchSerializer(data=request.data, context={'competition': competition})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE', 'GET'])
@permission_classes([IsAuthenticated])  # Restrict actions to authenticated users
def update_delete_detail_match(request, competition_id, match_id):
    match = get_object_or_404(Match, id=match_id, competition_id=competition_id)

    if request.method == 'PUT':
        serializer = MatchSerializer(match, data=request.data, partial=True)  # Allow partial updates
        competition = get_object_or_404(Competition, id=competition_id)
        if request.user != competition.created_by:
            raise PermissionDenied("Only the owner of a competition can update matches")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        competition = get_object_or_404(Competition, id=competition_id)
        if request.user == competition.created_by:
            match.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied("Only the owner of a competition can delete matches")
    elif request.method == "GET":
        competition = get_object_or_404(Competition, id=competition_id)
        is_participant = Participant.objects.filter(user=request.user, competition=competition).exists()
        if request.user == competition.created_by or is_participant:
            serializer = MatchSerializer(match)
            return Response(serializer.data, status=200)
        raise PermissionDenied("Only the owner of a competition can delete matches") 



# match = Match.objects.all().filter(id=)
# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def match_list_create_view(request, competition_id):

#     if request.method == 'GET':
#         # check user is in competition
#         user_in = Participant.objects.filter(competition_id=competition_id, user=request.user)
#         owner = Competition.objects.filter(id=competition_id, created_by=request.user)

#         if not (user_in or owner):
#             return Response({'error': 'user not in this competition'}, status=status.HTTP_400_BAD_REQUEST)

#         matches = Match.objects.filter(competition_id=competition_id)
#         serializer = MatchSerializer(matches, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     elif request.method == 'POST':
#         request.data['competition'] = competition_id

#         serializer = MatchSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
