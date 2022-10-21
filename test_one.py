import main
import urllib.request
import urllib.parse



# custom class to be the mock return value
# will override the requests.Response returned from requests.get
class MockResponse:

    # mock json() method always returns a specific testing dictionary
    status = "007"
    reason = "Testing"
    url = "http://test.address"
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @staticmethod
    def getheader(no_param):
        return 'rel, <http://nothing.com?page=100>; rel="last"'

    @staticmethod
    def getheaders():
        return "No headers"

    @staticmethod
    def read():
        return '[{ "item" : 1, "title": "Test" },{ "item" : 2, "title": "Test2" }]'.encode('utf-8')

def test_download_issues(monkeypatch):
    # Any arguments may be passed and mock_get() will always return our
    # mocked object, which only has the .json() method.
    def mock_get(*args, **kwargs):
        return MockResponse()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(urllib.request, "urlopen", mock_get)

    # app.get_json, which contains requests.get, uses the monkeypatch
    test_obj = main.GithubRepo("a","b")
    test_obj.download_issues_all()
    result = test_obj.issues_all
    assert len(result) == 200

