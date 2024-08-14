# habr-qna-parser

A script that parses all questions and answers from qna.habr.com with their metadata.
The full parsed dataset can be downloaded [here](https://huggingface.co/datasets/its5Q/habr_qna).

## Build docker image

```bash
docker build -t habr-qna-parser .
```

## Run docker image as container

```bash
export UID=$(id -u)
export GID=$(id -g)

docker run \
  -it \
  --rm \
  --user $UID:$GID \
  --volume="$PWD:/app:rw" \
  habr-qna-parser
```
