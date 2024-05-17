# download the latest version of llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
pip install -r requirements.txt
make
cd ..

# download a copy of wiki.train.raw
curl -L -O https://github.com/kpot/keras-transformer/raw/master/example/wikitext-2-raw-v1.zip
unzip wikitext-2-raw-v1.zip
cd wikitext-2-raw-v1
mv wiki.train.raw ../
cd ../

# create a directory to hold all of the models
mkdir models