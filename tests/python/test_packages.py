import json
import packagist, packages


def test_get_repository_link_converts_to_ssh(monkeypatch):
    def fake_get(url):
        class Resp:
            def json(self):
                return {
                    'packages': {
                        'pkg/name': [{
                            'source': {'url': 'https://github.com/Org/Repo'}
                        }]
                    }
                }
        return Resp()
    monkeypatch.setattr(packagist.requests, 'get', fake_get)
    url = packagist.get_repository_link('pkg/name')
    assert url == 'git@github.com:Org/Repo.git'


def test_read_packages(tmp_path):
    data = {'packages': {'p1': 'a', 'p2': 'b'}}
    file = tmp_path / 'packages.json'
    file.write_text(json.dumps(data))
    assert packages.read_packages(file) == data['packages']
