FROM kong:3.9.1-ubuntu

USER root

# Cài đặt gettext-base (chứa envsubst)
# --no-install-recommends: Không cài các gói "được đề xuất" (không bắt buộc), giúp giảm dung lượng
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext-base && \
    rm -rf /var/lib/apt/lists/*

USER kong

