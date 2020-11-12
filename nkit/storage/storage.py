import uuid
class Storage:
	def get_latest_hash(self):
		return uuid.uuid4().hex
