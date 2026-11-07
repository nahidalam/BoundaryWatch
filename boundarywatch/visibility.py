from __future__ import annotations

import random

from boundarywatch.model import TraceMessage, VisibleMessage


VISIBILITY_ORDER = ("full", "partial", "gateway_only")
VISIBILITY_LABELS = {
    "full": "Full",
    "partial": "50%",
    "gateway_only": "Gateway-only",
}


def visible_messages(messages: tuple[TraceMessage, ...], visibility: str, seed: int) -> tuple[VisibleMessage, ...]:
    if visibility not in VISIBILITY_ORDER:
        raise ValueError(f"Unknown visibility condition: {visibility}")
    rng = random.Random(seed)
    visible: list[VisibleMessage] = []
    for message in messages:
        if visibility == "full":
            keep = True
        elif visibility == "gateway_only":
            keep = message.channel == "gateway"
        elif message.channel == "gateway":
            keep = True
        else:
            keep = rng.random() < 0.5
        if keep:
            visible.append(VisibleMessage(
                message_id=message.message_id,
                sender=message.sender,
                recipient=message.recipient,
                channel=message.channel,
                event_type=message.event_type,
                text=message.text,
                sequence=message.sequence,
            ))
    return tuple(visible)