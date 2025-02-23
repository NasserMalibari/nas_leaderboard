import django.contrib.auth
import django.contrib.auth.models
from django.db import models
from django.conf import settings
import django.contrib

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

    def save(self, *args, **kwargs):
        if self.winner != "not_played":
            self.update_elo_ratings()
        super().save(*args, **kwargs)

    def update_elo_ratings(self):
        K = 32  # Elo K-factor

        rating1 = self.participant1.elo_rating
        rating2 = self.participant2.elo_rating

        expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
        expected2 = 1 / (1 + 10 ** ((rating1 - rating2) / 400))


        # Determine actual scores based on the winner
        if self.winner == "1":
            print("ELO UPDATING")
            actual1, actual2 = 1, 0
        elif self.winner == "2":
            print("ELO UPDATING")
            actual1, actual2 = 0, 1
        else:
            actual1, actual2 = 0.5, 0.5  # In case of a draw

        # Update Elo ratings
        new_rating1 = rating1 + K * (actual1 - expected1)
        new_rating2 = rating2 + K * (actual2 - expected2)

        # Save the new ratings
        self.participant1.elo_rating = new_rating1
        self.participant2.elo_rating = new_rating2
        self.participant1.save()
        self.participant2.save()

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