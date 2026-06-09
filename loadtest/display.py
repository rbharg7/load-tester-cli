from rich.console import Console
from rich.table import Table
from rich.panel import  Panel
from rich.text import Text

console = Console()

def show_results(url, method, duration, concurrency, stats, histogram):
    console.print()
    console.print(Panel(
        f"[bold]{method}[/bold] {url}",
        title = "Load Test Results",
        border_style = "cyan"
    ))

    console.print(f"  Duration:    {duration}s")
    console.print(f"  Concurrency: {concurrency}")
    console.print(f"  Requests:    {stats['total_requests']}")
    rps = round(stats['total_requests'] / duration, 1)
    console.print(f"  Throughput:  {rps} req/s")
    console.print()

    lat_table = Table(title="Latency", show_header=True, header_style="bold cyan")
    lat_table.add_column("Metric", style="dim")
    lat_table.add_column("Value", justify="right")
    
    lat_table.add_row("Avg", f"{stats['avg_ms']} ms")
    lat_table.add_row("Median", f"{stats['median_ms']} ms")
    lat_table.add_row("P90", f"{stats['p90_ms']} ms")
    lat_table.add_row("P95", f"{stats['p95_ms']} ms")
    lat_table.add_row("P99", f"{stats['p99_ms']} ms")
    lat_table.add_row("Max", f"{stats['max_ms']} ms")
    
    console.print(lat_table)
    console.print()

    status_table = Table(title="Status Codes", show_header=True, header_style="bold cyan")
    status_table.add_column("Code", style="dim")
    status_table.add_column("Count", justify="right")
    status_table.add_column("", justify="left")
    
    total = stats["total_requests"]
    for code, count in sorted(stats["status_codes"].items()):
        pct = round(count / total * 100, 1)
        bar_len = int(pct / 5)
        bar = "█" * bar_len
        color = "green" if 200 <= code < 300 else "yellow" if code == 429 else "red"
        status_table.add_row(str(code), str(count), f"[{color}]{bar}[/{color}] {pct}%")
    
    if stats["errors"] > 0:
        status_table.add_row("ERR", str(stats["errors"]), f"[red]{'█' * int(stats['error_rate_pct'] / 5)}[/red] {stats['error_rate_pct']}%")
    
    console.print(status_table)
    console.print()


    hist_table = Table(title="Latency Distribution", show_header=True, header_style="bold cyan")
    hist_table.add_column("Bucket", style="dim")
    hist_table.add_column("Count", justify="right")
    hist_table.add_column("", justify="left")
    
    for bucket, data in histogram.items():
        bar_len = int(data["pct"] / 3)
        bar = "█" * bar_len
        hist_table.add_row(bucket, str(data["count"]), f"[cyan]{bar}[/cyan] {data['pct']}%")
    
    console.print(hist_table)
    console.print()

