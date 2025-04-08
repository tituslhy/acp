import logging
from importlib.metadata import version
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    SERVICE_NAMESPACE,
    SERVICE_VERSION,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExportResult

logger = logging.getLogger("uvicorn.error")


class SilentOTLPSpanExporter(OTLPSpanExporter):
    def export(self, spans: Any) -> SpanExportResult:
        try:
            return super().export(spans)
        except Exception as e:
            logger.warning(f"OpenTelemetry Exporter failed silently: {e}")
            return SpanExportResult.FAILURE


def configure_telemetry() -> None:
    current_provider = trace.get_tracer_provider()

    # Detect default provider and override
    if isinstance(current_provider, trace.ProxyTracerProvider):
        provider = TracerProvider(
            resource=Resource(
                attributes={
                    SERVICE_NAME: "acp-server",
                    SERVICE_NAMESPACE: "acp",
                    SERVICE_VERSION: version("acp-sdk"),
                }
            )
        )

        processor = BatchSpanProcessor(SilentOTLPSpanExporter())
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)
