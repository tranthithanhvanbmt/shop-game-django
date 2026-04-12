from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from shop_game.shop.forms import GameCategoryForm
from shop_game.shop.models import AccountInventory, GameCategory


class SellerImageUrlFlowTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='seller01',
			password='StrongPass@123',
			is_seller=True,
		)
		self.category = GameCategory.objects.create(
			name='Free Fire',
			slug='free-fire',
			is_active=True,
		)

	def test_create_account_uses_image_url_when_no_uploaded_file(self):
		self.client.login(username='seller01', password='StrongPass@123')
		created_file = SimpleUploadedFile('thumb.jpg', b'fake-image-bytes', content_type='image/jpeg')

		with patch('shop_game.shop.views.download_image_from_url', return_value=created_file) as mocked_download:
			response = self.client.post(
				reverse('seller_create_account'),
				{
					'category_id': self.category.id,
					'username': 'acc_01',
					'password': 'pw_01',
					'login_method': 'Garena',
					'price': '100000',
					'rank': 'KC',
					'details': 'Test details',
					'image_thumb_url': 'https://example.com/thumb.jpg',
					'image_1_url': '',
					'image_2_url': '',
				},
				follow=True,
			)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(AccountInventory.objects.count(), 1)
		created = AccountInventory.objects.first()
		self.assertTrue(bool(created.image_thumb))
		mocked_download.assert_called_once()

	def test_validate_image_url_endpoint_returns_success(self):
		self.client.login(username='seller01', password='StrongPass@123')
		valid_file = SimpleUploadedFile('ok.jpg', b'abc123', content_type='image/jpeg')

		with patch('shop_game.shop.views.download_image_from_url', return_value=valid_file):
			response = self.client.post(
				reverse('seller_validate_image_url'),
				{
					'image_url': 'https://example.com/ok.jpg',
					'field_label': 'Ảnh bìa',
				},
			)

		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertTrue(payload.get('ok'))

	def test_validate_image_url_endpoint_returns_error_on_invalid_link(self):
		self.client.login(username='seller01', password='StrongPass@123')

		with patch('shop_game.shop.views.download_image_from_url', side_effect=ValidationError('bad-link')):
			response = self.client.post(
				reverse('seller_validate_image_url'),
				{
					'image_url': 'https://example.com/not-image.txt',
					'field_label': 'Ảnh bìa',
				},
			)

		self.assertEqual(response.status_code, 400)
		payload = response.json()
		self.assertFalse(payload.get('ok'))


class GameCategoryFormImageUrlTests(TestCase):
	def test_image_url_populates_image_field(self):
		uploaded = SimpleUploadedFile('category.png', b'png-bytes', content_type='image/png')
		with patch('shop_game.shop.forms.download_image_from_url', return_value=uploaded) as mocked_download:
			form = GameCategoryForm(
				data={
					'name': 'Lien Quan',
					'slug': 'lien-quan',
					'description': 'abc',
					'is_active': True,
					'image_url': 'https://example.com/cat.png',
				},
				files={},
			)
			self.assertTrue(form.is_valid(), form.errors)
			self.assertEqual(form.cleaned_data['image'], uploaded)
			mocked_download.assert_called_once()
