# download the latest version of llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp || exit
pip install -r requirements.txt
make
cd ..

# download a copy of wiki.train.raw
curl -L -O https://github.com/kpot/keras-transformer/raw/master/example/wikitext-2-raw-v1.zip
unzip wikitext-2-raw-v1.zip
cd wikitext-2-raw || exit
mv wiki.train.raw ../
cd ../
rm -rf wikitext-2-raw
rm -rf wikitext-2-raw-v1.zip

# download the groups merged dataset
curl -L -O https://github.com/ggerganov/llama.cpp/files/14194570/groups_merged.txt

curl -L -O https://gist.githubusercontent.com/bartowski1182/b6ac44691e994344625687afe3263b3a/raw/d53a2c532e318ebb8258bb1ccb94ddb870b04be2/calibration_data.txt

# create a directory to hold all of the models
mkdir models