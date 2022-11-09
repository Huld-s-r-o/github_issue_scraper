#!/bin/sh

if [ -f /run/secrets/token ]; then
  export GITHUB_TOKEN=$(cat /run/secrets/token)
fi

exec "$@"