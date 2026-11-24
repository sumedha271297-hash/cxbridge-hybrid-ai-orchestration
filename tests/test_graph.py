import pytest
from core import build_graph
@pytest.mark.parametrize('msg,expected',[('login','internal'),('fee','internal'),('fraud','human')])
def test_graph(msg,expected):
    assert build_graph().invoke({'messages':[msg]})['route']==expected
