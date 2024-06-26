import argparse
import logging
import os
import subprocess
from typing import Any

import toml
import torch
from huggingface_hub import snapshot_download, HfApi, create_repo
from transformers import AutoModelForCausalLM


class GGUFNGo:
    config_toml: dict[str, Any]
    huggingface_model_name: str
    huggingface_user_name: str
    gguf_model_name_base: str
    gguf_output_types: list[str]
    output_dir: str
    imatrix_path: str
    dataset_path: str

    def __init__(self, config_toml_path: str):
        logging.basicConfig(
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            level=logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger("GGUFNGo")
        self.logger.propagate = True

        self.logger.info(f"Loading config from {config_toml_path} ...")
        self.config_toml = toml.load(config_toml_path)
        self.logger.info(f"Parsing config values ...")
        self.huggingface_model_name = self.config_toml["huggingface"]["model_name"]
        self.huggingface_user_name = self.config_toml["huggingface"][
            "hugging_face_username"
        ]
        self.gguf_model_name_base = self.config_toml["gguf"]["model_name_base"]
        self.gguf_output_types = self.config_toml["gguf"]["output_types"]
        self.output_dir = self.config_toml["gguf"]["output_directory"]
        self.dataset_path = self.config_toml["dataset"]["imatrix"]

    def download_hf_model(self, hf_model_name, output_dir):
        self.logger.info(f"Downloading Huggingface model {hf_model_name} ...")
        try:
            snapshot_download(
                repo_id=hf_model_name,
                local_dir=f"{output_dir}/{hf_model_name}",
                revision="main",
            )
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            return False

    def upload_models_to_hf(self, model_dir, base_model_name, hf_username):
        api = HfApi()

        self.logger.info(f"Creating Repo Huggingface ...")
        create_repo(
            repo_id=f"{hf_username}/{base_model_name}-GGUF",
            repo_type="model",
            exist_ok=True,
        )

        self.logger.info(f"Uploading models to Huggingface ...")
        api.upload_folder(
            folder_path=model_dir,
            repo_id=f"{hf_username}/{base_model_name}-GGUF",
            allow_patterns=[
                f"{base_model_name}-GGUF-*.gguf",
                f"imatrix_{base_model_name}.dat",
            ],
        )

    def do_initial_conversion(self, hf_model_name, output_model_name, output_type):

        output_name = f"{self.output_dir}/{output_model_name}"
        command = f"python llama.cpp/convert-hf-to-gguf.py {hf_model_name} --outfile {output_name} --outtype {output_type}"
        # check to see if the model has already been converted
        if os.path.exists(output_name):
            self.logger.info(
                f"Initial converted model already exists: {output_model_name}"
            )
            return output_name
        else:
            try:
                self.logger.info(
                    f"Starting initial GGUF conversion of {hf_model_name} to {output_type} ..."
                )
                process = subprocess.run(
                    command, capture_output=True, text=True, shell=True
                )

                self.logger.info(f"Conversion complete: {output_model_name}")
            except Exception as e:
                self.logger.error(f"Error converting model: {e}")
                exit(0)

            return output_name

    def do_q_conversion(self, original_model_name, new_model_name, output_type):
        command = (
            f"./llama.cpp/quantize {original_model_name} {new_model_name} {output_type}"
        )
        try:
            self.logger.info(
                f"Starting conversion of {original_model_name} to {output_type} ..."
            )
            process = subprocess.run(
                command, capture_output=True, text=True, shell=True
            )
        except Exception as e:
            self.logger.error(f"Error quantizing model: {e}")
            return False
        self.logger.info(f"Conversion complete: {new_model_name}")
        return new_model_name

    def do_iq_conversion(
        self, original_model_name, new_model_name, output_type, imatrix_name
    ):
        command = f"./llama.cpp/quantize --imatrix {imatrix_name} {original_model_name} {new_model_name} {output_type}"
        try:
            self.logger.info(
                f"Starting conversion of {original_model_name} to {output_type} ..."
            )
            process = subprocess.run(
                command, capture_output=True, text=True, shell=True
            )
        except Exception as e:
            self.logger.error(f"Error quantizing model: {e}")
            return False
        self.logger.info(f"Conversion complete: {new_model_name}")
        return new_model_name

    def generate_imatrix(self, hf_model_name, model_for_matrix_gen):
        hf_model_base_name = hf_model_name.split("/")[1]
        imatrix_name = f"imatrix_{hf_model_base_name}.dat"
        matrix_path = f"{self.output_dir}/{imatrix_name}"
        # check to see if the file exists before creating it
        if os.path.exists(matrix_path):
            self.logger.info(f"Importance matrix already exists: {imatrix_name}")
            return matrix_path
        else:

            command = f"./llama.cpp/imatrix -m {model_for_matrix_gen} -f {self.dataset_path} -o {matrix_path} --chunks 100"
            try:
                self.logger.info(
                    f"Generating importance matrix for {hf_model_name} ..."
                )
                process = subprocess.run(
                    command, capture_output=True, text=True, shell=True
                )
            except Exception as e:
                self.logger.error(f"Error generating importance matrix: {e}")
                exit(0)
            self.logger.info(f"Importance matrix generated: {imatrix_name}")
            return matrix_path

    def create_model_name(self, model_base, output_type):
        return f"{model_base}-GGUF-{output_type}.gguf"

    def check_for_iq(self):
        # check to see if our output types contains a string that contains IQ
        self.logger.info(f"Checking for IQ in output types ...")
        for output_type in self.gguf_output_types:
            if "IQ" in output_type:
                return True
        return False

    def infer_torch_dtype(self, model_path):
        tmp_model = AutoModelForCausalLM.from_pretrained(model_path)
        tmp_model_torch_dtype = tmp_model.config.torch_dtype
        self.logger.info(f"Model config: {tmp_model.config}")
        self.logger.info(f"Model torch dtype: {tmp_model_torch_dtype}")
        if tmp_model_torch_dtype == torch.bfloat16:
            return "bf16"
        else:
            return "f16"

    def run(self):

        self.logger.info(f"Starting Run ...")

        # download the huggingface model
        self.download_hf_model(self.huggingface_model_name, self.output_dir)

        # do the initial conversion of the model to create the base we will use for the quants
        initial_conversion_type = self.infer_torch_dtype(
            f"{self.output_dir}/{self.huggingface_model_name}"
        )
        initial_model_path = self.do_initial_conversion(
            f"{self.output_dir}/{self.huggingface_model_name}",
            self.create_model_name(self.gguf_model_name_base, initial_conversion_type),
            initial_conversion_type,
        )

        # check to see if the output types contains any IQ quants as we will need an importance matrix if so
        request_for_iq = self.check_for_iq()
        if request_for_iq:
            # we need to generate the imatrix
            self.imatrix_path = self.generate_imatrix(
                self.huggingface_model_name, initial_model_path
            )

        for output_type in self.gguf_output_types:
            new_model_name = self.create_model_name(
                self.gguf_model_name_base, output_type
            )
            if "IQ" in output_type:
                self.do_iq_conversion(
                    initial_model_path,
                    f"{self.output_dir}/{new_model_name}",
                    output_type,
                    self.imatrix_path,
                )
            else:
                self.do_q_conversion(
                    initial_model_path,
                    f"{self.output_dir}/{new_model_name}",
                    output_type,
                )

        self.upload_models_to_hf(
            self.output_dir, self.gguf_model_name_base, self.huggingface_user_name
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GGUFNGo")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the config .toml file you would like to use",
    )

    args = parser.parse_args()

    quantizer = GGUFNGo(args.config)
    quantizer.run()
