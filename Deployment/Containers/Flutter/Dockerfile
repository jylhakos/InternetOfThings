# Use a base image with Flutter and Dart pre-installed
FROM ubuntu:latest AS builder

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV FLUTTER_VERSION 3.22.0
ENV DART_VERSION 3.4.1
ENV PATH="$PATH:/usr/local/flutter/bin"

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    unzip \
    zip \
    build-essential \
    libgtk-3-0 \
    libstdc++6 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git -b stable /usr/local/flutter && \
    cd /usr/local/flutter && \
    git checkout $FLUTTER_VERSION && \
    flutter doctor -v

# Install Dart
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    && wget https://storage.googleapis.com/dart-archive/channels/stable/release/${DART_VERSION}/sdk/dartsdk-linux-x64-release.zip \
    && unzip dartsdk-linux-x64-release.zip \
    && mv dart-sdk /usr/local/dart-sdk \
    && rm dartsdk-linux-x64-release.zip \
    && ln -s /usr/local/dart-sdk/bin/dart /usr/local/bin/dart \
    && ln -s /usr/local/dart-sdk/bin/dartfmt /usr/local/bin/dartfmt \
    && ln -s /usr/local/dart-sdk/bin/pub /usr/local/bin/pub \
    && dart --version && pub --version \
    && apt-get purge --auto-remove -y wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir /app

# Copy project files
COPY . /app

# Set working directory
WORKDIR /app

# Enable web support
RUN flutter config --enable-web

# Get Flutter packages
RUN flutter pub get

# Build the Flutter web app
RUN flutter build web --release --web-renderer html

# Use a smaller base image for the final stage
FROM ubuntu:latest AS final

# Install necessary packages for serving the web app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the built web app from the builder stage
COPY --from=builder /app/build/web /var/www/html

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]