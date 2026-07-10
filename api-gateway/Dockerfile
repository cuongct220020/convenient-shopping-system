FROM kong:3.9.1-ubuntu

USER root

# Cài đặt gettext-base (chứa envsubst) và tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext-base tzdata && \
    rm -rf /var/lib/apt/lists/*

# Cấu hình timezone cho Việt Nam
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

USER kong