# Internet of Things Security

This repository contains security implementations for IoT applications, focusing on secure authentication and communication protocols.

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [Topics Overview](#topics-overview)
3. [JSON Web Tokens (JWT)](#json-web-tokens-jwt)
   - [What is a JWT?](#what-is-a-jwt)
   - [JWT Structure](#jwt-structure)
   - [How JWTs Work in Node.js](#how-jwts-work-in-nodejs)
   - [JWT Security Best Practices](#jwt-security-best-practices)
   - [JWT Implementation Libraries](#jwt-implementation-libraries)
4. [Transport Layer Security (TLS)](#transport-layer-security-tls)
   - [What is TLS?](#what-is-tls)
   - [TLS Certificates](#tls-certificates)
   - [TLS Implementation](#tls-implementation)
5. [Security Implementation Guide](#security-implementation-guide)
6. [References and Further Reading](#references-and-further-reading)

## Directory Structure

```
Security/
├── JWT/                    # JSON Web Token implementation
│   ├── client/             # React.js frontend application
│   │   ├── src/            # Source code
│   │   │   ├── components/ # React components
│   │   │   └── services/   # API services
│   │   ├── public/         # Static assets
│   │   └── package.json    # Dependencies
│   └── server/             # Go backend server
│       ├── main.go         # Server implementation
│       └── go.mod          # Go modules
└── TLS/                    # Transport Layer Security implementation
    ├── certs/              # SSL/TLS certificates
    ├── tls/                # TLS server implementation
    └── README.md           # TLS documentation
```

## Overview

This repository demonstrates JWT and TLS security aspects for web applications.

### JWT (JSON Web Tokens)
Securing Node.js web applications with JSON Web Tokens for stateless authentication and authorization. The JWT implementation includes both client-side (React.js) and server-side (Go) components, demonstrating secure token generation, validation, and middleware protection.

### TLS (Transport Layer Security)
Implementing HTTPS encryption for secure data transmission. The TLS section covers certificate generation, server configuration, and encrypted communication setup to protect data in transit.

## JSON Web Tokens (JWT)

### What is a JWT?

A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. JWTs are an open standard ([RFC 7519](https://tools.ietf.org/html/rfc7519)) that defines a self-contained way for securely transmitting information between parties as a JSON object.

Key characteristics of JWTs:
- **Compact**: Can be sent through URL, POST parameters, or HTTP headers
- **Self-contained**: Contains all necessary information about the user
- **Digitally signed**: Can be verified and trusted using HMAC algorithm or RSA/ECDSA key pairs

### JWT Structure

A JWT consists of three parts separated by dots (`.`):

```
xxxxx.yyyyy.zzzzz
```

#### Header
Contains metadata about the token:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload
Contains the claims (statements about the user):
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}
```

#### Signature
Ensures the token hasn't been tampered with:
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

### How JWTs Work in Node.js?

#### User Authentication Flow

1. **User Login**: User submits credentials to the server
2. **Token Generation**: Server validates credentials and generates a JWT containing user information
3. **Token Signing**: Server signs the JWT using a secret key
4. **Token Issuance**: Signed JWT is sent back to the client
5. **Subsequent Requests**: Client includes JWT in Authorization header for protected routes
6. **Token Verification**: Server middleware verifies token signature and expiration
7. **Authorization**: Server uses JWT payload to determine user permissions

#### Implementation Steps

##### User Registration and Login
- Hash user passwords using `bcryptjs` before storing them
- Upon successful login, generate a JWT using `jsonwebtoken.sign()`
- Include user-specific information (e.g., user ID) in the payload
- Set appropriate expiration time

##### Protecting Routes
- Create middleware function to extract JWT from request headers
- Verify token authenticity and expiration using `jsonwebtoken.verify()`
- Allow access to protected resources only for valid tokens

### JWT Security Best Practices

#### Secure Secret Key Management
- Store JWT secret key securely in environment variables (`.env` file)
- Never hardcode secret keys in the codebase
- Use strong, randomly generated secret keys
- Rotate secret keys regularly

#### Token Expiration
- Implement appropriate expiration times for JWTs
- Use short-lived access tokens (15-30 minutes)
- Implement refresh token mechanism for longer sessions
- Consider different expiration times for different security levels

#### Middleware for Route Protection
- Utilize middleware in Express.js to verify JWT validity
- Implement consistent error handling for invalid tokens
- Log authentication attempts and failures
- Return appropriate HTTP status codes

#### Password Hashing
- Use strong algorithms like `bcrypt` for password hashing
- Implement proper salt rounds (minimum 10-12)
- Never store plain text passwords
- Validate password strength on registration

#### HTTPS Transmission
- Always transmit JWTs over HTTPS
- Prevent eavesdropping and man-in-the-middle attacks
- Use secure cookie flags when storing tokens in cookies
- Implement proper CORS policies

#### Additional Security Measures
- **Rate Limiting**: Implement rate limiting to prevent brute-force attacks
- **IP Blacklisting**: Block suspicious IP addresses
- **Input Validation**: Validate all user input on both client and server sides
- **Token Blacklisting**: Maintain a blacklist of revoked tokens
- **Audit Logging**: Log all authentication and authorization events

### JWT Implementation Libraries

#### Core Libraries for Node.js

1. **jsonwebtoken**
   - Most popular library for creating and verifying JWTs
   - Supports multiple algorithms (HMAC, RSA, ECDSA)
   - Easy integration with Express.js middleware

2. **Express.js**
   - Web framework for handling routing and middleware
   - Perfect for implementing JWT authentication workflows
   - Extensive middleware ecosystem

3. **dotenv**
   - Manages environment variables securely
   - Keeps sensitive information like JWT secrets out of codebase
   - Simple configuration management

4. **bcryptjs**
   - Secure password hashing library
   - Implements bcrypt algorithm with salt rounds
   - Prevents rainbow table attacks

## Transport Layer Security (TLS)

### What is TLS?

Transport Layer Security (TLS) is a cryptographic protocol designed to provide secure communication over a computer network. TLS is the successor to Secure Sockets Layer (SSL) and is widely used to secure web browsing, email, instant messaging, and voice over IP (VoIP).

Key features of TLS:
- **Encryption**: Protects data in transit from eavesdropping
- **Authentication**: Verifies the identity of communicating parties
- **Integrity**: Ensures data hasn't been tampered with during transmission

### TLS Certificates

TLS certificates are digital certificates that authenticate the identity of a website and enable encrypted connections. They contain:

- **Public Key**: Used for encryption
- **Certificate Authority (CA) Signature**: Validates the certificate's authenticity
- **Domain Information**: Specifies which domains the certificate covers
- **Expiration Date**: When the certificate expires

#### Certificate Types
- **Domain Validated (DV)**: Basic domain ownership validation
- **Organization Validated (OV)**: Validates organization identity
- **Extended Validation (EV)**: Highest level of validation with enhanced verification

### TLS Implementation

#### Certificate Generation
The `certs/` directory contains examples of:
- **Self-signed certificates**: For development and testing
- **Certificate Signing Requests (CSR)**: For production certificates
- **Private keys**: Securely stored encryption keys
- **Certificate chains**: Complete certificate hierarchy

#### Server Configuration
- Configure Node.js HTTPS server with TLS certificates
- Implement proper cipher suites and protocols
- Enable HTTP Strict Transport Security (HSTS)
- Configure certificate pinning for enhanced security

## Security Implementation

### JWT Authentication

1. **Install Dependencies**
   ```bash
   npm install jsonwebtoken bcryptjs dotenv express
   ```

2. **Environment Configuration**
   ```env
   JWT_SECRET=your-super-secure-secret-key
   JWT_EXPIRE_TIME=30m
   ```

3. **User Authentication Middleware**
   ```javascript
   const jwt = require('jsonwebtoken');
   
   const authenticateToken = (req, res, next) => {
     const authHeader = req.headers['authorization'];
     const token = authHeader && authHeader.split(' ')[1];
     
     if (!token) {
       return res.sendStatus(401);
     }
     
     jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
       if (err) return res.sendStatus(403);
       req.user = user;
       next();
     });
   };
   ```

### TLS/HTTPS

1. **Generate Development Certificates**
   ```bash
   openssl genrsa -out private.key 2048
   openssl req -new -key private.key -out certificate.csr
   openssl x509 -req -in certificate.csr -signkey private.key -out certificate.pem
   ```

2. **Configure HTTPS Server**
   ```javascript
   const https = require('https');
   const fs = require('fs');
   
   const options = {
     key: fs.readFileSync('certs/private.key'),
     cert: fs.readFileSync('certs/certificate.pem')
   };
   
   https.createServer(options, app).listen(443);
   ```


## References

### JWT Resources
- [Introduction to JSON Web Tokens](https://www.jwt.io/introduction) - Official JWT introduction and specification
- [Verifying JSON Web Tokens](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html) - AWS guide for JWT verification
- [Control access to HTTP APIs with JWT authorizers in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html) - AWS API Gateway JWT authorization
- [How to secure API Gateway HTTP endpoints with JWT authorizer](https://aws.amazon.com/blogs/security/how-to-secure-api-gateway-http-endpoints-with-jwt-authorizer/) - AWS Security Blog

### TLS Resources
- [TLS Authentication Certificates](https://docs.aws.amazon.com/rds/latest/userguide/UsingWithRDS.SSL.html) - AWS RDS SSL/TLS guide
- [Terminating HTTPS on EC2 instances running Node.js](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/https-singleinstance-nodejs.html) - AWS Elastic Beanstalk HTTPS
- [Node.js HTTPS API](https://nodejs.org/api/https.html) - Official Node.js HTTPS documentation

### Development Resources
- [Get started with Node.js](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/getting-started-nodejs.html) - AWS SDK for JavaScript
- [Setting Credentials in Node.js](https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-credentials-node.html) - AWS credential configuration

### Security Standards
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519) - Official JWT specification
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) - OWASP security guidelines
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - National cybersecurity standards

---
