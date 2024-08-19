version=':v1.00'  # Versao Inicial
version=':v1.50'  # Novos cloudamq, system_configm, Keysetter, Logger e Exchange
version=':v1.51'  # Ajustes para confiabilidade
version=':v1.60'  # Trabalhando com tasks

echo "TROCAR A VERSAO DAS IMAGENS EM docker-compose.yml"
sed -i'' -e 's/:v1.51/:v1.60/g' docker-compose.yml

echo "GERAR IMAGENS SG_InfoConnector ${version}"

echo "CLASSES ACESSORIAS Logger Exchange e Configurator"
if [ -d "utils" ]; then
  rm -rf utils
fi
sleep 5
git clone git@github.com:desenvolvimentopsa/Logger.git utils/Logger
git clone git@github.com:desenvolvimentopsa/Exchange.git utils/Exchange
git clone git@github.com:desenvolvimentopsa/Configurator.git utils/Configurator
cd utils
find . -name "*.py" | xargs -I {} cp {} .
rm -rf Logger Exchange Configurator
cd ..

cd dashboard
cp -r ../utils .
echo DASHBOARD
docker build -t dashboard${version} .
cd ..
rm -rf dashboard/utils