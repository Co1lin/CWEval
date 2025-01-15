# 🛡 CWEval

Is the LLM-generated code 🔧 functional ***and*** ⛑️ secure? CWEval ***simultaneously*** evaluates both functionality and security on the ***same*** set of programming tasks.

To appear in [LLM4Code 2025](https://llm4code.github.io). arXiv is [here](https://arxiv.org/abs/2501.08200).

## 🚀 Quick Start

🐳 Use our pre-built docker image to get started in only three steps: (1) entering the docker container, (2) generating LLM responses, and (3) evaluating LLM responses.

### 1. Prepare the environment

Pull the docker image:

```bash
docker pull co1lin/cweval # from Docker Hub
# docker pull ghcr.io/co1lin/cweval:latest # from GitHub Container Registry
```


Start a container and get a `zsh` shell to work in it:

```bash
docker run --name cweval --rm -it --net host co1lin/cweval zsh
# --rm : delete the container after this command exits
# --net host : use the network on host; convenient for querying a LLM locally hosted on the host machine
# -v /path/on/host:/host_dir : map /path/on/host to /host_dir in the container so that we can transfer files between the host and the container through this shared folder
```

By default, you will be in the directory `/home/ubuntu/CWEval` in the container; if not, enter this directory.

Setup environment variables by:

```bash
source .env
```

(Optional) The we can do some sanity checks:

```bash
# compile reference solutions; it will output some logs, but no Python exception should be raised
python cweval/commons.py compile_all_in --path benchmark/
echo $? # "0" is expected here; check if the command above exits normally

# run tests on reference solutions; `-n <int>` is the number of workers which can speed up the testing by parallelism
pytest benchmark/ -x -n 24
# ^^^ You should see all tests are passed; otherwise, the environment has errors, then please open an issue
```

### 2. Generate LLM responses

Once the environment is ready, we can generate LLM responses with various models by the command `python cweval/generate.py gen --model <model_name>`.

We use [litellm](https://github.com/BerriAI/litellm) to query LLMs.  The command line argument `--model <model_name>` will be passed to `litellm.completion(model=<model_name>, ...)`. Refer [docs of litellm](https://docs.litellm.ai) ([Supported Models & Providers](https://docs.litellm.ai/docs/providers)) to know how to specify the value for `--model`.

Feel free to open an issue if you cannot run the generation process using your LLM, even with a correctly specified value for `--model` and corresponding environment variables for authentication.

Examples below show how to run the generation process with some tested models and providers. They also show the following changable parameters:

- `--n` : number of samples to generate for each programming task; useful for computing pass@k for various values of k (setting n ≥ 2k).
- `--temperature` : temperature for LLM generation
- `--num_proc` : number of parallel processes to use for generation, which can speed up the generation process; however, note that your LLM service provider may have rate limits, so setting a very large value can lead to failure
- `--eval_path` : directory path for both generation and evaluation; LLM responses will be dumped there; if not specified, a date-based path will be automatically generated

```bash
# OpenAI
export OPENAI_API_KEY=sk-xxxxxx
python cweval/generate.py gen --n 3 --temperature 0.8 --num_proc 16 --eval_path evals/eval_4omini_t8 --model gpt-4o-mini-2024-07-18

# Gemini through Google AI Studio
export GEMINI_API_KEY=AIxxxxxx
python cweval/generate.py gen --n 3 --temperature 0.8 --num_proc 16 --eval_path evals/eval_gflash_t8 --model gemini/gemini-1.5-flash-002

# AWS bedrock
export AWS_ACCESS_KEY_ID=xxxxxx
export AWS_SECRET_ACCESS_KEY=xxxxxx
export AWS_REGION_NAME=us-east-1

python cweval/generate.py gen --n 3 --temperature 0.8 --num_proc 16 --eval_path evals/eval_haiku_t8 --model bedrock/anthropic.claude-3-5-haiku-20241022-v1:0

python cweval/generate.py gen --n 3 --temperature 0.8 --num_proc 16 --eval_path evals/eval_llama3b_t8 --model bedrock/us.meta.llama3-2-3b-instruct-v1:0

# local serving with vLLM
# pip install vllm
vllm serve deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct --trust-remote-code --tensor-parallel-size 4 --max-model-len 16384 --disable-log-requests # in another shell session

export OPENAI_API_KEY=sk-xxxxxx # set a dummy one
python cweval/generate.py gen --n 3 --temperature 0.8 --num_proc 16 --eval_path evals/eval_dscv2lite_t8 --model openai/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct --api_base http://localhost:8000/v1
```

### 3. Evaluate LLM Responses

We can evaluate the generated responses by:

```bash
# set --eval_path to the one used in generation
# since we are already in docker, we should set --docker False
python cweval/evaluate.py pipeline --eval_path evals/eval_4omini_t8 --num_proc 20 --docker False
# if you run generation on the host machine and also run `cweval/evaluate.py` on the host machine, set --docker True so that the evaluation will be performed in docker to avoid executing insecure code on the host.
```

pass@k results will be printed out at the end. You can run the following command to print it again:

```bash
python cweval/evaluate.py report_pass_at_k --eval_path evals/eval_4omini_t8
```

Detailed evaluation results are stored in `<eval_path>/res_all.json` (e.g. `evals/eval_4omini_t8/res_all.json`).

## 📜 Citation

```bibtex
@misc{peng2025cwevaloutcomedrivenevaluationfunctionality,
  title={CWEval: Outcome-driven Evaluation on Functionality and Security of LLM Code Generation},
  author={Jinjun Peng and Leyi Cui and Kele Huang and Junfeng Yang and Baishakhi Ray},
  year={2025},
  eprint={2501.08200},
  archivePrefix={arXiv},
  primaryClass={cs.SE},
  url={https://arxiv.org/abs/2501.08200},
}
```

## 💻 Development

### Python (required)

```bash
# 1. Setup mamba/conda (mamba resolves dependencies faster than conda).
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh

# 2. Create a Python environment
mamba create -y -n cweval python=3.10
conda activate cweval

# 3. Install core dependencies
pip install -r requirements/core.txt
pip install -r requirements/ai.txt

# 4. Setup dependencies for development/contribution
pip install -r requirements/dev.txt
pre-commit install

# 5. Pull docker image
docker pull co1lin/cweval:latest

# Before running the code, append the repo root path to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```


### C

```bash
mamba install libarchive zlib
sudo apt install libjwt-dev
```


### JavaScript

```bash
# 1. Install nvm according to https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 2. Configure node.js
nvm install --lts
nvm use --lts

# 3. Install dependencies globally
npm install -g escape-html node-rsa argon2 escape-string-regexp lodash js-yaml jsonwebtoken jsdom xpath sqlite3

# 4. Enable global dependencies in scripts
export NODE_PATH=$(npm root -g)
```

### Golang

```bash
# 1. Install golang
wget https://go.dev/dl/go1.23.3.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.23.3.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# 2. Install dependencies
go mod download
go install golang.org/x/tools/cmd/goimports@latest
export PATH=$PATH:~/go/bin
```

### Sanity Test

Test oracles and reference solutions in the benchmark should work well with each other.

```bash
pytest benchmark -x -n 24
```

### Note: [`pre-commit`](https://pre-commit.com)

[`pre-commit`](https://pre-commit.com) is used to unify the format of all files. Basically after installing it, the linters will check the changed files before each commit. If there is any violation, it will block the commit and fix them. Then you need to `git add` the changes and `git commit` again.
