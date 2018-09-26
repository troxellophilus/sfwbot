FROM bvlc/caffe:cpu

ENV SRC_DIR "/detect_nsfw"

COPY nsfw_detect.sh ${SRC_DIR}/
COPY open_nsfw ${SRC_DIR}/open_nsfw

WORKDIR ${SRC_DIR}

ENTRYPOINT [ "/usr/bin/env", "bash", "/detect_nsfw/nsfw_detect.sh" ]
