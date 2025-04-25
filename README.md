# fix-price-scraper

![Workflow Status](https://github.com/Polodashvili-Iosif/fix-price-scraper/actions/workflows/main.yml/badge.svg)

A Scrapy-based web scraper for Fix Price to collect product data by categories.

### Installation:

Cloning the repository:

```bash
git clone https://github.com/Polodashvili-Iosif/fix-price-scraper.git
```

Navigate to the project directory:

```bash
cd fix-price-scraper
```

Create and activate a virtual environment:


For Unix/MacOS
```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows
```bash
python -m venv venv
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
playwright install
```

### Usage:
Navigate to the Scrapy project directory:

```bash
cd fix_price_scraper
```

Run the scraper for a specific category:

```bash
scrapy crawl fix_price -a categories="https://fix-price.com/catalog/krasota-i-zdorove/dlya-volos" -O output.json
```

This will scrape product data from the specified category and save it to `output.json`.

You can specify multiple categories by separating them with commas:

```bash
scrapy crawl fix_price -a categories="https://fix-price.com/catalog/krasota-i-zdorove/dlya-volos, https://fix-price.com/catalog/igrushki/igrovye-nabory-nastolnye-igry" -O products.json
```

### Output:

The scraper outputs data in JSON format.

Example:

```json
[
  {
    "timestamp": 1745598064,
    "RPC": "3225164",
    "url": "https://fix-price.com/catalog/krasota-i-zdorove/p-3225164-maska-dlya-volos-loresan-450-ml-v-assortimente",
    "title": "Маска для волос, Floresan, 450 мл, в ассортименте",
    "marketing_tags": [
      "По карте «Fix Price»"
    ],
    "brand": "Floresan",
    "section": [
      "Красота",
      "Для волос"
    ],
    "price_data": {
      "current": 99.0,
      "original": 116.0,
      "sale_tag": "Скидка 14%"
    },
    "stock": {
      "in_stock": true,
      "count": 925
    },
    "assets": {
      "main_image": "https://img.fix-price.com/800x800/_marketplace/images/origin/d1/d173c1e736f1af3ec225b989f304ff38.jpg",
      "set_images": [
        "https://img.fix-price.com/800x800/_marketplace/images/origin/d1/d173c1e736f1af3ec225b989f304ff38.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/e4/e480a356901d5565efad60f7a149a9c2.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/3f/3f8d50d475e7f84ef2e454995fc68616.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/db/db17a7c794b96a46db72d403610be1b7.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/f3/f33c5a515456087423a36565ea6f0f88.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/fc/fc469be90c08c1d817b3c46df4c0e8b9.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/eb/ebfeffea4e3fee70e4cdb7daa9463b27.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/6c/6c98292ec2ca1b5959c693eb45abda5d.jpg",
        "https://img.fix-price.com/800x800/_marketplace/images/origin/0d/0dd2e0fa75f2a9ecdfc9283e94af0559.jpg"
      ],
      "view360": [],
      "video": []
    },
    "metadata": {
      "Ширина, мм.": "105",
      "Высота, мм.": "70",
      "Длина, мм.": "105",
      "Вес, гр.": "480",
      "Страна производства": "Россия",
      "__description": "Маска для волос, Floresan, предназначена для дополнительного ухода за волосами. Выберите средство исходя из желаемого результата. Перед использованием ознакомьтесь с инструкцией и мерами предосторожности на упаковке. Объём: 450 мл. Товар представлен в ассортименте."
    },
    "variants": null
  },
  ...
]
```