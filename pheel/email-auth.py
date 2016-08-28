from django.contrib.auth.models import User
import re

email_re = re.compile(
						r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
						r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
						r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'
						r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE
					)

class BasicBackend:
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None

class EmailBackend(BasicBackend):
	def authenticate(self, username=None, password=None):
		#If username is an email address, then try to pull it up
		if email_re.search(username):
			try:
				user = User.objects.get(email=username)
			except User.DoesNotExist:
				return None
		else:
			#We have a non-email address username we should try username
			try:
				user = User.objects.get(username=username)
			except User.DoesNotExist:
				return None
		if user.check_password(password):
			return user
