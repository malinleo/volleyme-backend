#!/bin/bash

uvicorn src.volleyme.presentation.rest.main:app --host ${HOST} --port ${PORT} --reload