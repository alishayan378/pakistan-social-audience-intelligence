# Pakistan Social Audience & Campaign Intelligence Engine

A Streamlit dashboard for exploring audience needs and campaign patterns for Pakistani fashion brands. The bundled demo data is **synthetic** and is clearly marked in the app; it is not measured data from any named brand. Import properly collected public post/comment records to analyze real observations.

## Run in VS Code

1. Open this folder in VS Code.
2. Open a terminal and create an environment: `python -m venv .venv`
3. Activate it on Windows: `.venv\\Scripts\\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the dashboard: `streamlit run app.py`

## Features

- Compare content formats by likes, comments, shares, views and normalized engagement.
- Discover comment themes (price, fabric, sizing, delivery, discounts, availability, purchase intent) using TF-IDF and KMeans, with rule-based topic labels for readable summaries.
- Surface unusual posts using robust median/MAD scores against the selected peer group.
- Review audience segments and evidence-linked marketing recommendations.
- Filter by brand, platform, campaign and content format; export filtered records and analysis tables.
- Upload post and comment CSV files using the templates in `data/`.

## Data files and schema

`data/demo_posts.csv` and `data/demo_comments.csv` contain generated examples for demonstration only.

Post CSV required columns: `post_id,brand,platform,campaign,content_type,product_category,likes,comments_count,shares,views,days_since_post`

Comment CSV required columns: `post_id,comment_text,language_type` (optional: `sentiment,purchase_intent`)

Use blank values for metrics that are not available. The app does not scrape platforms or fetch private analytics. Keep source URL, collection date, provenance and reuse permissions with any research dataset you prepare. Check platform terms and dataset license before collection or redistribution.

## Methods and limitations

Engagement rate is calculated as `(likes + comments + shares) / views * 100` when views are present; otherwise the app displays interactions per post and does not invent a reach denominator. Comment themes use unsupervised text clustering and keyword labels, so clusters are exploratory and can be imperfect on short Roman Urdu or Urdu text. Anomalies are statistical prompts for investigation, not proof of fraud or campaign success. Recommendations describe tests to run, not causal conclusions.
