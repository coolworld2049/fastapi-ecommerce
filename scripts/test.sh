#! /bin/bash

set +e

# shellcheck disable=SC2086
source ../src/.env

printf '\n%s\n\n' "❗ APP_ENV=$APP_ENV"

REQUIRED_PKG="netcat"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi
printf '\n'

set -e
for port in 27122-27127 27017 27119 8001-8002 6433 6434 443 80; do
  set +e
  url="127.0.0.1"
  CMD="$(nc -vz $url $port)"
  printf '%s' "$CMD"
done
