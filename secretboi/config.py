import os

from . import log

logger = log.make_logger(__name__)


class MissingEnvVars(Exception):
    def __init__(self, message, env_vars=[]):
        super().__init__(message)
        self.message = message
        self.env_vars = env_vars

    def __str__(self):
        vals = '\n'.join([f'{v}="..."' for v in self.env_vars])
        return f'{self.message}\n{vals}'


class MissingPaths(Exception):
    def __init__(self, message, paths=[]):
        super().__init__(message)
        self.message = message
        self.paths = paths

    def __str__(self):
        paths = '\n'.join(['does not exist: ' + p for p in self.paths])
        return f'{self.message}\n{paths}'


class Config:

    default_kubernetes_token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
    defualt_secrets_directory = '/secrets'

    @classmethod
    def from_env(cls, env={}):
        logger.info('pulling config from envirnment variables')

        logger.info('checking for required environment variables')
        required = ['VAULT_ADDR', 'VAULT_ROLE']
        missing = [var for var in required if var not in env]
        if any(missing):
            raise MissingEnvVars('There are missing environment variables!', env_vars=missing)

        kwargs = {}
        for var in required:
            value = env[var]
            logger.info('using %s="%s"', var, value)
            kwargs[var.lower()] = value

        logger.info('setting defaults from environment variables')
        if 'KUBERNETES_TOKEN_PATH' in env:
            value = env['KUBERNETES_TOKEN_PATH']
            logger.info('using KUBERNETES_TOKEN_PATH="%s"', value)
            kwargs['kubernetes_token_path'] = value
        else:
            kwargs['kubernetes_token_path'] = cls.default_kubernetes_token_path

        if 'ONLY_RUN_ONCE' in env:
            value = env['ONLY_RUN_ONCE']
            logger.info('using ONLY_RUN_ONCE="%s"', value)
            kwargs['only_run_once'] = value in ['1', 'true', 'yes', 'yas']

        if 'RECURSE_SECRETS' in env:
            value = env['RECURSE_SECRETS']
            logger.info('using RECURSE_SECRETS="%s"', value)
            kwargs['recurse_secrets'] = value in ['1', 'true', 'yes', 'yas']

        if 'SECRETS_DIRECTORY' in env:
            value = env['SECRETS_DIRECTORY']
            logger.info('using SECRETS_DIRECTORY="%s"', value)
            kwargs['secrets_directory'] = value
        else:
            kwargs['secrets_directory'] = cls.defualt_secrets_directory

        logger.info('checking if paths exist')
        paths = ('kubernetes_token_path', 'secrets_directory')
        missing = [kwargs[key] for key in paths if not os.path.exists(kwargs[key])]
        if missing:
            raise MissingPaths('There are missing paths!', paths=missing)

        logger.info('paring secret paths to target')
        kwargs['paths'] = {}
        for key, value in env.items():
            if not key.startswith('SECRET_'):
                continue

            target = key.split('SECRET_')[1]
            logger.info('found %s="%s"', target, value)
            kwargs['paths'][target] = value

        return cls(**kwargs)

    def __init__(
            self, vault_addr='', vault_role='',
            kubernetes_token_path='', only_run_once=False, recurse_secrets=False,
            secrets_directory='', paths={}
    ):
        self.vault_addr = vault_addr
        self.vault_role = vault_role
        self.kubernetes_token_path = kubernetes_token_path
        self.only_run_once = only_run_once
        self.recurse_secrets = recurse_secrets
        self.secrets_directory = secrets_directory
        self.paths = paths
