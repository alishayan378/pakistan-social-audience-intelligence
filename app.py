from pathlib import Path
import re
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).parent
POST_REQUIRED = ["post_id", "brand", "platform", "campaign", "content_type", "product_category", "likes", "comments_count", "shares", "views", "days_since_post"]
COMMENT_REQUIRED = ["post_id", "comment_text", "language_type"]
TOPICS = {
    "Price": ["price", "cost", "rate", "qeemat", "mehnga", "expensive", "kitne", "pkr"],
    "Fabric quality": ["fabric", "quality", "kapra", "lawn", "cotton", "material", "stitch", "stitched"],
    "Sizing": ["size", "sizing", "sleeve", "fit", "measurement", "small", "medium", "large"],
    "Delivery": ["delivery", "deliver", "shipping", "courier", "order", "waiting", "dispatch", "karachi delivery"],
    "Discounts": ["discount", "sale", "offer", "promo", "coupon", "kam", "off"],
    "Availability": ["available", "availability", "stock", "restock", "karachi", "lahore", "islamabad"],
    "Purchase interest": ["inbox", "dm", "buy", "order", "chahiye", "want", "purchase", "cod", "send details"],
}

def topic_label(text):
    t = str(text).lower()
    hits = [(sum(1 for w in words if w in t), name) for name, words in TOPICS.items()]
    n, name = max(hits)
    return name if n else "Other / general"

def load_csv(upload, fallback):
    return pd.read_csv(upload) if upload is not None else pd.read_csv(ROOT / fallback)

def validate(df, required, label):
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"{label} file is missing columns: {', '.join(missing)}")
        st.stop()
    return df

st.set_page_config(page_title="Audience & Campaign Intelligence", page_icon="🧵", layout="wide")
st.markdown("<style>.block-container{padding-top:1.5rem}.metric-card{border:1px solid #e9e3dc;border-radius:14px;padding:1rem}</style>", unsafe_allow_html=True)
st.title("🧵 Pakistan Social Audience & Campaign Intelligence")
st.caption("Discover audience needs, content patterns and campaign outliers for Pakistani fashion brands.")
with st.sidebar:
    st.header("Workspace")
    post_file = st.file_uploader("Post records CSV", type="csv", key="posts")
    comment_file = st.file_uploader("Comment records CSV", type="csv", key="comments")
    st.caption("No uploads? The app opens with a synthetic class-demo dataset. It is not real brand data.")
    st.divider()
    st.markdown("**CSV templates**")
    st.download_button("Download posts template", (ROOT / "data/posts_template.csv").read_bytes(), "posts_template.csv", "text/csv")
    st.download_button("Download comments template", (ROOT / "data/comments_template.csv").read_bytes(), "comments_template.csv", "text/csv")

posts = validate(load_csv(post_file, "data/demo_posts.csv"), POST_REQUIRED, "Posts")
comments = validate(load_csv(comment_file, "data/demo_comments.csv"), COMMENT_REQUIRED, "Comments")
for c in ["likes", "comments_count", "shares", "views", "days_since_post"]:
    posts[c] = pd.to_numeric(posts[c], errors="coerce")
posts["shares"] = posts["shares"].fillna(0)
posts["interactions"] = posts[["likes", "comments_count", "shares"]].fillna(0).sum(axis=1)
posts["engagement_rate"] = np.where(posts["views"].gt(0), posts["interactions"] / posts["views"] * 100, np.nan)
posts["interactions_per_post"] = posts["interactions"]
comments["comment_text"] = comments["comment_text"].fillna("").astype(str)
comments = comments[comments["comment_text"].str.strip().ne("")].copy()
comments["topic"] = comments["comment_text"].map(topic_label)
if "sentiment" not in comments: comments["sentiment"] = "Not provided"
if "purchase_intent" not in comments: comments["purchase_intent"] = "Not provided"

source = "Uploaded records" if post_file or comment_file else "Synthetic demonstration data"
if source.startswith("Synthetic"):
    st.warning("Synthetic demonstration data: all posts, metrics and comments shown here are generated examples, not actual measurements from Lahore Loom, Rang Studio or Mehr Pret.")
else:
    st.info("Using uploaded observations. Confirm collection permissions and source provenance before interpreting or sharing results.")

with st.sidebar:
    st.header("Filters")
    def multi(label, col):
        opts = sorted(posts[col].dropna().astype(str).unique())
        return st.multiselect(label, opts, default=opts)
    brands = multi("Brand", "brand"); platforms = multi("Platform", "platform")
    campaigns = multi("Campaign", "campaign"); formats = multi("Content format", "content_type")

