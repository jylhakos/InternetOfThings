# Dart and Flutter for Web

To create a web application with Dart and Flutter, you'll need to set up your development environment, create a Flutter project.

1. Setting up the environment

Install Dart and Flutter: 

Follow the official installation guides for Dart and Flutter SDKs.

IDE/Editor:

Choose a code editor like VS Code or Android Studio with Flutter and Dart plugins.

2. Creating a Flutter Web project:

New project: 

Use the command flutter create my_web_app in your terminal to create a new Flutter project.

Navigate: 

Change directory to your newly created project: 

```

$ cd my_web_app.


```
3. Create the UI

Flutter's declarative UI:

Use Flutter's widgets (like Scaffold, Column, Row, etc.) to build your user interface. 

Styling:

Utilize Flutter's theming and styling options to create a visually appealing interface.

Responsive layouts:

Employ MediaQuery and LayoutBuilder to make your app adapt to different screen sizes. 

4. Running the app:

Target device: 

Use flutter run -d web to run your app in a web browser.

5. Navigation and routing

Navigator: 

Use Flutter's Navigator and MaterialPageRoute to manage navigation between different screens or pages.

6. State management

Provider or Riverpod: 

Consider using state management packages like provider or riverpod to handle the state of your application.

7. Data fetching

HTTP package:

Use the http package to make API calls and fetch data from external sources. 

8. Building and deploying:

Build:

Before you can build a web application with Flutter, make sure that you have the [Flutter SDK](https://docs.flutter.dev/get-started/install).

Use flutter build web to create a production build of your web application.

This populates a build/web directory with built files, including an assets directory, which need to be served together.

Deployment:

Deploy your web app using a web server (e.g., Python's http.server or a dedicated server).

## How to deploy Flutter app for Web on Google's Firebase Hosting?

Deploying to Firebase Hosting

You can use the Firebase CLI to build and release your Flutter app with [Firebase Hosting](https://firebase.google.com/docs/hosting/frameworks/flutter).

## How to deploy Flutter app for Web on AWS?

To deploy a Flutter web app on AWS, you can use a combination of services like AWS Amplify, S3, CloudFront, and CodePipeline.

An approach involves building the web application, storing it in an S3 bucket, and then serving it through a CloudFront distribution for availability.

## How to deploy Flutter app for Web on AWS with S3 and CloudFront?

To deploy a Flutter web app on AWS using S3 and CloudFront, you'll first build your Flutter project for the web, then upload the build/web output to an S3 bucket, and finally, serve the content through a CloudFront distribution.

Using S3 and CloudFront:

Build your Flutter web app: Use flutter build web to generate the web build. 

Create an S3 bucket: 

Create a new S3 bucket in your AWS account and configure it for static website hosting.

Upload your build: 

Upload the contents of your /build/web directory to the S3 bucket.

Create a CloudFront distribution: 

Create a CloudFront distribution to serve your static website from the S3 bucket.

Configure CloudFront: 

Point the CloudFront distribution to your S3 bucket as the origin and configure caching and other settings as needed. 

1. Build the Flutter Web app

Navigate to your Flutter project's root directory.

```

    $ flutter build web
    
```

The flutter build command generates a build/web directory containing the compiled HTML, CSS, JavaScript, and other assets for your web application.

2. Create an S3 bucket

To interact with AWS S3 on a Linux, you can use the AWS Command Line Interface (AWS CLI). 

First, install the AWS CLI and configure it with your AWS credentials. 

Install the AWS CLI:

Open a terminal on your Ubuntu system.

Update the package list: 

```

    $ sudo apt update
    
```
Install pip (if you don't have it): sudo apt install python3-pip

Install the AWS CLI: 

```

    $ pip3 install awscli

```

Configure the AWS CLI:

Run the aws configuration command.

```

    $ aws configure


```

Enter your AWS Access Key ID, Secret Access Key, default region name, and default output format when prompted.

Then, you can use commands like aws s3 ls to list buckets, aws s3 cp to copy files, and aws s3 sync to synchronize directories between your local system and S3. 

Interact with S3:

List Buckets: 

```

    $ aws s3 ls 

```

List contents of a bucket: 

```

    $ aws s3 ls s3://<bucket-name> 


```

Upload a file to S3: 

```

    $ aws s3 cp <local-file-path> s3://<bucket-name>/<destination-path> 


```

Example to download a file named my_data.csv from a S3 bucket called my-bucket to your current directory:

```

$ aws s3 cp s3://my-bucket/my_data.csv .


```

Open the AWS S3 console.

Create a new bucket.

Configure the bucket:

Bucket Name: 

Choose a unique name. 

Consider using a name related to your application or domain.

Region: 

Select the region closest to your users or where you want your infrastructure to be located.

Domain:

You can use a custom domain with CloudFront by configuring Route 53 and associating it with your CloudFront distribution. 

Block all public access: 

Temporarily disable this setting for now, as you'll need to make your bucket publicly accessible to serve the website. 

You'll reconfigure this later for security.

Security:

Ensure you configure appropriate permissions for your S3 bucket and CloudFront distribution to prevent unauthorized access.

Other settings: 

Accept the default settings for the rest of the configuration options.

Enable Static Website Hosting:

Go to the "Properties" tab of your bucket.

Find the "Static website hosting" section and click "Edit".

Enable static website hosting.

Set the "Index document" to index.html (or your app's entry point).

Set the "Error document" to index.html (or your error page).

Save the changes. 

3. Upload your Flutter Web app to S3

Use the AWS CLI or an S3 browser to upload the contents of the build/web directory to your S3 bucket.

```

    $ aws s3 cp build/web s3://your-bucket-name/ --recursive --acl public-read

```
Replace your-bucket-name with the actual name of your S3 bucket. 

The --acl public-read flag makes the uploaded files publicly accessible.

4. Create a CloudFront distribution

Open the AWS CloudFront console.

Create a new distribution.

Configure the distribution:

Origin Domain Name: 

Select your S3 bucket from the dropdown.

Origin Path: 

Leave it blank if your app is at the root of the bucket, otherwise, specify the path to your app's directory within the bucket.

Viewer Protocol Policy: 

Choose "Redirect HTTP to HTTPS" for security.

Allowed HTTP Methods: 

Select GET, HEAD, OPTIONS.

Cache Policy: 

You can use the default cache policy for now, but you may want to customize it for better performance.

Object Caching: 

You can configure the cache behavior here.

Compress objects automatically: 

Enable this to reduce bandwidth usage.

Alternate Domain Names (CNAMEs): 

If you have a custom domain, add it here.

SSL Certificate: 

If you have a custom domain, you'll need to create an ACM certificate and associate it with your CloudFront distribution.

Default Root Object: 

Set it to index.html

5. Configure S3 Bucket permissions

Go back to your S3 bucket in the AWS console.

Edit the bucket policy:

Find the bucket policy section and click "Edit".

Add a bucket policy that allows CloudFront to access your bucket.

Edit placeholders with your bucket name and CloudFront distribution ID.

References

Building a web application with Flutter

https://docs.flutter.dev/platform-integration/web/building

Build and release a web app

https://docs.flutter.dev/deployment/web

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
