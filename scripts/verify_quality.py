import os
import sys
import traceback

# Initialize Django environment from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metaguard_project.settings')

import django
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from datasets.services import DatasetImportService

csv_content = b'email,name,age\nuser@example.com,Alice,30\nbad-email,Bob,45\n,Charlie,25\n'
file = SimpleUploadedFile('test.csv', csv_content, content_type='text/csv')

try:
    DatasetImportService.import_dataset('Test Dataset', file)
    client = Client()
    history_response = client.get('/datasets/history/')
    print('history status', history_response.status_code, 'has dataset row', b'Test Dataset' in history_response.content)
    from datasets.models import Dataset
    from quality.models import QualityReport
    from governance.models import SensitiveDataReport

    dataset = Dataset.objects.filter(name='Test Dataset').first()
    print('quality exists', QualityReport.objects.filter(dataset=dataset).exists())
    print('sensitive exists', SensitiveDataReport.objects.filter(dataset=dataset).exists())
    quality_response = client.get(f'/datasets/{dataset.id}/quality/')
    sensitive_response = client.get(f'/datasets/{dataset.id}/sensitive/')
    print('quality status', quality_response.status_code)
    print('sensitive status', sensitive_response.status_code)
except Exception:
    traceback.print_exc()
