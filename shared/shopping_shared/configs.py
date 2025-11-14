# shared/shopping_shared/configs.py

class PostgreSQLConfig:
    """PostgreSQL database configuration."""

    def __init__(
        self,
        driver: str,
        user: str,
        password: str,
        host: str,
        port: int,
        name: str
    ):
        self.DB_DRIVER = driver
        self.DB_USER = user
        self.DB_PASSWORD = password
        self.DB_NAME = name
        self.DB_HOST = host
        self.DB_PORT = port
        self.DATABASE_URI = f'{driver}://{user}:{password}@{host}:{port}/{name}'


class RedisConfig:
    """Redis configuration."""

    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: str | None = None,
        decode_responses: bool = True
    ):
        self.REDIS_HOST = host
        self.REDIS_PORT = port
        self.REDIS_DB = db
        # Rất quan trọng: Mật khẩu (nếu có)
        self.REDIS_PASSWORD = password
        # Rất tiện lợi: Tự động giải mã bytes thành string (utf-8)
        self.REDIS_DECODE_RESPONSES = decode_responses


class KafkaConfig:
    """Kafka configuration."""

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str | None = 'default-client',
        security_protocol: str = 'PLAINTEXT',
        sasl_mechanism: str | None = None,
        sasl_plain_username: str | None = None,
        sasl_plain_password: str | None = None
    ):
        self.KAFKA_BOOTSTRAP_SERVERS = bootstrap_servers
        self.CLIENT_ID = client_id

        # Cấu hình bảo mật (phổ biến nhất là SASL/PLAINTEXT hoặc SASL/SSL)
        self.SECURITY_PROTOCOL = security_protocol
        self.SASL_MECHANISM = sasl_mechanism
        self.SASL_PLAIN_USERNAME = sasl_plain_username
        self.SASL_PLAIN_PASSWORD = sasl_plain_password