filtered = posts[posts.brand.astype(str).isin(brands) & posts.platform.astype(str).isin(platforms) & posts.campaign.astype(str).isin(campaigns) & posts.content_type.astype(str).isin(formats)].copy()
filtered_comments = comments[comments.post_id.astype(str).isin(filtered.post_id.astype(str))].copy()
if filtered.empty:
    st.warning("No posts match those filters. Adjust the selection in the sidebar."); st.stop()

m1,m2,m3,m4 = st.columns(4)
m1.metric("Posts in view", f"{len(filtered):,}")
m2.metric("Comments in view", f"{len(filtered_comments):,}")
m3.metric("Median interactions", f"{filtered.interactions.median():,.0f}")
median_er = filtered.engagement_rate.median()
m4.metric("Median engagement rate", f"{median_er:.2f}%" if pd.notna(median_er) else "Views unavailable")

summary, needs, outliers, actions, records = st.tabs(["Content performance", "Audience needs", "Unusual patterns", "What to do next", "Data"])
with summary:
    st.subheader("Which content attracts attention?")
    metric = st.radio("Compare formats by", ["Interactions per post", "Engagement rate (%)", "Likes", "Comments", "Shares"], horizontal=True)
    col = {"Interactions per post":"interactions", "Engagement rate (%)":"engagement_rate", "Likes":"likes", "Comments":"comments_count", "Shares":"shares"}[metric]
    agg = filtered.groupby("content_type", as_index=False).agg(value=(col,"median"), posts=("post_id","count"))
    fig = px.bar(agg.sort_values("value",ascending=False), x="content_type", y="value", color="content_type", text_auto=".2s", hover_data=["posts"], title=f"Median {metric.lower()} by content type", labels={"content_type":"Content format","value":metric})
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=metric)
    st.plotly_chart(fig, width="stretch")
    st.caption("Engagement rate uses (likes + comments + shares) / views. If views are absent, compare interactions per post; no reach estimate is imputed.")
    trend = filtered.groupby("campaign",as_index=False).agg(posts=("post_id","count"), median_interactions=("interactions","median"), median_engagement=("engagement_rate","median"))
    st.dataframe(trend.sort_values("median_interactions",ascending=False), width="stretch", hide_index=True)

