# Image Downloader Plus

Enhanced version of sczhengyabin's Image Downloader. Added another invocation layer to the original features to provide features that can better help you out with your image crawling task.

## Highlights

- Supports loading keywords directly from `.xlsx`, `.xls`, `.csv`, `.tsv`, and even standard input piped from another application.
- Filter image by type and minimum resolution.
- Auto-retry to get the desired number of images.
- Sort images according to criteria.
- Customize filename prefix.

## Command

The command includes command from sczhengyabin's Image Downloader as well as the command provided in this Image Downloader Plus. The command may seem daunting. But don't be afraid, there aren't much arguments you need to specify. I recommend jumping directly to the next section on examples

```bash
usage: crawl.py [-h] [--engine {Google,Bing,Baidu}] [--driver {chrome_headless,chrome,phantomjs}] [--max-number MAX_NUMBER] [--num-threads NUM_THREADS]
                [--timeout TIMEOUT] [--output OUTPUT] [--safe-mode] [--face-only] [--proxy_http PROXY_HTTP] [--proxy_socks5 PROXY_SOCKS5]
                [--type {clipart,linedrawing,photograph}] [--color COLOR] [--engines STRING] [--keywords STRING] [--format-filter STRING] [--file DIR]    
                [--input-type {txt,csv,tsv,excel,stdin,cmd}] [--begin INT] [--end INT] [--column-index INT] [--column-name STRING] [--exclude-header]     
                [--max-attempts INT] [--required-number INT] [--file-prefix STRING] [--images-format STRING] [--images-quality INT] [--min-dim STRING]    
                [--sort STRING] [--echo-only] [--remove-extra] [--starting-number INT] [--verbose] [--include-index] [--remove-duplicate] [--debug-mode]  
                [stdin]

Image Downloader

positional arguments:
  stdin

optional arguments:
  -h, --help            show this help message and exit
  --engine {Google,Bing,Baidu}, -e {Google,Bing,Baidu}
                        Image search engine.
  --driver {chrome_headless,chrome,phantomjs}, -d {chrome_headless,chrome,phantomjs}
                        Image search engine.
  --max-number MAX_NUMBER, -n MAX_NUMBER
                        Maximum number of images to download for the keywords.
  --num-threads NUM_THREADS, -j NUM_THREADS
                        Number of threads to concurrently download images.
  --timeout TIMEOUT, -t TIMEOUT
                        Seconds to timeout when download an image.
  --output OUTPUT, -o OUTPUT
                        Output directory to save downloaded images.
  --safe-mode, -S       Turn on safe search mode. (Only effective in Google)
  --face-only, -F       Only search for
  --proxy_http PROXY_HTTP, -ph PROXY_HTTP
                        Set http proxy (e.g. 192.168.0.2:8080)
  --proxy_socks5 PROXY_SOCKS5, -ps PROXY_SOCKS5
                        Set socks5 proxy (e.g. 192.168.0.2:1080)
  --type {clipart,linedrawing,photograph}, -ty {clipart,linedrawing,photograph}
                        What kinds of images to download.
  --color COLOR, -cl COLOR
                        Specify the color of desired images.
  --engines STRING      Engine names separated by comma (,). Overrides the --engine option.
  --keywords STRING, -k STRING
                        Keywords separated by comma (,).
  --format-filter STRING
                        case insensitive formats separated by comma (,)
  --file DIR, -f DIR    Path to the input file.
  --input-type {txt,csv,tsv,excel,stdin,cmd}
                        File type (default: inferred).
  --begin INT           The beginning row number (excluding the header row).
  --end INT             The last row number (default to the last row).
  --column-index INT    The index of the desired column.
  --column-name STRING  The name of the desired column.
  --exclude-header      Exclude the header from the input file.
  --max-attempts INT    Maximum number of attempts allowed to get the required number of images.
  --required-number INT
                        Required number of images to download for the keywords (default: any).
  --file-prefix STRING  File prefix (default: current keyword).
  --images-format STRING
                        The format of output images. Default: not converted.
  --images-quality INT  Only required when --images-format is specified. (Default: 95 when --images-format is specifed)
  --min-dim STRING      Minimum dimension of the image (default: none)
  --sort STRING         The criteria for sorting (default: rank,asc). Example: resolution,desc
  --echo-only           Only output the keywords in comma-separated format.
  --remove-extra        Only keep the minimum number of images.
  --starting-number INT
                        Your preference of the starting number (default: 1).
  --verbose             Show debug information.
  --include-index       Include the index in the folder name.
  --remove-duplicate    Remove duplicate images.
  --debug-mode          Show debug information (not recommended).
```

## Examples





