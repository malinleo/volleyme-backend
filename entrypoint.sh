#!/bin/bash

sleep 10000
uvicorn src.volleyme.main:app --reload --host ${HOST} --port ${PORT}
