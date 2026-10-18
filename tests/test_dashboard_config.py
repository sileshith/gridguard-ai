import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).resolve().parents[1]/'scripts/build_dashboard.py'
spec=importlib.util.spec_from_file_location('dashboard_build',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_empty_gpt_url():assert m.safe_gpt_url('')==''

def test_approved_gpt_url():assert m.safe_gpt_url('https://chatgpt.com/g/g-example')=='https://chatgpt.com/g/g-example'

@pytest.mark.parametrize('url',['javascript:alert(1)','http://chatgpt.com/g/g-example','https://chatgpt.com.evil.invalid/g/g-example','https://user:password@chatgpt.com/g/g-example','https://chatgpt.com/g/g-example?token=example','https://chatgpt.com/g/g-example#secret','https://other.invalid/g/g-example'])
def test_invalid_gpt_urls(url):
    with pytest.raises(ValueError):m.safe_gpt_url(url)
