from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

c = Client()
csv = SimpleUploadedFile('test.csv', b'name,email\nA,a@b.com\n', content_type='text/csv')
r = c.post('/datasets/upload/', {'name': 'Test CSV', 'file': csv})
print('CSV upload status', r.status_code)

jsonf = SimpleUploadedFile('test.json', b'[{"name":"A","email":"a@b.com"}]', content_type='application/json')
r2 = c.post('/datasets/upload/', {'name': 'Test JSON', 'file': jsonf})
print('JSON upload status', r2.status_code)
