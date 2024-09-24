cd packages/nomad-FAIR/ops/docker-compose/infrastructure/ || exit
sudo docker compose down
sudo docker compose up -d
cd ../../../../../