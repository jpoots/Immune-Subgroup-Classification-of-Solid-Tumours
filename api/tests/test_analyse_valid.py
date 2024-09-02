import os
import sys

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
# https://stackoverflow.com/questions/22736850/flask-module-import-failure-from-test-folder/22737042#22737042

from app import create_app

app = create_app()


def test_get_genes():
    response = app.test_client().get("/genelist")
    print(response)
    assert response.status_code == 200
