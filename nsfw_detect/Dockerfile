FROM bvlc/caffe:cpu

WORKDIR /nsfw_detect

COPY nsfw_detect.sh ./
COPY open_nsfw ./open_nsfw

WORKDIR /nsfwdetectbot

ENTRYPOINT [ "bash", "/nsfw_detect/nsfw_detect.sh" ]
