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

# create a directory to hold all of the models
mkdir models