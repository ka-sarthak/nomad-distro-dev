export NODE_OPTIONS=--openssl-legacy-provider
cd packages/nomad-FAIR/gui/ || exit

## To be used only once
# uv run python -m nomad.cli dev gui-env > .env.development 

yarn
yarn start
cd ../../../