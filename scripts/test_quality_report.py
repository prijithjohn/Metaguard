import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'metaguard_project.settings'
import django
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

django.setup()
client = Client()
content = b'email,age\nnot-an-email,30\nvalid@example.com,40\n'
upload = SimpleUploadedFile('quality_sample.csv', content, content_type='text/csv')
response = client.post('/datasets/upload/', {'name': 'Quality Dataset', 'file': upload}, follow=True)
print('Upload status:', response.status_code)
print('Redirect chain:', response.redirect_chain)
print('Success message present:', 'Dataset uploaded successfully.' in response.content.decode())
response = client.get('/datasets/history/')
print('History status:', response.status_code)
if 'Quality Dataset' in response.content.decode():
    print('Dataset present in history')
# Use dataset ID from created dataset record
from datasets.models import Dataset
latest = Dataset.objects.filter(name='Quality Dataset').order_by('-uploaded_at').first()
if not latest:
    print('No dataset record found')
    sys.exit(1)
path = f'/datasets/{latest.id}/quality/'
print('Quality detail path:', path)
quality_response = client.get(path)
print('Quality detail status:', quality_response.status_code)
text = quality_response.content.decode()
print('Contains Quality score:', 'Quality score' in text)
print('Contains invalid email records:', 'Invalid email records' in text)
print('Contains 1 invalid record:', '1' in text)
