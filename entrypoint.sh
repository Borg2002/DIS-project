#!/bin/bash
# host=0.0.0.0 is important so flask exposes the application to the outside network
flask run --host=0.0.0.0 --debug