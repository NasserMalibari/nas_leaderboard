import django.contrib.auth
import django.contrib.auth.models
from django.db import models
from django.conf import settings
import django.contrib
from django.db.models import F

# Create your models here.
class Competition(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(django.contrib.auth.models.User, on_delete=models.CASCADE, related_name='competitions')

    def __str__(self):
        return self.name
    
class Participant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='participants')
    elo_rating = models.IntegerField(default=1200)

    class Meta:
        unique_together = ('user', 'competition')
    def __str__(self):
        return f"{self.user.username} in {self.competition.name}"

class Match(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='matches')
    participant1 = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='matches_as_p1')
    participant2 = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='matches_as_p2')
    WinnerChoices = models.TextChoices("WinnerChoices", ["1", "2", "draw", "not_played"])
    winner = models.CharField(
        max_length=20,
        choices=WinnerChoices.choices,
        default="not_played"
    )
    played_at = models.DateTimeField()
    participant1_elo_change = models.IntegerField(default=0)  # Elo change for participant1
    participant2_elo_change = models.IntegerField(default=0)  # Elo change for participant2


    def save(self, *args, **kwargs):
        # Check if the instance already exists in the database
        if self.pk is not None:
            previous_match = Match.objects.get(pk=self.pk)
            previous_winner = previous_match.winner
        else:
            previous_winner = "not_played"

        # Call the superclass save method to save the match
        super().save(*args, **kwargs)

        # Update Elo ratings if the match is played
        if self.winner != "not_played":
            self.update_elo_ratings(previous_winner)

        # If the winner has changed, update the participant stats
        if self.winner != previous_winner:
            self.update_participant_stats(previous_winner)

    def update_participant_stats(self, previous_winner):
        # Update stats based on the previous winner
        if previous_winner == "1":
            ParticipantStats.objects.filter(id=self.participant1_id).update(wins=F('wins') - 1)
            ParticipantStats.objects.filter(id=self.participant2_id).update(losses=F('losses') - 1)
        elif previous_winner == "2":
            ParticipantStats.objects.filter(id=self.participant2_id).update(wins=F('wins') - 1)
            ParticipantStats.objects.filter(id=self.participant1_id).update(losses=F('losses') - 1)
        elif previous_winner == "draw":
            ParticipantStats.objects.filter(id=self.participant1_id).update(draws=F('draws') - 1)
            ParticipantStats.objects.filter(id=self.participant2_id).update(draws=F('draws') - 1)

        # Update stats based on the new winner
        if self.winner == "1":
            ParticipantStats.objects.filter(id=self.participant1_id).update(wins=F('wins') + 1)
            ParticipantStats.objects.filter(id=self.participant2_id).update(losses=F('losses') + 1)
        elif self.winner == "2":
            ParticipantStats.objects.filter(id=self.participant2_id).update(wins=F('wins') + 1)
            ParticipantStats.objects.filter(id=self.participant1_id).update(losses=F('losses') + 1)
        elif self.winner == "draw":
            ParticipantStats.objects.filter(id=self.participant1_id).update(draws=F('draws') + 1)
            ParticipantStats.objects.filter(id=self.participant2_id).update(draws=F('draws') + 1)

        # Increment matches_played for both participants if the match is being marked as played
        if self.winner != "not_played" and previous_winner == "not_played":
            ParticipantStats.objects.filter(id=self.participant1_id).update(matches_played=F('matches_played') + 1)
            ParticipantStats.objects.filter(id=self.participant2_id).update(matches_played=F('matches_played') + 1)
        # Decrement matches_played for both participants if the match is being marked as not played
        # elif self.winner == "not_played" and previous_winner != "not_played":
            # ParticipantStats.objects.filter(id=self.participant1_id).update(matches_played=F('matches_played') - 1)
            # ParticipantStats.objects.filter(id=self.participant2_id).update(matches_played=F('matches_played') - 1)

    def update_elo_ratings(self, previous_winner):
        K = 32  # Elo K-factor

        # Reverse previous Elo changes if the winner has changed
        if previous_winner != "not_played":
            self.participant1.elo_rating -= self.participant1_elo_change
            self.participant2.elo_rating -= self.participant2_elo_change
            self.participant1.save()
            self.participant2.save()

        # Calculate new Elo changes
        rating1 = self.participant1.elo_rating
        rating2 = self.participant2.elo_rating

        expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
        expected2 = 1 / (1 + 10 ** ((rating1 - rating2) / 400))

        # Determine actual scores based on the winner
        if self.winner == "1":
            actual1, actual2 = 1, 0
        elif self.winner == "2":
            actual1, actual2 = 0, 1
        else:
            actual1, actual2 = 0.5, 0.5  # In case of a draw

        # Update Elo ratings
        self.participant1_elo_change = round(K * (actual1 - expected1))
        self.participant2_elo_change = round(K * (actual2 - expected2))

        self.participant1.elo_rating += self.participant1_elo_change
        self.participant2.elo_rating += self.participant2_elo_change

        # Save the new ratings and Elo changes
        self.participant1.save()
        self.participant2.save()
        Match.objects.filter(pk=self.pk).update(
            participant1_elo_change=self.participant1_elo_change,
            participant2_elo_change=self.participant2_elo_change
        )


    def __str__(self):
        return f"Match between {self.participant1.user.username} and {self.participant2.user.username} in {self.competition.name}"
    

class ParticipantStats(models.Model):
    id = models.OneToOneField(Participant, on_delete=models.CASCADE, primary_key=True)
    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    peak_elo = models.IntegerField(default=1200)

    def update_stats(self, result):
        if result == "win":
            self.wins += 1
        elif result == "loss":
            self.losses += 1
        elif result == "draw":
            self.draws += 1
        self.matches_played += 1
        self.save()

    def __str__(self):
        return f"Stats of participant: {self.id}"