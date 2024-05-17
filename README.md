![](assets/GGUF_n_Go_Header.png)

# GGUF'n'GO

Welcome to **GGUF'n'Go**, your go-to tool for easily creating quantized versions of Hugging Face models in the GGUF
format. Whether you're a machine learning enthusiast or a professional looking to optimize your models, GGUF'n'Go
simplifies the process of converting models into various quantized formats for efficient deployment.

## Why GGUF'n'Go?

Quantization is a key technique in reducing the size of large language models (LLMs) without significantly compromising
their performance. By converting models to lower precision formats, you can save on storage, reduce latency, and enable
deployment on resource-constrained environments. GGUF'n'Go supports a wide range of quantization types, ensuring
flexibility and efficiency for your specific needs.

## How to Use

### Prerequisites

Ensure that you have `curl` and `unzip` installed on your system. These tools are essential for downloading and
extracting the necessary files.

### Setup

Follow these steps to set up the project:

1. Clone the repository:
    ```bash
    git clone git@github.com:thesven/GGUF-n-Go.git
    cd GGUF-n-Go
    ```

2. Make the setup script executable and run it. This will download and compile `llama.cpp`, as well as download
   the `wiki.train.raw` dataset.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

### Configuration

1. Copy the example configuration file and customize it with the Hugging Face model you wish to convert to the GGUF
   format:
    ```bash
    cp gguf.example.toml gguf.toml
    ```

2. Edit `gguf.toml` to specify your model details.

### Running the Conversion

Execute the conversion process with the following command:

```bash
python ./gguf_n_go.py --config ./gguf.toml
```

This will generate the quantized model in the specified formats.

#### Supported Quantization Types

GGUF'n'Go supports a comprehensive range of quantization types, each offering different trade-offs between model size,
performance, and quality. Please see the list of quantization types in the gguf.example.toml file. If you notice any
missing, please feel free to add them.

## Contributing

Feel free to fork this repository and submit pull requests to contribute to the project. All ideas and suggestions are
welcome!

## Happy quantizing!
