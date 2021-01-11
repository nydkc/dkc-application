#!/bin/sh

gcloud beta emulators datastore start --host-port=localhost:8500 &

$(gcloud beta emulators datastore env-init)

dev_appserver.py \
    --application=dkc-app \
    --support_datastore_emulator true \
    --skip_sdk_update_check true \
    src/app.yaml
