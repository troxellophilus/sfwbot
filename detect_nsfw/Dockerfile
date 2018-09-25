FROM bvlc/caffe:cpu

ENV WORKDIR = "/sfwbot"

COPY nsfw_detect.sh ${WORKDIR}/
COPY open_nsfw ${WORKDIR}/open_nsfw

WORKDIR ${WORKDIR}

ENTRYPOINT [ "./nsfw_detect.sh" ]
