from __future__ import annotations

import asyncio
import collections.abc
import dataclasses
import datetime
import itertools
import logging

import aio_pika
import pamqp.commands
import tenacity

from src.common import pubsub

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True)
class RabbitMQPublisher(pubsub.Publisher):
    connection: aio_pika.Connection
    exchange_name: str

    async def publish(self, messages: collections.abc.Iterable[pubsub.Message]) -> None:
        async with (
            self.connection.channel(publisher_confirms=False) as channel,
            channel.transaction(),
        ):
            exchange = await channel.declare_exchange(self.exchange_name, durable=True)
            tasks: list[asyncio.Task[None]] = []
            for message in messages:
                rabbit_message = aio_pika.Message(
                    body=message.get_body(),
                    headers=message.get_headers(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    timestamp=datetime.datetime.now(datetime.UTC).timestamp(),
                )
                tasks.append(
                    asyncio.create_task(
                        self._publish_message(
                            exchange,
                            rabbit_message,
                            message.get_routing_key(),
                        )
                    )
                )
                # Return control flow to the event loop to start task
                await asyncio.sleep(0)
            await asyncio.gather(*tasks)

    async def _publish_message(
        self,
        exchange: aio_pika.abc.AbstractExchange,
        message: aio_pika.Message,
        routing_key: str,
    ) -> None:
        try:
            confirmation = await exchange.publish(
                message,
                routing_key=routing_key,
            )
        except Exception as e:
            _logger.error(f"Error publishing message: {e}", exc_info=True)
            return
        if not isinstance(confirmation, pamqp.commands.Basic.Ack):
            _logger.error(f"Message {message.body!r} was not acknowledged by broker!")
        return


class RabbitMQSubscriber(pubsub.Subscriber):
    connection: aio_pika.Connection
    queue_name: str
    poll_interval_seconds: float = 1.0
    timeout_seconds: float = 10.0

    async def get_messages(
        self,
        count: int | None = None,
    ) -> list[pubsub.ReceivedMessage]:
        messages: list[pubsub.ReceivedMessage] = []
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(self.queue_name, durable=True)
            _iter = range(count) if count else itertools.count()
            for _ in _iter:
                message = await self._get_message(queue)
                if not message:
                    await channel.flow()
                    break
                messages.append(message)
        return messages

    async def get_message(self) -> pubsub.ReceivedMessage | None:
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(self.queue_name, durable=True)
            return await self._get_message(queue)

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=8),
        retry=tenacity.retry_if_exception_type(aio_pika.exceptions.AMQPError),
        reraise=True,
    )
    async def _get_message(
        self,
        queue: aio_pika.abc.AbstractQueue,
    ) -> pubsub.ReceivedMessage | None:
        rabbit_message = await queue.get(
            fail=False,
            no_ack=True,
            timeout=self.timeout_seconds,
        )
        if not rabbit_message:
            return None
        await rabbit_message.ack()
        return pubsub.ReceivedMessage(
            body=rabbit_message.body,
            headers=rabbit_message.headers,
        )

    async def iter_messages(
        self,
    ) -> collections.abc.AsyncIterator[pubsub.ReceivedMessage]:
        return self._iter_messages()

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=16),
        retry=tenacity.retry_if_exception_type(aio_pika.exceptions.AMQPError),
        reraise=True,
    )
    async def _iter_messages(
        self,
    ) -> collections.abc.AsyncIterator[pubsub.ReceivedMessage]:
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(self.queue_name, durable=True)
            for _ in itertools.count():
                rabbit_message = await self._get_message(queue)
                if not rabbit_message:
                    await channel.flow()
                    await asyncio.sleep(self.poll_interval_seconds)
                    continue
                yield pubsub.ReceivedMessage(
                    body=rabbit_message.body,
                    headers=rabbit_message.headers,
                )
