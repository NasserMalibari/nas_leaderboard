from django.contrib import admin
from .models import Competition, Participant, Match, ParticipantStats


admin.site.register(Competition)
admin.site.register(Participant)
admin.site.register(Match)
admin.site.register(ParticipantStats)