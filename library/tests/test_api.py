from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.test.client import Client
from library_app.models import Genre, Book, Author
from json import dumps


class ViewSetsTests(TestCase):
    pages = (
        (Genre, '/rest/Genre/', {'name': 'genre'}, {'description': 'description'}),
        (Book, '/rest/Book/', {'title': 'book', 'type': 'book'}, {'description': 'description'}),
        (Author, '/rest/Author/', {'full_name': 'name'}, {'full_name': 'new_name'}),
    )

    def setUp(self):
        self.client = Client()
        self.creds_superuser = {'username': 'super', 'password': 'super'}
        self.creds_user = {'username': 'default', 'password': 'default'}
        self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
        self.user = User.objects.create_user(**self.creds_user)

    def test_get(self):
        # logging in with superuser creds
        self.client.login(**self.creds_user)
        # GET
        for _, url, _, _ in self.pages:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # logging out
        self.client.logout()

    def test_manage_superuser(self):
        # logging in with superuser creds
        self.client.login(**self.creds_superuser)
        for cls_model, url, data, to_change in self.pages:
            # POST
            resp_post = self.client.post(url, data=data)
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
            # PUT
            created_id = cls_model.objects.get(**data).id
            resp_put = self.client.put(
                f'{url}?id={created_id}', 
                data=dumps(to_change)
            )
            self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
            attr, value = list(to_change.items())[0]
            self.assertEqual(getattr(cls_model.objects.get(id=created_id), attr), value)
            # DELETE EXISTING
            resp_delete = self.client.delete(f'{url}?id={created_id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
            # DELETE NONEXISTENT
            repeating_delete = self.client.delete(f'{url}?id={created_id}')
            self.assertEqual(repeating_delete.status_code, status.HTTP_404_NOT_FOUND)

        # logging out
        self.client.logout()

    def test_manage_user(self):
        # logging in with superuser creds
        self.client.login(**self.creds_user)
        for cls_model, url, data, to_change in self.pages:
            # POST
            resp_post = self.client.post(url, data=data)
            self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)
            # PUT
            created = cls_model.objects.create(**data)
            resp_put = self.client.put(
                f'{url}?id={created.id}', 
                data=dumps(to_change)
            )
            self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)
            # DELETE EXISTING
            resp_delete = self.client.delete(f'{url}?id={created.id}')
            self.assertEqual(resp_delete.status_code, status.HTTP_403_FORBIDDEN)
            # clean up
            created.delete()
        # logging out
        self.client.logout()