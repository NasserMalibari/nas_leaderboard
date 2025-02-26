from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Competition, Participant, Match
from django.utils import timezone

User = get_user_model()

class CompetitionTests(APITestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create some competitions for testing
        Competition.objects.create(name='Competition 1', created_by=self.user)
        Competition.objects.create(name='Competition 2', created_by=self.user)
        Competition.objects.create(name='Competition 3', created_by=self.other_user)

    def test_list_competitions_authenticated(self):
        """
        Ensure we can list competitions created by the authenticated user.
        """
        url = reverse('list_create_competition')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only 2 competitions belong to the authenticated user

    def test_create_competition_authenticated(self):
        """
        Ensure we can create a new competition.
        """
        url = reverse('list_create_competition')
        data = {'name': 'New Competition'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Competition.objects.count(), 4)  # Initial 3 + 1 new competition
        self.assertEqual(Competition.objects.get(id=response.data['id']).created_by, self.user)

    def test_create_competition_unauthenticated(self):
        """
        Ensure that unauthenticated users cannot create competitions.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('list_create_competition')
        data = {'name': 'New Competition'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_competitions_unauthenticated(self):
        """
        Ensure that unauthenticated users cannot list competitions.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('list_create_competition')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_competition_invalid_data(self):
        """
        Ensure that competitions cannot be created with invalid data.
        """
        url = reverse('list_create_competition')
        data = {'name': ''}  # Invalid data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Competition.objects.count(), 3)  # No new competition should be created

class ParticipantTests(APITestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')

        # Generate JWT token for user1
        refresh = RefreshToken.for_user(self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a competition
        self.competition = Competition.objects.create(name='Test Competition', created_by=self.user1)

        # Create some participants for testing
        Participant.objects.create(user=self.user1, competition=self.competition)
        Participant.objects.create(user=self.user2, competition=self.competition)

    def test_list_participants(self):
        """
        Ensure participants can be listed for a specific competition.
        """
        url = reverse('participant_list_create', args=[self.competition.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two participants were created in setUp

    def test_add_participant(self):
        """
        Ensure a participant can be added to a competition.
        """
        url = reverse('participant_list_create', args=[self.competition.id])
        data = {'username': 'user3'}
        response = self.client.post(url, data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check there are 3 participants
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3) 

        self.assertEqual(Participant.objects.count(), 3)

    def test_add_participant_invalid_username(self):
        """
        Ensure adding a participant with a non-existent username fails.
        """
        url = reverse('participant_list_create', args=[self.competition.id])
        data = {'username': 'nonexistentuser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)  # Error message for invalid username

    def test_add_participant_unauthenticated(self):
        """
        Ensure unauthenticated users cannot add participants.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('participant_list_create', args=[self.competition.id])
        data = {'username': 'user2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_participants_unauthenticated(self):
        """
        Ensure unauthenticated users cannot list participants.
        """
        self.client.credentials()  # Remove authentication
        url = reverse('participant_list_create', args=[self.competition.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_participant_to_nonexistent_competition(self):
        """
        Ensure adding a participant to a non-existent competition fails.
        """
        nonexistent_competition_id = 999  # Assuming no competition with this ID exists
        url = reverse('participant_list_create', args=[nonexistent_competition_id])
        data = {'username': 'user2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MatchTests(APITestCase):
    def setUp(self):
        # create some users
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        refresh2 = RefreshToken.for_user(self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh2.access_token}')

        # create some competitions
        self.comp1 = Competition.objects.create(name='Competition 1', created_by=self.user1)
        self.comp2 = Competition.objects.create(name='Competition 2', created_by=self.user2)

        # create some participants
        self.part1_1 = Participant.objects.create(user=self.user1, competition=self.comp1)
        self.part2_1 = Participant.objects.create(user=self.user2, competition=self.comp1)
        self.part3_1 = Participant.objects.create(user=self.user3, competition=self.comp1)
        self.part3_2 = Participant.objects.create(user=self.user3, competition=self.comp2)

        played_at = timezone.make_aware(timezone.datetime(2023, 10, 1, 14, 0, 0))
        # set up matches
        Match.objects.create(competition=self.comp1, participant1=self.part1_1, participant2=self.part2_1,
                             played_at=played_at)

    def test_list_matches(self):
        url = '/api/competitions/1/matches/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        url = '/api/competitions/2/matches/'
        response = self.client2.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_post_matches(self):
        url = '/api/competitions/1/matches/'

        played_at = timezone.make_aware(timezone.datetime(2023, 10, 1, 14, 0, 0))
        data = {'participant1': 1, 'participant2': 2,
                'played_at': played_at
                }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check there are 2 matches
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_matches_not_in_comp(self):
        url = '/api/competitions/2/matches/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_post_match_non_exostant_comp(self):
        url = '/api/competitions/10/matches/'

        response = self.client.get(url)
        # should this be 404 or something else? 400?
        self.assertEqual(response.status_code, 404)
        
class UpdateMatchTests(APITestCase):
    def setUp(self):
        # create some users
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        refresh2 = RefreshToken.for_user(self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh2.access_token}')

        # create some competitions
        self.comp1 = Competition.objects.create(name='Competition 1', created_by=self.user1)
        self.comp2 = Competition.objects.create(name='Competition 2', created_by=self.user2)

        # create some participants
        self.part1_1 = Participant.objects.create(user=self.user1, competition=self.comp1)
        self.part2_1 = Participant.objects.create(user=self.user2, competition=self.comp1)
        self.part3_1 = Participant.objects.create(user=self.user3, competition=self.comp1)
        self.part3_2 = Participant.objects.create(user=self.user3, competition=self.comp2)

        played_at = timezone.make_aware(timezone.datetime(2023, 10, 1, 14, 0, 0))
        # set up matches
        Match.objects.create(competition=self.comp1, participant1=self.part1_1, participant2=self.part2_1,
                             played_at=played_at)
        Match.objects.create(competition=self.comp1, participant1=self.part3_1, participant2=self.part2_1,
                             played_at=played_at)

        Match.objects.create(competition=self.comp1, participant1=self.part2_1, participant2=self.part3_1,
                             played_at=played_at)
    
    def test_update_winner(self):
        url = '/api/competitions/1/matches/1/'
        data = {'winner': "1"}

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        url = '/api/competitions/1/participants/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


        # check elo has increased for 1 and decreased for 2
        p1 = Participant.objects.get(user=1)
        self.assertGreater(p1.elo_rating, 1200)

        p2 = Participant.objects.get(user=2)
        self.assertLess(p2.elo_rating, 1200)

    def test_delete(self):
        url = '/api/competitions/1/matches/1/'
        # data = {'winner': 1}

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        
        url = '/api/competitions/1/matches/'
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)


    def test_non_owner_update(self):
        url = '/api/competitions/1/matches/1/'
        data = {'winner': 2}

        response = self.client2.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_non_owner_delete(self):
        url = '/api/competitions/1/matches/1/'
        # data = {'winner': 1}

        response = self.client2.delete(url)
        self.assertNotEqual(response.status_code, 204)

    def test_get_match(self):
        url = '/api/competitions/1/matches/1/'
        # data = {'winner': 1}

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_change_winner(self):
        url = '/api/competitions/1/matches/1/'
        data = {'winner': "1"}

        self.client.put(url, data, format='json')

        data = {'winner': "2"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # check elo calcs were reversed
        p1 = Participant.objects.get(user=1)
        self.assertLess(p1.elo_rating, 1200)

        p2 = Participant.objects.get(user=2)
        self.assertGreater(p2.elo_rating, 1200)

        # now change to draw
        data = {'winner': "draw"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # check elo calcs were reversed
        p1 = Participant.objects.get(user=1)
        self.assertEqual(p1.elo_rating, 1200)

        p2 = Participant.objects.get(user=2)
        self.assertEqual(p2.elo_rating, 1200)
        # print(p1.elo_rating, p2.elo_rating)
    
class ParticipantStatsTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='testpass123')
        self.user2 = User.objects.create_user(username='otheruser', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')


        refresh2 = RefreshToken.for_user(self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh2.access_token}')

        refresh3 = RefreshToken.for_user(self.user3)
        self.client3 = APIClient()
        self.client3.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh3.access_token}')

        # Create some competitions for testing
        self.comp1 = Competition.objects.create(name='Competition 1', created_by=self.user1)

        self.part1_1 = Participant.objects.create(user=self.user1, competition=self.comp1)
        self.part2_1 = Participant.objects.create(user=self.user2, competition=self.comp1)


    def test_stats_created(self):
        url = '/api/competitions/1/stats/1/'

        # stats wasnt specifically invoked, but should be created automatically when 
        # participants are created
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
    
    def test_stats_detail_diff_user(self):
        """
            Different users in comp should see others' stats
        """
        url = '/api/competitions/1/stats/1/'

        resp = self.client2.get(url)

        self.assertEqual(resp.status_code, 200)

    def test_stats_detail_not_in_comp(self):
        """
            Permission denied for users not in the competition
        """
        url = '/api/competitions/1/stats/1/'

        resp = self.client3.get(url)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_matches_updates_stats(self):
        # create matches 
        played_at = timezone.make_aware(timezone.datetime(2023, 10, 1, 14, 0, 0))
        # set up matches
        Match.objects.create(competition=self.comp1, participant1=self.part1_1, participant2=self.part2_1,
                             played_at=played_at)
        
        self.client.put('/api/competitions/1/matches/1/', {'winner': "1"}, format='json')

        url = '/api/competitions/1/stats/1/'
        resp = self.client.get(url)
        self.assertEqual(resp.data['matches_played'], 1)
        self.assertEqual(resp.data['wins'], 1)



class UpdateDeleteParticipants(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        refresh2 = RefreshToken.for_user(self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh2.access_token}')

        # create some competitions
        self.comp1 = Competition.objects.create(name='Competition 1', created_by=self.user1)
        self.comp2 = Competition.objects.create(name='Competition 2', created_by=self.user2)

        # create some participants
        self.part1_1 = Participant.objects.create(user=self.user1, competition=self.comp1)
        self.part2_1 = Participant.objects.create(user=self.user2, competition=self.comp1)
        self.part3_1 = Participant.objects.create(user=self.user3, competition=self.comp1)
        self.part3_2 = Participant.objects.create(user=self.user3, competition=self.comp2)
    
    def test_delete_participant_as_owner(self):
        url = '/api/competitions/1/participants/2/'

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        objs = Participant.objects.all()
        self.assertEqual(len(objs), 3)

    def test_delete_participant_self(self):
        url = '/api/competitions/1/participants/2/'

        resp = self.client2.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        objs = Participant.objects.all()
        self.assertEqual(len(objs), 3)

    def test_delete_participant_other_user(self):
        url = '/api/competitions/1/participants/1/'

        resp = self.client2.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_participant(self):
        url = '/api/competitions/1/participants/1/'
        data = {'elo_rating': 2000}
        resp = self.client.put(url, data=data, format='json')

        self.assertEqual(resp.status_code, 201)
    
    def test_update_participant_non_owner(self):
        url = '/api/competitions/1/participants/1/'
        data = {'elo_rating': 2000}
        resp = self.client2.put(url, data=data, format='json')

        self.assertEqual(resp.status_code, 403)

class UpdateDeleteCompetitions(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user1)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        refresh2 = RefreshToken.for_user(self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh2.access_token}')

        # create some competitions
        self.comp1 = Competition.objects.create(name='Competition 1', created_by=self.user1)
        self.comp2 = Competition.objects.create(name='Competition 2', created_by=self.user2)

        # create some participants
        self.part1_1 = Participant.objects.create(user=self.user1, competition=self.comp1)
        self.part2_1 = Participant.objects.create(user=self.user2, competition=self.comp1)
        self.part3_1 = Participant.objects.create(user=self.user3, competition=self.comp1)
        self.part3_2 = Participant.objects.create(user=self.user3, competition=self.comp2)
    

    def test_delete_competition(self):
        url = '/api/competitions/1/'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

    def test_delete_competition_non_owner(self):
        url = '/api/competitions/1/'
        resp = self.client2.delete(url)
        self.assertEqual(resp.status_code, 403)

    def test_competition_update(self):
        url = '/api/competitions/1/'
        data = {'title': 'new name'}
        resp = self.client.put(url, data=data)
        self.assertEqual(resp.status_code, 201)

    def test_competition_update_non_owner(self):
        url = '/api/competitions/1/'
        data = {'title': 'new name'}
        resp = self.client2.put(url, data=data)
        self.assertEqual(resp.status_code, 403)


