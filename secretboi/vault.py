import json
import os

from . import log
from . import rest

logger = log.make_logger(__name__)


class Client:
    @classmethod
    def from_config(cls, config):
        return cls(
            addr=config.vault_addr,
            role=config.vault_role,
            jwt_path=config.kubernetes_token_path,
            paths=config.paths,
            secrets_dir=config.secrets_directory,
            recurse_secrets=config.recurse_secrets
        )

    def __init__(self, addr='', role='', jwt_path='', paths={}, secrets_dir='', recurse_secrets=False):
        logger.info('creating client for vault %s using role %s', addr, role)
        self.token = None

        if not addr.endswith('/'):
            addr += '/'

        self.addr = addr
        self.role = role
        self.paths = paths
        self.jwt_path = jwt_path
        self.secrets_dir = secrets_dir
        self.recurse_secrets = recurse_secrets

    @property
    def jwt_token(self):
        logger.info('reading JWT token from %s', self.jwt_path)
        with open(self.jwt_path) as f:
            return f.read().strip()

    @property
    def token_destination(self):
        return os.path.join(self.secrets_dir, 'token')

    def write_token(self):
        logger.info('writing vault token to %s', self.token_destination)
        with open(self.token_destination, 'w') as f:
            f.write(self.token)

    def path(self, relpath):
        if relpath.startswith('/'):
            relpath = relpath[1:]
        return self.addr + 'v1/' + relpath

    def authenticate(self):
        payload = {'role': self.role, 'jwt': self.jwt_token}
        url = self.path('auth/kubernetes/login')
        logger.info('sending login request to %s', url)
        response = rest.post(url, data=payload)
        auth = response['auth']
        role, policies = auth['metadata']['role'], auth['policies']
        logger.info('login succeeded as role %s, policies %s', role, policies)
        logger.info('saving vault token')
        self.token = auth['client_token']
        self.write_token()

        # TODO: response['auth']['lease_duration']

    def populate(self):
        for k, v in self.paths.items():
            url = self.path(f'/secret/data/{v}')
            target = os.path.join(self.secrets_dir, k)

            logger.info('fetching %s from %s', v, url)
            response = rest.get(url, headers={'X-Vault-Token': self.token})
            data = response['data']['data']

            if self.recurse_secrets:
                logger.info('recursing enabled, writing keys inside %s to their own files within %s', k, target)
                os.makedirs(target)
                for k, v in data.items():
                    r_target = os.path.join(target, k)
                    logger.info('writing %s to %s', v, r_target)
                    with open(r_target, 'w') as f:
                        f.write(json.dumps(v))
            else:
                logger.info('writing %s to %s', v, target)
                with open(target, 'w') as f:
                    f.write(json.dumps(data))
