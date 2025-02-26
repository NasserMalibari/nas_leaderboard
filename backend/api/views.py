from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.models import Competition, Match, Participant, ParticipantStats
from .serializers import CompetitionSerializer, MatchSerializer, ParticipantSerializer, ParticipantStatsSerializer, UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import generics
from django.contrib.auth.models import User

# @extend_schema(
#     description="Retrieve a list of competitions created by the authenticated user or create a new competition.",
#     methods=['GET'],
#     responses={
#         200: CompetitionSerializer(many=True),  # Response for GET
#         401: OpenApiTypes.OBJECT,  # Unauthorized
#     },
#     examples=[
#         OpenApiExample(
#             name="Example Request (GET)",
#             description="Example of a successful GET request.",
#             value=[
#                 {
#                     "id": 1,
#                     "name": "Tournament 1",
#                     "created_by": 1,
#                 },
#                 {
#                     "id": 2,
#                     "name": "Tournament 2",
#                     "created_by": 1,
#                 },
#             ],
#             response_only=True,  # This example is only for the response
#         ),
#     ],
# )
# @extend_schema(
#     description="Create a new competition.",
#     methods=['POST'],
#     request=CompetitionSerializer,  # Request body for POST
#     responses={
#         201: CompetitionSerializer,  # Response for POST (created)
#         400: OpenApiTypes.OBJECT,  # Bad request
#         401: OpenApiTypes.OBJECT,  # Unauthorized
#     },
#     examples=[
#         OpenApiExample(
#             name="Example Request (POST)",
#             description="Example of a successful POST request.",
#             value={
#                 "name": "New Tournament",
#             },
#             request_only=True,  # This example is only for the request
#         ),
#         OpenApiExample(
#             name="Example Response (POST)",
#             description="Example of a successful POST response.",
#             value={
#                 "id": 3,
#                 "name": "New Tournament",
#                 "created_by": 1,
#             },
#             response_only=True,  # This example is only for the response
#         ),
#     ],
# )
@extend_schema(
    methods=["GET"],
    summary="List user competitions",
    description="Retrieve a list of all competitions created by the authenticated user.",
    responses={
        200: OpenApiResponse(response=CompetitionSerializer(many=True), description="List of user's competitions retrieved successfully"),
    },
    tags=["competitions"]
)
@extend_schema(
    methods=["POST"],
    summary="Create competition",
    description="Create a new competition. The authenticated user will be set as the competition creator.",
    request=CompetitionSerializer,
    responses={
        201: OpenApiResponse(response=CompetitionSerializer, description="Competition created successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
    },
    tags=["competitions"]
)
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

@extend_schema(
    methods=["GET"],
    summary="List participants",
    description="Retrieve a list of all participants for a specific competition.",
    responses={
        200: OpenApiResponse(response=ParticipantSerializer(many=True), description="List of participants retrieved successfully"),
        404: OpenApiResponse(description="Competition not found")
    },
    tags=["participants"]
)
@extend_schema(
    methods=["POST"],
    summary="Add participant",
    description="Add a new participant to a competition.",
    request=ParticipantSerializer,
    responses={
        201: OpenApiResponse(response=ParticipantSerializer, description="Participant added successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
        404: OpenApiResponse(description="Competition not found")
    },
    tags=["participants"]
)
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


@extend_schema(
    methods=["PUT"],
    summary="Update participant",
    description="Update a participant's details in a competition. Only the competition creator can update participants.",
    request=ParticipantSerializer,
    responses={
        201: OpenApiResponse(response=ParticipantSerializer, description="Participant updated successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
        403: OpenApiResponse(description="Not authorized to update participants"),
        404: OpenApiResponse(description="Competition or participant not found")
    },
    tags=["participants"]
)
@extend_schema(
    methods=["DELETE"],
    summary="Remove participant",
    description="Remove a participant from a competition. Competition creators can remove any participant, while participants can only remove themselves.",
    responses={
        202: OpenApiResponse(description="Participant removed successfully"),
        403: OpenApiResponse(description="Not authorized to remove this participant"),
        404: OpenApiResponse(description="Competition or participant not found")
    },
    tags=["participants"]
)
@api_view(["PUT", "DELETE"])
def update_delete_participants(request, competition_id, participant_id):
    try:
        competition = Competition.objects.get(id=competition_id)
    except Competition.DoesNotExist:
        raise NotFound('Competition not found.')
    

    if request.method == "DELETE":

        participant = Participant.objects.get(user=request.user, competition=competition_id)
        if request.user == competition.created_by or participant.id == participant_id:
            participant = Participant.objects.get(id=participant_id)
            participant.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            raise PermissionDenied("Only the owner or the user themselves can leave a competition.")

    elif request.method == "PUT":
        if request.user == competition.created_by:
            participant = Participant.objects.get(id=participant_id)
            serializer = ParticipantSerializer(participant, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied("You are not authorized to update participants")



@extend_schema(
    methods=["PUT"],
    summary="Update competition",
    description="Update an existing competition. Only the creator of the competition can update it.",
    request=CompetitionSerializer,
    responses={
        201: OpenApiResponse(response=CompetitionSerializer, description="Competition updated successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
        403: OpenApiResponse(description="Not authorized to update this competition"),
        404: OpenApiResponse(description="Competition not found")
    },
    tags=["competitions"]
)
@extend_schema(
    methods=["DELETE"],
    summary="Delete competition",
    description="Delete an existing competition. Only the creator of the competition can delete it.",
    responses={
        202: OpenApiResponse(description="Competition deleted successfully"),
        403: OpenApiResponse(description="Not authorized to delete this competition"),
        404: OpenApiResponse(description="Competition not found")
    },
    tags=["competitions"]
)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_delete_competition(request, competition_id):
    try:
        competition = Competition.objects.get(id=competition_id)
    except Competition.DoesNotExist:
        raise NotFound('Competition not found.')
    
    if request.method == "PUT":
        if request.user == competition.created_by:
            serializer = CompetitionSerializer(competition, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        raise PermissionDenied("You are not authorized to update competitions")  

    elif request.method == "DELETE":
        if request.user == competition.created_by:
            competition.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        raise PermissionDenied("You are not authorized to delete competitions")  

@extend_schema(
    methods=["GET"],
    summary="List competition matches",
    description="Retrieve a list of all matches for a specific competition. User must be the competition owner or a participant.",
    responses={
        200: OpenApiResponse(response=MatchSerializer(many=True), description="List of matches retrieved successfully"),
        403: OpenApiResponse(description="Not authorized to view these matches"),
        404: OpenApiResponse(description="Competition not found")
    },
    tags=["matches"]
)
@extend_schema(
    methods=["POST"],
    summary="Create competition match",
    description="Create a new match within a competition.",
    request=MatchSerializer,
    responses={
        201: OpenApiResponse(response=MatchSerializer, description="Match created successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
        403: OpenApiResponse(description="Not authorized to create matches"),
        404: OpenApiResponse(description="Competition not found")
    },
    tags=["matches"]
)
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

@extend_schema(
    methods=["GET"],
    summary="Get match details",
    description="Retrieve details for a specific match. User must be the competition owner or a participant.",
    responses={
        200: OpenApiResponse(response=MatchSerializer, description="Match details retrieved successfully"),
        403: OpenApiResponse(description="Not authorized to view this match"),
        404: OpenApiResponse(description="Match or competition not found")
    },
    tags=["matches"]
)
@extend_schema(
    methods=["PUT"],
    summary="Update match",
    description="Update an existing match. Only the competition owner can update matches.",
    request=MatchSerializer,
    responses={
        200: OpenApiResponse(response=MatchSerializer, description="Match updated successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
        403: OpenApiResponse(description="Not authorized to update matches"),
        404: OpenApiResponse(description="Match or competition not found")
    },
    tags=["matches"]
)
@extend_schema(
    methods=["DELETE"],
    summary="Delete match",
    description="Delete an existing match. Only the competition owner can delete matches.",
    responses={
        204: OpenApiResponse(description="Match deleted successfully"),
        403: OpenApiResponse(description="Not authorized to delete matches"),
        404: OpenApiResponse(description="Match or competition not found")
    },
    tags=["matches"]
)
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


@extend_schema(
    methods=["GET"],
    summary="Get participant statistics",
    description="Retrieve statistics for a specific participant. User must be the competition owner or a participant in the competition.",
    responses={
        200: OpenApiResponse(response=ParticipantStatsSerializer, description="Statistics retrieved successfully"),
        403: OpenApiResponse(description="Not authorized to view these statistics"),
        404: OpenApiResponse(description="Statistics or competition not found")
    },
    tags=["participants", "statistics"]
)
@extend_schema(
    methods=["PUT"],
    summary="Update participant statistics",
    description="Update statistics for a specific participant. User must be the competition owner or a participant in the competition.",
    request=ParticipantStatsSerializer,
    responses={
        200: OpenApiResponse(response=ParticipantStatsSerializer, description="Statistics updated successfully"),
        400: OpenApiResponse(description="Invalid data provided"),
        403: OpenApiResponse(description="Not authorized to update these statistics"),
        404: OpenApiResponse(description="Statistics or competition not found")
    },
    tags=["participants", "statistics"]
)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def get_stats_detail(request, id, competition_id):

    # check requester is in competition or owner
    if is_participant_or_owner(request.user, competition_id):
        stats = get_object_or_404(ParticipantStats, id=id)
        serializer = ParticipantStatsSerializer(stats)
        return Response(serializer.data, 200)
    raise PermissionDenied("You are not in the competition of this participant")


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


def is_participant_or_owner(request_id, competition_id):
    is_participant = Participant.objects.filter(user=request_id, competition=competition_id).exists()
    competition = get_object_or_404(Competition, id=competition_id)

    return is_participant or competition.created_by == request_id

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
