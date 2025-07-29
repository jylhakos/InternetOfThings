# Sentry

JavaScript error monitoring with stack traces. Monitoring a React application with Sentry in a JavaScript environment involves integrating the Sentry SDK to capture errors, performance data, and other relevant events.

1. Prerequisites

A [Sentry account](https://sentry.io/signup/) and [project](https://docs.sentry.io/product/projects/)

Select "React" as the platform when creating the project to ensure platform-specific configurations and features are enabled.

2. Install Sentry SDK

In your React project, install the necessary Sentry packages using npm or yarn tools.

```

$ npm install @sentry/react @sentry/tracing

# or

$ yarn add @sentry/react @sentry/tracing

```
3. Configure Sentry in your React application

Initialize Sentry in your application's lifecycle, typically in your index.js or App.js file.

Retrieve your Sentry DSN (Data Source Name) from your Sentry project settings and use it in the Sentry.init() call.

Configure options like tracesSampleRate for performance monitoring and integrations for additional functionalities.

```

Sentry.init({ dsn: 'https://<key>@sentry.io/<project>',
  // This enables automatic instrumentation (recommended)
  integrations: [Sentry.browserTracingIntegration()],

  // We recommend adjusting this value in production, or using tracesSampler for finer control
  tracesSampleRate: 1.0,

  // Set tracePropagationTargets to control for which URLs distributed tracing should be enabled
  tracePropagationTargets: ['localhost', /^https://yourserver.io/api/],
});

```

**Capture errors and performance**

Sentry automatically captures unhandled exceptions and errors in your React application after initialization.

You can manually capture specific errors or messages using Sentry.captureException() or Sentry.captureMessage().

**Source maps for readable stack traces**

To get human-readable stack traces from minified or transpiled production code, upload source maps to Sentry.

3. Configure Next.js SDK (Optional)

Configure your app automatically by running the Sentry wizard in the root of your project.

```

$ npx @sentry/wizard@latest -i nextjs --saas --org <USER-NAME> --project <PROJECT-NAME>

```

Manual configuration

Alternatively, you can also set up the SDK manually.

If you already have the configuration for Sentry in your application, and just need this project's (javascript-nextjs) DSN.

### References

[JavaScript Error and Performance Monitoring](https://sentry.io/for/javascript/)

[JavaScript SDKs](https://develop.sentry.dev/sdk/platform-specifics/javascript-sdks/)

[sentry-javascript](https://github.com/getsentry/sentry-javascript)

[React](https://docs.sentry.io/platforms/javascript/guides/react/)

