set -o errexit
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1

dockle --exit-level WARN -af settings.py gisaia/agate:${VERSION}
dockle -af settings.py gisaia/airs:${VERSION}
dockle -af settings.py gisaia/fam:${VERSION}
dockle -af settings.py -i CIS-DI-0009 -i DKL-DI-0005 gisaia/aproc-proc:${VERSION}
dockle -af settings.py gisaia/aproc-service:${VERSION}
dockle -af settings.py --accept-key KEY_SHA512 gisaia/arlas-fam-wui:${VERSION}
dockle -af settings.py gisaia/stac-geodes:${VERSION}
