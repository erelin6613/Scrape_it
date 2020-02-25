

class Business:

	def __init__(self, url, company_name=None, category=None, 
				country=None):

		self.url = url
		self.company_name = company_name
		self.country = country
		self.category = category
		self.contact_link = None
		self.phones = None
		self.address = None
		self.state = None
		self.county = None
		self.city = None
		self.street = None
		self.house_number = None
		self.zip = None
		self.district = None
		self.email = None
		self.facebook = None
		self.instagram = None
		self.linkedin = None
		self.pinterest = None
		self.twitter = None
		self.youtube = None
		self.faq_link = None
		self.privacy_link = None
		self.return_link = None
		self.shipping_link = None
		self.terms_link = None
		self.warranty_link = None
		self.faq_text = None
		self.privacy_text = None
		self.return_text = None
		self.shipping_text = None
		self.terms_text = None
		self.warranty_text = None


	def __repr__(self):
		return f'Business("{self.url}", "{self.company_name}", "{self.country}",\
			 "{self.category}", "{self.contact_link}", "{self.phones}", \
			 "{self.address}, "{self.state}", "{self.county}", "{self.city}",\
			 "{self.street}", "{self.house_number}", "{self.zip}", "{self.district}",\
			 "{self.email}", "{self.facebook}", "{self.instagram}", \
			 "{self.linkedin}", "{self.pinterest}", "{self.twitter}",\
			 "{self.youtube}", "{self.faq_link}", "{self.privacy_link}",\
			 "{self.return_link}", "{self.shipping_link}", "{self.terms_link}",\
			 "{self.warranty_link}", "{self.faq_text}", "{self.privacy_text}",\
			 "{self.return_text}", "{self.shipping_text}", "{self.terms_text}",\
			 "{self.warranty_text}")'



