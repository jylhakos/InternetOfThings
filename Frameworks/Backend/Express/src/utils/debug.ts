import debug from 'debug';

/**
 * Creates a debug instance with a given namespace
 * @param namespace - The debug namespace
 * @returns Debug instance
 */
export const createDebug = (namespace: string) => {
    return debug(namespace);
};

/**
 * Debug logger for different levels
 */
export class DebugLogger {
    private debugInfo = debug('info');
    private debugWarn = debug('warn');
    private debugError = debug('error');

    info(message: string, ...args: any[]) {
        this.debugInfo(message, ...args);
    }

    warn(message: string, ...args: any[]) {
        this.debugWarn(message, ...args);
    }

    error(message: string, ...args: any[]) {
        this.debugError(message, ...args);
    }
}

/**
 * Performance measurement utility
 */
export class PerformanceTimer {
    private startTime: [number, number];
    private label: string;

    constructor(label: string) {
        this.label = label;
        this.startTime = process.hrtime();
    }

    end(): number {
        const [seconds, nanoseconds] = process.hrtime(this.startTime);
        const duration = seconds * 1000 + nanoseconds / 1000000;
        debug(`perf:${this.label}`)(`Completed in ${duration.toFixed(2)}ms`);
        return duration;
    }
}

/**
 * Memory usage tracker
 */
export const getMemoryUsage = () => {
    const usage = process.memoryUsage();
    return {
        rss: Math.round(usage.rss / 1024 / 1024 * 100) / 100,
        heapTotal: Math.round(usage.heapTotal / 1024 / 1024 * 100) / 100,
        heapUsed: Math.round(usage.heapUsed / 1024 / 1024 * 100) / 100,
        external: Math.round(usage.external / 1024 / 1024 * 100) / 100
    };
};

/**
 * Request/Response debugging utility
 */
export const debugRequest = (req: any) => {
    const requestDebug = debug('request');
    requestDebug('Incoming request:', {
        method: req.method,
        url: req.url,
        headers: req.headers,
        params: req.params,
        query: req.query,
        body: req.body
    });
};

export default createDebug;
