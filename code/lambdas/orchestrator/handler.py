import json
from http import HTTPStatus
from typing import Any, Dict

from quant_core.bodies.ig_alert_body import IGAlertBody
from quant_core.clients.aws.sns import SNSClient
from quant_core.entities.response import Response
from quant_core.enums.platform import Platform
from quant_core.services.core_logger import CoreLogger
from quant_core.settings.configuration import Configuration


def handle(event: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
    """Forward request to the correct lambda function based on the event."""
    event_body = json.loads(event.get("body", "{}"))
    CoreLogger().info(f"Received event body: {json.dumps(event_body, indent=2)}")

    if Platform(event_body["platform"]) is Platform.IG:
        parsed_body = IGAlertBody(event_body)

        SNSClient().publish(topic_arn=Configuration().sns_topic_arn, message=parsed_body.to_sns_body())
    elif Platform(event_body["platform"]) is Platform.METATRADER:
        raise NotImplementedError()
    else:
        raise ValueError(f"Platform {event_body['platform']} is not supported")

    return Response(HTTPStatus.OK, "Signal has been successfully published to SNS!").to_response()
