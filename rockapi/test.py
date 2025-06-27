# Create your tests here.

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rockapi.models import Rock, Type  # Update this import path as needed


class RockViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(
            username='user1', password='pass')
        self.user2 = User.objects.create_user(
            username='user2', password='pass')

        # Tokens for authentication
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        # Create a rock type
        self.rock_type = Type.objects.create(label='Granite')

        # Create a rock owned by user1
        self.rock = Rock.objects.create(
            name='Big Rock',
            weight=42.0,
            user=self.user1,
            type=self.rock_type
        )

    def test_destroy_own_rock(self):
        """User can delete their own rock"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.delete(f'/rocks/{self.rock.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rock.objects.filter(id=self.rock.id).exists())

    def test_destroy_others_rock(self):
        """User cannot delete another user's rock"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        response = self.client.delete(f'/rocks/{self.rock.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Rock.objects.filter(id=self.rock.id).exists())

    def test_destroy_nonexistent_rock(self):
        """Returns 404 when trying to delete non-existent rock"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.delete('/rocks/9999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_rock(self):
        """User can create a new rock"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        payload = {
            'name': 'Tiny Pebble',
            'weight': 2.3,
            'typeId': self.rock_type.id
        }
        response = self.client.post('/rocks', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rock.objects.count(), 2)
        self.assertEqual(Rock.objects.last().name, 'Tiny Pebble')

    def test_list_all_rocks(self):
        """User can list all rocks"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get('/rocks')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_owned_rocks_only(self):
        """Filter rocks by current user's ownership"""
        # Add another rock owned by user2
        Rock.objects.create(
            name='Lunar Rock',
            weight=3.5,
            user=self.user2,
            type=self.rock_type
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        response = self.client.get('/rocks?owner=current')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Lunar Rock')
