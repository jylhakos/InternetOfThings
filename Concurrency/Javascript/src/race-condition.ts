import fs from 'fs';
import path from 'path';
import { Worker, isMainThread } from 'worker_threads';

// The account file acts as shared memory between all concurrent cash machine workers.
// __dirname points to dist/ after compilation, so the account file lands in the project root.
const ACCOUNT_FILE = path.join(__dirname, '..', 'account');
const TRANSACTIONS_PER_MACHINE = 100;
const NUMBER_OF_CASH_MACHINES = 5;

// Suppose all the cash machines share a single bank account, stored in a file named 'account'
function readBalance(): number {
  return parseFloat(fs.readFileSync(ACCOUNT_FILE).toString());
}

function writeBalance(balance: number): void {
  fs.writeFileSync(ACCOUNT_FILE, balance.toString());
}

function deposit(): void {
  let balance = readBalance();
  balance = balance + 1;
  writeBalance(balance);
}

function withdraw(): void {
  let balance = readBalance();
  balance = balance - 1;
  writeBalance(balance);
}

if (!isMainThread) {
  // Worker thread: simulates one cash machine.
  // Each deposit/withdraw pair should leave the balance unchanged, but
  // concurrent interleaving with other workers will cause a race condition.
  for (let i = 0; i < TRANSACTIONS_PER_MACHINE; ++i) {
    deposit(); // put a dollar in
    withdraw(); // take it back out
  }
} else {
  // Main thread: initialise the shared account and spawn worker cash machines.
  const initialBalance = 200;
  writeBalance(initialBalance);
  console.log(`Initial balance: $${initialBalance}`);
  console.log(
    `Running ${NUMBER_OF_CASH_MACHINES} cash machines, ` +
      `each doing ${TRANSACTIONS_PER_MACHINE} deposit/withdraw cycles...`
  );

  let completed = 0;

  for (let i = 0; i < NUMBER_OF_CASH_MACHINES; ++i) {
    // Spawning a worker with __filename re-executes this compiled .js file.
    // Inside the worker, isMainThread is false, so the worker branch runs.
    const worker = new Worker(__filename);

    worker.on('error', (err: Error) => {
      console.error(`Worker ${i} error:`, err.message);
    });

    worker.on('exit', () => {
      completed++;
      if (completed === NUMBER_OF_CASH_MACHINES) {
        const finalBalance = readBalance();
        console.log(`\nFinal balance:   $${finalBalance}`);

        if (finalBalance === initialBalance) {
          console.log('Result: CORRECT - Balance unchanged as expected.');
        } else {
          const diff = finalBalance - initialBalance;
          console.log(
            `Result: RACE CONDITION detected - balance changed by $${diff}`
          );
          console.log(
            'Explanation: Concurrent workers interleaved their read/write operations.'
          );
        }

        // Clean up the shared account file after the demonstration
        if (fs.existsSync(ACCOUNT_FILE)) {
          fs.unlinkSync(ACCOUNT_FILE);
        }
      }
    });
  }
}
