# Deployment of a PHP script for RESTful APIs on a Docker container

1. Choose a PHP image

Select an appropriate PHP base image from Docker Hub.

Choose a version that suits your PHP REST API's requirements (e.g., php:8.1-fpm for PHP-FPM or php:8.1-apache for Apache).

PHP-FPM is generally recommended for production, especially in high-traffic environments, due to its efficiency and scalability compared to mod_php. 

2. Set the working directory

Specify the directory within the container where your application code will reside using the WORKDIR instruction.

3. Copy application files

Copy your PHP scripts and any necessary files (e.g., dependencies, configuration files) from your local machine to the container's working directory using the COPY instruction.

Consider using multi-stage builds to optimize image size by installing dependencies in one stage and copying only the necessary files to the final Docker image.

4. Install dependencies

If your REST API has dependencies, install them using Composer (PHP package manager) within the Dockerfile using the RUN instruction.

Example: 

RUN composer install --no-dev --no-interaction

5. Configure PHP extensions

If your API requires specific PHP extensions, install them using docker-php-ext-install and docker-php-ext-enable.

6. Expose the port

Use the EXPOSE instruction to specify the port your PHP application will listen on (e.g., 80 for Apache or 9000 for PHP-FPM).

Note: EXPOSE doesn't publish the port, it only serves as documentation. You'll need to publish the port when running the container using the -p or --publish flag.

7. Define the entrypoint and command

Set the main command or script to execute when the container starts using the CMD or ENTRYPOINT instruction.

For example, if you're using PHP's built-in web server for testing, you could use CMD ["php", "-S", "0.0.0.0:8000", "index.php"].

8. Build the Docker image

Build the Docker image using the docker build command, specifying a tag for identification.

9. Run the Docker container

Run the Docker container using the docker run command, publishing the port to make your REST API accessible.

Security: 

Avoid running containers as the root user. 

Create a dedicated non-root user and switch to it using the USER instruction.

Use environment variables for sensitive information like database credentials.

## Example: PHP scripts for RESTful APIs on Docker containers

Dockerfile

```

    # Use the official PHP image with Apache
    FROM php:8.2-apache

    # Set the working directory
    WORKDIR /var/www/html

    # Copy the PHP files into the container
    COPY . .

    # Install PHP extensions
    RUN docker-php-ext-install mysqli pdo pdo_mysql

    # Expose the web server port
    EXPOSE 80

    # Start the Apache server
    CMD ["apache2ctl", "-D", "FOREGROUND"]

```