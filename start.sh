#!/bin/bash
export LD_LIBRARY_PATH="/nix/store/*postgresql-*/lib:$LD_LIBRARY_PATH"
gunicorn run:app