Debugging TypeScript on Linux can be done through several methods depending on your preferred environment (terminal vs. IDE).

Debugging in Terminal

For a quick, CLI-based approach without manual compilation, use runtime wrappers that handle TypeScript on the fly.

Using ts-node: This allows you to run scripts directly. To debug, use the Node.js --inspect flag with the ts-node register.

Using ts-node:

```

# Install if you haven't
npm install -D ts-node typescript

# Run in debug mode
node --inspect -r ts-node/register your-script.ts

```

Using tsx:

```

npx tsx --inspect your-script.ts

```



References

Running TypeScript with a runner" https://nodejs.org/learn/typescript/run

Debugging TypeScript https://code.visualstudio.com/docs/typescript/typescript-debugging






