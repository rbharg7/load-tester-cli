import click
import asyncio
import json
from loadtest.runner import LoadRunner
from loadtest.stats import StatsCollector
from loadtest.display import show_results 


@click.command()
@click.argument("url")
@click.option("--method", "-m", default="GET", help="HTTP method (GET, POST, PUT, DELETE)")
@click.option("--body", "-b", default=None, help="Request body (JSON string)")
@click.option("--header", "-H", multiple=True, help="Headers (key:value)")
@click.option("--concurrency", "-c", default=10, help="Concurrent connections")
@click.option("--duration", "-d", default=5, help="Test duration in seconds")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def main(url, method, body, header, concurrency, duration, json_output):

    headers = {"Content-Type": "application/json"}
    for h in header:
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    
    click.echo(f"Loading {method} {url}")
    click.echo(f"  {concurrency} connections, {duration}s duration")
    click.echo()
    
    # Run the async load test
    runner = LoadRunner(
        url=url,
        method=method.upper(),
        headers=headers,
        body=body,
        concurrency=concurrency,
        duration=duration
    )
    
    results = asyncio.run(runner.run())

    collector = StatsCollector(results)
    stats = collector.summary()
    histogram = collector.histogram()
    
    if json_output:
        click.echo(json.dumps({"stats": stats, "histogram": histogram}, indent=2))
    else:
        show_results(url, method.upper(), duration, concurrency, stats, histogram)

if __name__ == "__main__":
    main()
