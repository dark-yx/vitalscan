declare module 'http-cache-semantics' {
    export class CachePolicy {
        constructor(req: any, res: any, options?: any);
        static fromObject(obj: any): CachePolicy;
        storable(): boolean;
        satisfiesWithoutRevalidation(req: any): boolean;
        responseHeaders(): any;
        timeToLive(): number;
        toObject(): any;
    }
} 