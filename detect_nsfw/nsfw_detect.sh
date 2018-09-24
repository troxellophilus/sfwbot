#!/usr/bin/env bash

IMAGE_DIR="${2:?"Need image directory argument."}"

for filepath in ${image_dir}/*; do
    [[ ${filepath} == *.result ]] && continue
    python ./open_nsfw/classify_nsfw.py \
        --model_def ./open_nsfw/nsfw_model/deploy.prototxt \
        --pretrained_model ./open_nsfw/nsfw_model/resnet_50_1by2_nsfw.caffemodel \
        "${filepath}" \
        > "${filepath}.result"
done
