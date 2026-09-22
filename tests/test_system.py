from io import BytesIO
import numpy as np
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pypdf import PdfWriter
from app.config import load_settings, Settings
from app.criteria import extract_criteria
from app.embedding import Embedder, EmbeddingError
from app.main import create_app
from app.parsing import parse_document, InputError
from app.schemas import AssessmentRequest
from app.scoring import assess

JD = 'Required qualifications:\nPython programming for backend services.'
RESUME = 'Developed backend services using Python and automated tests.'

class ExactEmbedder:
    """Deterministic stub for API/aggregation tests, NOT calibration."""
    model = None
    def embed(self, texts):
        return np.tile([1.,0.], (len(texts),1))

@pytest.fixture
def config():
    return load_settings()

@pytest.fixture
def client(config):
    return TestClient(create_app(config,ExactEmbedder()))

@pytest.mark.parametrize('field,value',[('resume',' ' * 30),('resume',3),('job_description','tiny')])
def test_request_validation(client,field,value):
    data = {'job_description':JD,'resume':RESUME,field:value}
    assert client.post('/assess',json=data).status_code == 422

def test_unknown_field(client):
    assert client.post('/assess',json={'job_description':JD,'resume':RESUME,'score':99}).status_code == 422

def test_assessment(client):
    response=client.post('/assess',json={'job_description':JD,'resume':RESUME})
    assert response.status_code == 200
    data=response.json()
    assert data['overall_score']==100
    assert data['criteria'][0]['evidence'][0]['text']==RESUME
    assert data['human_review_required'] is True

def test_txt_upload(client):
    response=client.post('/assess/files',files={'job_description':('jd.txt',JD),'resume':('r.txt',RESUME)})
    assert response.status_code == 200

@pytest.mark.parametrize('name,data,status',[('r.txt',b'',422),('r.txt',b'\xff'*40,422),('r.pdf',b'%PDF-broken',422),('r.docx',b'content',415)])
def test_bad_upload(client,name,data,status):
    r=client.post('/assess/files',files={'job_description':('jd.txt',JD),'resume':(name,data)})
    assert r.status_code==status

def test_scanned_pdf(client):
    writer=PdfWriter(); writer.add_blank_page(width=200,height=200)
    stream=BytesIO(); writer.write(stream)
    r=client.post('/assess/files',files={'job_description':('jd.txt',JD),'resume':('blank.pdf',stream.getvalue())})
    assert r.status_code==422
    assert 'OCR' in r.json()['detail']

def test_size_limit(config):
    config.max_file_bytes=10
    with pytest.raises(InputError) as error:
        parse_document('r.txt',b'A'*11,config)
    assert error.value.status==413

@pytest.mark.parametrize('patch',[{'chunk_overlap':64},{'similarity_floor':1.0},{'weights':{'skills':1}},{'review_threshold':90}])
def test_config_validation(config,patch):
    with pytest.raises(ValidationError):
        Settings.model_validate(config.model_dump() | patch)

def test_extraction(config):
    criteria=extract_criteria('Requirements:\n3 years of Python experience.\nPreferred qualifications:\nDocker container packaging.',config)
    assert criteria[0].category=='experience'
    assert criteria[1].importance=='preferred'

def test_embedding_failure_returns_503(config):
    class Broken:
        def embed(self,texts):
            raise EmbeddingError('Embedding unavailable')
    r=TestClient(create_app(config,Broken())).post('/assess',json={'job_description':JD,'resume':RESUME})
    assert r.status_code==503
    assert r.json()['error']=='embedding_unavailable'

def test_invalid_embedding_output(config):
    class BadModel:
        def embed(self,texts,**kwargs):
            return [[float('nan'),0]]*len(texts)
    engine=Embedder(config); engine.model=BadModel()
    with pytest.raises(EmbeddingError):
        engine.embed(['hello'])

def test_negation_cap(config):
    report=assess(AssessmentRequest(job_description=JD,resume='I have no experience with Python backend services.'),config,ExactEmbedder())
    assert report.overall_score==config.negation_score_cap

def test_weighted_aggregation(config):
    class DifferentScores:
        def embed(self,texts):
            return np.array([[1.,0.],[0.,1.],[1.,0.]])
    request=AssessmentRequest(job_description='Requirements:\nPython programming for backend services.\nBachelor degree in computer science.',resume=RESUME)
    report=assess(request,config,DifferentScores())
    assert report.overall_score==60 # (100 * 3 + 0 * 2) / 5
    config.weights['education']=3
    assert assess(request,config,DifferentScores()).overall_score==33.33

def text_pdf(text):
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    writer=PdfWriter(); page=writer.add_blank_page(width=595,height=842)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
    stream=DecodedStreamObject(); stream.set_data(f'BT /F1 12 Tf 50 750 Td ({text}) Tj ET'.encode())
    page[NameObject('/Contents')]=writer._add_object(stream)
    output=BytesIO(); writer.write(output)
    return output.getvalue()

def test_both_inputs_as_pdf(client):
    r=client.post('/assess/files',files={'job_description':('jd.pdf',text_pdf('Python programming for backend services.')),'resume':('r.pdf',text_pdf(RESUME))})
    assert r.status_code==200
    assert 'Python' in r.json()['criteria'][0]['evidence'][0]['text']

def test_encrypted_pdf(config):
    writer=PdfWriter(); writer.add_blank_page(width=100,height=100); writer.encrypt('secret')
    data=BytesIO(); writer.write(data)
    with pytest.raises(InputError,match='Encrypted'):
        parse_document('encrypted.pdf',data.getvalue(),config)

def test_duplicate_lines_and_order(config):
    request=AssessmentRequest(job_description=JD,resume=RESUME+'\n'+RESUME)
    result=assess(request,config,ExactEmbedder())
    assert result.metadata['resume_chunks']==1
    assert result.overall_score==100
