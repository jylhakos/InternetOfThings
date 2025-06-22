# Angular application on Docker container

An example of an Angular application fetching data from a Node.js web server involves using Angular's HttpClient to make HTTP requests to a Node.js API endpoint.

Angular application

Create the api.service.ts, app.component.ts, and app.component.html files and add the Angular code.

Service

```

    import { Injectable } from '@angular/core';
    import { HttpClient } from '@angular/common/http';
    import { Observable } from 'rxjs';

    // Define an interface for the expected data structure (optional but recommended)
    export interface Device {
      id: number;
      name: string;
      // ... other properties
    }

    @Injectable({
      providedIn: 'root'
    })
    export class ApiService {
      private apiUrl = 'http://localhost:3000/devices'; // URL of your Node.js API endpoint

      constructor(private http: HttpClient) {}

      getDevices(): Observable<Device[]> {
        return this.http.get<Device[]>(this.apiUrl);
      }
    }

```
Component

```

    import { Component, OnInit } from '@angular/core';
    import { ApiService, Device } from './api.service';

    @Component({
      selector: 'app-root',
      templateUrl: './app.component.html',
      styleUrls: ['./app.component.css']
    })
    export class AppComponent implements OnInit {
      devices: Device[] = [];
      errorMessage: string = '';

      constructor(private apiService: ApiService) {}

      ngOnInit(): void {
        this.fetchDevices();
      }

      fetchDevices(): void {
        this.apiService.getDevices().subscribe({
          next: (data) => {
            this.devices = data;
          },
          error: (error) => {
            this.errorMessage = 'Error fetching devices: ' + error.message;
            console.error('There was an error!', error);
          }
        });
      }
    }

```
Component Template

```

    <h1>Device List</h1>
    <div *ngIf="errorMessage" class="error-message">{{ errorMessage }}</div>
    <ul>
      <li *ngFor="let device of devices">
        {{ device.name }} (ID: {{ device.id }})
      </li>
    </ul>

```

Run the Angular application 

```

    $ ng serve

```

Node.js server

Create a server.js file and add the Node.js code.

```

    const express = require('express');
    const cors = require('cors'); // Required for handling Cross-Origin Resource Sharing

    const app = express();
    const port = 3000;

    app.use(cors()); // Enable CORS for all routes

    // Example data
    const devices = [
      { id: 1, name: 'Smartphone' },
      { id: 2, name: 'Laptop' },
      { id: 3, name: 'Tablet' }
    ];

    app.get('/devices', (req, res) => {
      res.json(devices);
    });

    app.listen(port, () => {
      console.log(`Node.js server listening at http://localhost:${port}`);
    });

```
Install Express and CORS: 

```

    $ npm install express cors

```
Run the Node.js server

```

    $ node server.js

```

1. Compile your Angular application

Execute the ng build command to build the application in production mode.

```

    $ ng build --configuration=production

```

The ng build command compiles your Angular application, optimizes it for production, and places the build artifacts (e.g., HTML, CSS, JavaScript files) in the dist/your-app-name/browser directory.

2. Create a Dockerfile

Employ a multi-stage build to minimize the final image size.

Build stage: 

Use a Node.js image to install dependencies and build the Angular application.

Serve stage: 

Use a lightweight web server image (e.g., Nginx) to serve the compiled Angular application.

```

    # Stage 1: Build the Angular application
    FROM node:lts-alpine as builder
    WORKDIR /app
    COPY package.json package-lock.json ./
    RUN npm install
    COPY . .
    RUN npm run build -- --configuration production

    # Stage 2: Run the Angular application with Nginx
    FROM nginx:alpine
    COPY --from=builder /app/dist/your-app-name /usr/share/nginx/html
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]

```
Replace your-app-name with the actual name of your Angular project as it appears in the dist directory.

3. Configure Nginx file

Create a file named nginx.conf in the root of your Angular project.

```

    server {
        listen 80;
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
    }

```
The configuration file for Nginx to run an Angular application is located at /etc/nginx/nginx.conf.

The Nginx configuration for an Angular application include:

Server block:

Defines the virtual host for the Angular application, including the port it listens on (e.g., listen 80;).

Root directive:

Specifies the directory where the built Angular application's static files (HTML, CSS, JavaScript) are located (e.g., root /usr/share/nginx/html;).

Index directive:

Defines the default file to be served when a directory is requested, which is typically index.html for Angular applications (e.g., index index.html;).

Try_files directive:

This is essential directive for handling Angular's client-side routing. 

Try_files ensures that if a requested URI does not directly map to a file or directory, Nginx will serve the index.html file, allowing Angular's router to handle the routing (e.g., try_files $uri $uri/ /index.html =404;). 

Try_files prevents 404 errors for direct access to sub-routes within the Angular application.

4. Create a .dockerignore file

Create a file named .dockerignore in the root of your project to exclude unnecessary files and directories from the Docker image, such as node_modules directory.

```

    node_modules
    .git
    .angular
    tmp

```
5. Build the Docker image

Navigate to the root of your Angular project in your terminal.

```

    $ docker build -t your-angular-app-image .

```
Replace your-angular-app-image with a descriptive name for your Docker image.

The . indicates that the Dockerfile is in the current directory.

6. Run the Docker container

```

    $ docker run -d -p 8080:80 --name your-angular-app-container your-angular-app-image

```
The docker run command runs the container in detached mode (-d), maps port 8080 on your host to port 80 inside the Docker container.

7. Test Angular application

Open your web browser and navigate to http://localhost:8080 (or the port you mapped) to access your Angular application running inside the Docker container.
