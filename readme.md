# Linkage Disequilibrium web scraper

## About

This program is used as an automation tool that generates a Linkage Disequilibrium matrix from the **Ensambl** database service -> https://www.ensembl.org/index.html

## Usage

Use `settings.json` to define settings of the app.

- thread_count: Number of threads to use for scraping
- page_load_seconds: Minimum number of seconds to account for when loading each page + additional estimate.
    - Program will try to continue the process as soon as possible, and this will not slow the process down.
- input_file_path: Input Excel file path
- outpu_file_path: Output Excel file path
- starting_url: Url of the main page of Ensambl
    - Default: https://www.ensembl.org/index.html
- do_end_checkup: After finishing the initial run, try to redo all unset values
- options: Edge Web driver options

```json
{
    "thread_count": 1,
    "page_load_seconds": 30,
    "input_file_path": "./input/rsid_values__.xlsx",
    "output_file_path": "./output/output_toscani.xlsx",
    "starting_url": "https://www.ensembl.org/index.html",
    "population": "Toscani in Italy",
    "do_end_checkup": "true",
    "options": [
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--log-level=3",
        "--disable-crash-reporter",
        "--disable-in-process-stack-traces",
        "--output=/dev/null"
    ]
}
```



### WebDriver

In order for Selenium to work, a WebDriver is required. As this program uses Edge as the main browser, Edge WebDriver of sufficient version must be downloaded.

Edge WebDriver download link: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

> [!NOTE]
> Make sure that the WebDriver is always up to date

#### Setup

- Download webdriver from the provided link
- Place the contents of the zip into a folder (eg. `./WebDriver/EdgeWebDriver`)
- Make sure that environment path points to the web driver folder (eg. `./WebDriver/EdgeDriver`)
    - Press windows button (seach for 'Edit the System Envirnonment Variables')
    - Press 'Envirnomnent variables' button
    - In the new window, look at the bottom list ('System Variables' should be enabled for edit and new...)
    - Find path (select and press new)
    - Paste the path to the web driver
    - OK


### Dependencies

`pip install selenium openpyxl pandas`

App should be started from `main.py`

### Excel

Input excel should have no formatting applied to it (paste 'Match destination formating' or 'Paste without format'). In 'A' column, place all the rsid values (starting from row 2). In the first row, add 'rsid' as the value (representing the rsid column).

#### Table representation below

|#| A |
| -- | -- |
|1| rsid |
|2| r123 |
|3| r223 |
|4| r333 |
|5| ... |