with needs:
    st.subheader("What does the audience want?")
    topic_counts=filtered_comments.topic.value_counts().rename_axis("Audience need").reset_index(name="Comments")
    if topic_counts.empty: st.info("No comments are linked to the selected posts.")
    else:
        c1,c2=st.columns([1,1]); c1.plotly_chart(px.bar(topic_counts.sort_values("Comments"),x="Comments",y="Audience need",orientation="h",color="Audience need",title="Comment themes" ).update_layout(showlegend=False),width="stretch")
        byfmt=filtered_comments.merge(filtered[["post_id","content_type"]],on="post_id",how="left").groupby(["content_type","topic"]).size().reset_index(name="comments")
        c2.plotly_chart(px.density_heatmap(byfmt,x="content_type",y="topic",z="comments",histfunc="sum",title="Needs by content format",labels={"content_type":"Format","topic":"Need"}),width="stretch")
        st.markdown("**Sample comments for context**")
        st.dataframe(filtered_comments.groupby("topic").head(3)[["topic","comment_text","language_type"]],width="stretch",hide_index=True)
    st.markdown("#### Exploratory text clusters")
    k = st.slider("Number of text clusters", 2, 8, 5)
    if len(filtered_comments) >= k:
        corpus=filtered_comments.comment_text.tolist()
        vec=TfidfVectorizer(analyzer="char_wb",ngram_range=(2,5),min_df=2,max_features=4000,sublinear_tf=True)
        try:
            X=vec.fit_transform(corpus)
            actual_k=min(k, max(2, X.shape[0]//2))
            labels=KMeans(n_clusters=actual_k,random_state=17,n_init=10).fit_predict(X)
            term_names=np.array(vec.get_feature_names_out()); rows=[]
            for cl in range(actual_k):
                ix=np.where(labels==cl)[0]; mean=np.asarray(X[ix].mean(axis=0)).ravel(); top=term_names[np.argsort(mean)[-5:][::-1]]
                rows.append({"Cluster":f"Cluster {cl+1}","Comments":len(ix),"Common text patterns":", ".join(top),"Most common need":filtered_comments.iloc[ix].topic.mode().iloc[0]})
            st.dataframe(pd.DataFrame(rows),width="stretch",hide_index=True)
            st.caption("TF-IDF character n-grams with KMeans: useful for exploratory groupings across Roman Urdu/English spelling variations. Review examples before acting.")
        except ValueError as e: st.info(f"Text clustering needs more repeated text patterns: {e}")
    else: st.info("Add more comments to enable text clustering.")

with outliers:
    st.subheader("Which posts differ from comparable posts?")
    peer=st.selectbox("Peer group",["Content format","Platform","Campaign"],index=0)
    peercol={"Content format":"content_type","Platform":"platform","Campaign":"campaign"}[peer]
    score_col="engagement_rate" if filtered.engagement_rate.notna().sum()>=3 else "interactions"
    work=filtered.dropna(subset=[score_col]).copy()
    med=work.groupby(peercol)[score_col].transform("median")
    mad=work.groupby(peercol)[score_col].transform(lambda s: np.median(np.abs(s-np.median(s))))
    work["robust_deviation"]=(work[score_col]-med)/(1.4826*mad.replace(0,np.nan))
    work["robust_deviation"]=work.robust_deviation.replace([np.inf,-np.inf],np.nan).fillna(0)
    work["pattern"] = np.where(work.robust_deviation>=2,"Higher than peers",np.where(work.robust_deviation<=-2,"Lower than peers","Within typical range"))
    flagged=work[work.robust_deviation.abs()>=2].sort_values("robust_deviation",key=abs,ascending=False)
    st.caption(f"Flagging uses robust median absolute deviation within {peer.lower()} groups on {score_col.replace('_',' ')}; flags are prompts to investigate, not proof of a cause.")
    if flagged.empty: st.success("No strong statistical outliers in this filtered view.")
    else: st.dataframe(flagged[["post_id","brand","platform","campaign","content_type",score_col,"robust_deviation","pattern"]],width="stretch",hide_index=True)
    st.plotly_chart(px.scatter(work,x=peercol,y=score_col,color="pattern",hover_data=["post_id","campaign"],title="Post performance relative to its peer group"),width="stretch")

with actions:
    st.subheader("Evidence-based next steps")
    topic_counts=filtered_comments.topic.value_counts()
    top_topics=topic_counts.head(3)
    format_perf=filtered.groupby("content_type").interactions.median().sort_values(ascending=False)
    if len(format_perf):
        best=format_perf.index[0]; st.markdown(f"**Content test:** {best} has the highest median interactions in this selection ({format_perf.iloc[0]:,.0f}). Run a controlled follow-up against the next format, holding product and offer as similar as possible.")
    if len(top_topics):
        for topic,n in top_topics.items():
            advice={"Price":"Test transparent price and value messaging; compare response to a limited, clearly scoped offer.","Fabric quality":"Publish close-up fabric, lining and stitching details; answer quality questions in a pinned FAQ.","Sizing":"Add a clear size chart and fit reference; track size-related questions before and after.","Delivery":"Show delivery timelines, coverage and tracking steps; route delayed-order comments to service follow-up.","Discounts":"Test a time-limited offer against a value-led creative and compare engagement plus purchase inquiries.","Availability":"Post stock and city availability updates; avoid implying availability that inventory cannot confirm.","Purchase interest":"Make the path to order clear (price, sizes, delivery and approved contact route) and measure qualified inquiries.","Other / general":"Review a sample of uncategorized comments and add labels that match repeated customer needs."}.get(topic,"Review a sample of comments to determine the next test.")
            st.markdown(f"**Audience need: {topic} ({n:,} comments).** {advice}")
    else: st.info("No linked comments to generate audience-specific actions.")
    st.markdown("**Service check:** review comments marked Delivery and Purchase interest by post age and respond through the brand's approved support channel.")
    st.markdown("**Measurement:** compare like-for-like posts and track views, interactions, comment themes and qualified inquiries together. This observational data does not establish causation.")

with records:
    st.subheader("Filtered source records")
    st.download_button("Download filtered posts",filtered.to_csv(index=False).encode("utf-8"),"filtered_posts.csv","text/csv")
    st.download_button("Download classified comments",filtered_comments.to_csv(index=False).encode("utf-8"),"classified_comments.csv","text/csv")
    st.dataframe(filtered.drop(columns=["interactions_per_post"],errors="ignore"),width="stretch",hide_index=True)
    st.markdown("**Data quality snapshot**")
    dq=pd.DataFrame({"Field":POST_REQUIRED,"Missing values":[int(filtered[c].isna().sum()) for c in POST_REQUIRED]})
    st.dataframe(dq,width="stretch",hide_index=True)

st.divider()
st.caption("Research note: store source URL, collection date, provenance and applicable reuse permissions with real data. This dashboard does not collect data from social platforms and does not infer causality.")

