#! /bin/bash -x

set -e
# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)

# shellcheck disable=SC2164
rm -rf ./ssl
mkdir ./ssl

# shellcheck disable=SC2164
cd ./ssl

set +e
apt install libnss3-tools
apt install mkcert
VPS_IP="$(ip  -f inet a show eth0| grep inet| awk '{ print $2}' | cut -d/ -f1)"
set -e

# shellcheck disable=SC2035
mkcert -key-file key.pem -cert-file cert.pem \
  "${NGINX_DOMAIN}" \
  www."${NGINX_DOMAIN}" \
  *."${NGINX_DOMAIN}" \
  "${VPS_IP:-localhost}" \
  127.0.0.1 ::1
