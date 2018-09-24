FROM bvlc/caffe:cpu

ENV WORKDIR = "/nsfw_detect"

COPY nsfw_detect.sh ${WORKDIR}
COPY open_nsfw ${WORKDIR}/open_nsfw

WORKDIR ${WORKDIR}

ENTRYPOINT [ "/usr/bin/env", "bash", "/nsfw_detect/nsfw_detect.sh" ]
