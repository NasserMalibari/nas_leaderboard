from rest_framework import serializers
from api.models import Competition, Match, Participant, ParticipantStats
from django.contrib.auth import get_user_model


User = get_user_model()

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'name', 'created_at', 'created_by']
        extra_kwargs = {'created_by': {'read_only': True}}


class ParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'user', 'competition', 'username', 'elo_rating']
        read_only_fields = ['competition', 'user', 'elo_rating']

    def create(self, validated_data):
        # Extract the username and competition_id from the validated data
        username = validated_data.pop('username')
        # competition_id = validated_data.pop('competition_id')

        # Get the User instance based on the username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "User with this username does not exist."})

        competition = self.context['competition']
        # Create the Participant instance
        participant = Participant.objects.create(user=user, competition=competition, **validated_data)
        return participant

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'competition', 'participant1', 'participant2', 'winner', 'played_at', 'participant1_elo_change', 'participant2_elo_change']
        read_only_fields = ['competition']

    def validate(self, data):
        participant1 = data.get('participant1')
        participant2 = data.get('participant2')

        if participant1 is not None and participant2 is not None:
            if participant1 == participant2:

                raise serializers.ValidationError("Both participants must be different.")


        return data

    def create(self, validated_data):
        competition = self.context['competition']

        match = Match.objects.create(competition=competition, **validated_data)
        return match
    
    def update(self, instance, validated_data):
        if 'winner' in validated_data.keys():
            # print("UPDATE INSURANCE")
            # ensure winner is a participant
            if validated_data['winner'] not in ["1", "2", "draw", "not_played"]:
                raise serializers.ValidationError("winner should be one of 1, 2, draw, not_played")
        
        return super().update(instance, validated_data)

class ParticipantStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantStats
        fields = ['id', 'matches_played', 'wins', 'losses', 'draws', 'peak_elo']


# class MatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Match
#         fields = ['id', 'competition', 'participant1', 'participant2', 'winner', 'played_at']
#         read_only_fields = ['id']
    
#     def validate(self, data):
#         """
#         Custom validation to ensure:
#         - participant1 and participant2 are not the same.
#         - winner is either participant1 or participant2.
#         """
#         participant1 = data.get('participant1')
#         participant2 = data.get('participant2')
#         winner = data.get('winner')

#         if participant1 == participant2:
#             raise serializers.ValidationError("Participant 1 and Participant 2 cannot be the same.")

#         if winner and winner not in [participant1, participant2]:
#             raise serializers.ValidationError("The winner must be either Participant 1 or Participant 2.")