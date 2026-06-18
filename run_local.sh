#!/bin/sh

export GOOGLE_CLOUD_PROJECT=dkc-app
export APPLICATION_ID=dev~$GOOGLE_CLOUD_PROJECT

for i in "$@"; do
case $i in
    --google_application_credentials=*)
		google_application_credentials="${i#*=}"
		shift # past argument=value
		;;
    *)
        echo "Unknown parameter passed: ${i}";
		exit 1
    ;;
esac
done

if [ -z "$google_application_credentials" ]; then
    echo "Usage: $0 --google_application_credentials=<json_key_file>"
    echo
    echo "Error: Missing parameter: --google_application_credentials"
    echo "       You can set this to the JSON key file from the instructions at"
    echo "       https://cloud.google.com/iam/docs/keys-create-delete#creating"
    exit 1
fi


if ! pgrep -f "com.google.cloud.datastore.emulator.CloudDatastore" > /dev/null; then
    gcloud beta emulators datastore start --host-port=localhost:8500 &
    echo "TIP: Use https://github.com/remko/dsadmin to view/modify entities in Datastore emulator"
    echo "Waiting for datastore to start..."
    sleep 5
fi

$(gcloud beta emulators datastore env-init)

# If dsadmin is installed in the PATH, start it (https://github.com/remko/dsadmin)
if command -v dsadmin > /dev/null && ! pgrep "dsadmin" > /dev/null; then
    echo "Found dsadmin in PATH. Starting dsadmin..."
    dsadmin -port 8501 -datastore-emulator-host localhost:8500 &
    sleep 1
fi

# --support_datastore_emulator is currently broken because of https://issuetracker.google.com/issues/331809443
dev_appserver.py \
    --application=$GOOGLE_CLOUD_PROJECT \
    --support_datastore_emulator false \
    --enable_host_checking false \
    --skip_sdk_update_check true \
    --env_var GOOGLE_APPLICATION_CREDENTIALS="$google_application_credentials" \
    src/app.yaml
