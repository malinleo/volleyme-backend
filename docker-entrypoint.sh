#!/bin/bash

uvicorn src.volleyme.main:app --host ${HOST} --port ${PORT} --reload