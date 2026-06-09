import numpy as np

class StatsCollector:

    def __init__(self, results: list[dict]):

        self.results = results
        self.latencies = [r["latency_ms"] for r in results]
        self.errors = 0 
        self.status_codes = {}

        for r in results:
            if r["error"]:
                self.errors += 1
            else: 
                code = r["status"]
                self.status_codes[code] = self.status_codes.get(code, 0) + 1

    def summary(self) -> dict:
        if not self.latencies:
            return {}
        
        arr = np.array(self.latencies)

        return {
            "total_requests" : len(arr), 
            "successful":  len(arr) - self.errors,
            "errors": self.errors,
            "error_rate_pct" : round(self.errors * 100 / len(arr), 2),
            "avg_ms": round(np.mean(arr), 2),
            "median_ms": round(np.median(arr), 2),
            "p90_ms": round(np.percentile(arr, 90), 2),
            "p95_ms": round(np.percentile(arr, 95), 2),
            "p99_ms": round(np.percentile(arr, 99), 2),
            "min_ms": round(np.min(arr), 2),
            "max_ms": round(np.max(arr), 2),
            "status_codes": dict(self.status_codes),

        }

    def histogram(self) -> dict: 

        buckets = [0, 10, 25, 50, 100, 250, 500, 1000]
        arr = np.array(self.latencies)
        hist = {}

        for i in range(len(buckets) - 1):
            low,high = buckets[i], buckets[i+1]
            count = int (np.sum((arr >= low) & (arr  < high)))
            pct = round(count/len(arr)*100, 1)
            hist[f"{low}-{high}ms"] = {"count": count, "pct": pct} 
            
        count = int(np.sum(arr >= buckets[-1]))
        pct = round(count / len(arr) * 100, 1)
        hist[f"{buckets[-1]}ms+"] = {"count": count, "pct": pct}
        
        return hist