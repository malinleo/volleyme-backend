from __future__ import annotations

import typing

import fastapi

from src.common import schemas

T = typing.TypeVar("T")


class PaginationParams(schemas.BaseSchema):
    limit: int
    offset: int


class PaginatedResponse(schemas.BaseSchema, typing.Generic[T]):
    next_url: str
    prev_url: str | None = None
    items: list[T]

    @classmethod
    def build(
        cls,
        request: fastapi.Request,
        pagination_params: PaginationParams,
        items: list[T],
    ) -> PaginatedResponse[T]:
        return cls(
            items=items,
            next_url=cls.get_next_url(request, pagination_params),
            prev_url=cls.get_prev_url(request, pagination_params),
        )

    @staticmethod
    def get_next_url(
        request: fastapi.Request,
        pagination_params: PaginationParams,
    ) -> str:
        return str(
            request.url.include_query_params(
                limit=pagination_params.limit,
                offset=pagination_params.offset + pagination_params.limit,
            )
        )

    @staticmethod
    def get_prev_url(
        request: fastapi.Request,
        pagination_params: PaginationParams,
    ) -> str | None:
        prev_offset = pagination_params.offset - pagination_params.limit
        if prev_offset < 0 and pagination_params.offset != 0:
            return str(
                request.url.include_query_params(
                    limit=pagination_params.limit,
                    offset=0,
                )
            )
        if prev_offset >= 0:
            return str(
                request.url.include_query_params(
                    limit=pagination_params.limit,
                    offset=prev_offset,
                )
            )
        return None
