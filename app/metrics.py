"""
Módulo de Métricas para CloudWatch
Implementa métricas de tiempo de ejecución y comportamiento HTTP
"""
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Colector de métricas para AWS CloudWatch
    Implementa:
    - Métrica de latencia (tiempo de ejecución)
    - Métrica de comportamiento HTTP (2xx, 4xx, 5xx)
    """

    def __init__(self, namespace: str, environment: str, region: str = "us-east-1"):
        self.namespace = namespace
        self.environment = environment
        self.region = region
        self.cloudwatch = None
        
        # Inicializar cliente de CloudWatch solo si existen credenciales en el entorno
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_profile = os.getenv("AWS_PROFILE")

        if aws_key and aws_secret or aws_profile:
            try:
                self.cloudwatch = boto3.client(
                    'cloudwatch',
                    region_name=region,
                    aws_access_key_id=aws_key or None,
                    aws_secret_access_key=aws_secret or None
                )
                logger.info(f"CloudWatch client initialized for region {region}")
            except NoCredentialsError:
                logger.warning("AWS credentials not found. Metrics will be logged locally only.")
            except Exception as e:
                logger.warning(f"Could not initialize CloudWatch client: {e}")
        else:
            logger.info("No AWS credentials found in environment; CloudWatch metrics disabled.")

    def _get_http_status_range(self, status_code: int) -> str:
        """Determina el rango del código HTTP"""
        if 200 <= status_code < 300:
            return "2xx"
        elif 400 <= status_code < 500:
            return "4xx"
        elif 500 <= status_code < 600:
            return "5xx"
        else:
            return "other"

    def record_latency(self, endpoint: str, latency_ms: float):
        """
        Registra la latencia de un endpoint en milisegundos
        """
        dimensions = [
            {'Name': 'Environment', 'Value': self.environment},
            {'Name': 'Endpoint', 'Value': endpoint}
        ]
        
        logger.info(f"[METRIC] Latency - {endpoint}: {latency_ms:.2f}ms (env: {self.environment})")
        
        if self.cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=[
                        {
                            'MetricName': 'RequestLatency',
                            'Dimensions': dimensions,
                            'Timestamp': datetime.utcnow(),
                            'Value': latency_ms,
                            'Unit': 'Milliseconds',
                            'StorageResolution': 60  # Standard resolution
                        }
                    ]
                )
            except ClientError as e:
                logger.error(f"Error sending latency metric to CloudWatch: {e}")

    def record_http_status(self, endpoint: str, status_code: int):
        """
        Registra el conteo de respuestas HTTP por rango (2xx, 4xx, 5xx)
        """
        status_range = self._get_http_status_range(status_code)
        
        dimensions = [
            {'Name': 'Environment', 'Value': self.environment},
            {'Name': 'Endpoint', 'Value': endpoint},
            {'Name': 'StatusRange', 'Value': status_range}
        ]
        
        logger.info(f"[METRIC] HTTP Status - {endpoint}: {status_code} ({status_range}) (env: {self.environment})")
        
        if self.cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=[
                        {
                            'MetricName': 'HTTPStatusCount',
                            'Dimensions': dimensions,
                            'Timestamp': datetime.utcnow(),
                            'Value': 1,
                            'Unit': 'Count',
                            'StorageResolution': 60
                        }
                    ]
                )
            except ClientError as e:
                logger.error(f"Error sending HTTP status metric to CloudWatch: {e}")

    def record_error(self, error_type: str, message: str):
        """
        Registra errores de la aplicación
        """
        dimensions = [
            {'Name': 'Environment', 'Value': self.environment},
            {'Name': 'ErrorType', 'Value': error_type}
        ]
        
        logger.error(f"[METRIC] Error - {error_type}: {message} (env: {self.environment})")
        
        if self.cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=[
                        {
                            'MetricName': 'ApplicationErrors',
                            'Dimensions': dimensions,
                            'Timestamp': datetime.utcnow(),
                            'Value': 1,
                            'Unit': 'Count',
                            'StorageResolution': 60
                        }
                    ]
                )
            except ClientError as e:
                logger.error(f"Error sending error metric to CloudWatch: {e}")

    def record_custom_metric(self, metric_name: str, value: float, unit: str = 'Count', 
                             extra_dimensions: list = None):
        """
        Registra una métrica personalizada
        """
        dimensions = [
            {'Name': 'Environment', 'Value': self.environment}
        ]
        
        if extra_dimensions:
            dimensions.extend(extra_dimensions)
        
        logger.info(f"[METRIC] Custom - {metric_name}: {value} {unit} (env: {self.environment})")
        
        if self.cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=[
                        {
                            'MetricName': metric_name,
                            'Dimensions': dimensions,
                            'Timestamp': datetime.utcnow(),
                            'Value': value,
                            'Unit': unit,
                            'StorageResolution': 60
                        }
                    ]
                )
            except ClientError as e:
                logger.error(f"Error sending custom metric to CloudWatch: {e}")
