# Flutter/Dart

To deploy a Flutter app written in Dart on a Docker container from a local Linux machine, you'll need to create a Dockerfile, build the Docker image, and then run the container.

The Dockerfile will define the environment, copy your project files, and execute Flutter commands to build and run your application.

## Example: Dockerfile

```
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

```
3. Steps

Ensure your Flutter project is set up and you can run it locally using flutter run -d <device> command.

Flutter Web is unique in that it follows web standards.

3.1. Write the Dockerfile

Put the above Dockerfile in your Flutter app's root directory.

Use a multi-stage Dockerfile.

Use Nginx or an alternative web server for serving the Flutter app.

3.2. Create .dockerignore file

Create a .dockerignore file to ignore files not needed:

```

    build/
    .dart_tool/
    .git/
    .gitignore
    .idea/
    .packages
    .pub/
    test/

```
3.3. Build the Docker image

Navigate to the root directory of your Flutter project.

Build your app inside the Docker container.

```

    $ docker build -t flutter-web-app .

```

Replace flutter-web-app with a name for your image.

3.4. Run the Docker container

```

    $ docker run -d -p 8080:80 flutter-web-app

```
4. Build configurations

Configure ports and ignore unnecessary files.

Flutter channel:

Use a stable channel unless you need beta/dev.

Port mapping:

Map the desired host port to the Docker container (-p 8080:80).

Environment variables:

Pass secrets/config as env vars if needed.

Multi-stage build:

Recommended for small images.

Persistent data:

Use Docker volumes if the app needs to write persistent data.

Production assets:

Ensure flutter build web or your target is correct.

Access your web app

Open http://localhost:8080 in your browser.

References

Build and release a web app

https://docs.flutter.dev/deployment/web#deploying-to-web-server








