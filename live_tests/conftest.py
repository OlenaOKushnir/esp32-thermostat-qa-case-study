import pytest

def pytest_addoption(parser):
    parser.addoption('--serial-url',default='rfc2217://localhost:4001')
    parser.addoption('--capture-seconds',type=float,default=90)
    parser.addoption('--run-dir',required=True,help='New output directory for this live execution')
