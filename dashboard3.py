import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium  
import geodatasets

st.title("E-Commerce Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("all_data.csv")
    df["order_date"] = pd.to_datetime(df["order_purchase_timestamp"])
    geolocation_df = pd.read_csv("geo_dataset_fix.csv")
    geolocation_df = geolocation_df.drop_duplicates(subset=["geolocation_city"])
    df = pd.merge(df, geolocation_df[["geolocation_city", "geolocation_lat", "geolocation_lng"]], 
                  left_on="customer_city", right_on="geolocation_city", how="left")
    return df
all_data = load_data()

st.sidebar.title("Navigasi")
page = st.sidebar.selectbox("Pilih Visualisasi", [
    "Kategori Produk Terlaris",
    "Produk dengan Review Terbanyak",
    "Distribusi Skor Review",
    "Kota dengan Pesanan Terbanyak",
    "Analisis RFM",
    "Analisis Geospasial"
])

def replace_customer_labels(df, column, top_n=5):
    sort_ascending = (column == "recency")
    top_customers = df.sort_values(by=column, ascending=sort_ascending).head(top_n)
    mapping = {customer: chr(65 + i) for i, customer in enumerate(top_customers["customer_id"])}
    df["customer_label"] = df["customer_id"].map(mapping)
    return df, mapping

if page == "Kategori Produk Terlaris":
    st.header("10 Kategori Produk dengan Penjualan Terbanyak")
    category_sales = all_data.groupby("product_category_name")["order_id"].count().reset_index()
    category_sales.columns = ["product_category_name", "total_sales"]
    category_sales = category_sales.sort_values(by="total_sales", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="total_sales", y="product_category_name", data=category_sales, hue="product_category_name", palette="viridis", legend=False, ax=ax)
    ax.set_xlabel("Jumlah Penjualan")
    ax.set_ylabel("Kategori Produk")
    ax.set_title("10 Kategori Produk dengan Penjualan Terbanyak")
    ax.invert_yaxis()
    st.pyplot(fig)

elif page == "Produk dengan Review Terbanyak":
    st.header("10 Produk dengan Review Terbanyak")
    product_reviews = all_data.groupby(["product_id", "product_category_name"]).agg(total_reviews=("review_score", "count")).reset_index()
    most_reviewed_products = product_reviews.sort_values(by="total_reviews", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=most_reviewed_products, x="total_reviews", y="product_id", hue="product_category_name", palette="magma", legend=False, ax=ax)
    ax.set_xlabel("Total Reviews")
    ax.set_ylabel("Product ID")
    ax.set_title("Top 10 Produk dengan Review Terbanyak")
    st.pyplot(fig)

elif page == "Distribusi Skor Review":
    st.header("Distribusi Skor Review untuk 3 Produk Teratas")
    product_reviews = all_data.groupby(["product_id", "product_category_name"]).agg(total_reviews=("review_score", "count")).reset_index()
    top_3_products = product_reviews.sort_values(by="total_reviews", ascending=False).head(3)["product_id"].tolist()

    fig, ax = plt.subplots(figsize=(12, 6))
    for product in top_3_products:
        review_counts = all_data[all_data["product_id"] == product]["review_score"].value_counts()
        sns.barplot(x=review_counts.index, y=review_counts.values, label=f"Product ID {product}", ax=ax)
    ax.set_xlabel("Review Score")
    ax.set_ylabel("Count")
    ax.set_title("Distribusi Skor Review untuk 3 Produk Teratas")
    ax.legend()
    st.pyplot(fig)

elif page == "Kota dengan Pesanan Terbanyak":
    st.header("10 Kota dengan Pesanan Terbanyak")
    city_high = all_data.groupby("customer_city")["customer_id"].count().reset_index()
    city_high.columns = ["customer_city", "total_orders"]
    top_10_cities = city_high.sort_values(by="total_orders", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="total_orders", y="customer_city", data=top_10_cities, hue="customer_city", palette="Blues_r", legend=False, ax=ax)
    ax.set_xlabel("Total Orders")
    ax.set_ylabel("Customer City")
    ax.set_title("Top 10 Kota dengan Pesanan Terbanyak")
    st.pyplot(fig)

elif page == "Analisis RFM":
    st.header("Analisis RFM - Pelanggan Terbaik")

    rfm_df = all_data.groupby("customer_id", as_index=False).agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    recent_date = all_data["order_date"].max().date()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x.date()).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    st.write(f"Recent Date: {recent_date}")
    st.write("Top 5 Recency Values:")
    st.write(rfm_df.sort_values(by="recency").head(5))

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
    colors = ["#72BCD4"] * 5

    rfm_df_recency, recency_mapping = replace_customer_labels(rfm_df.copy(), "recency")
    top_recency = rfm_df_recency.dropna(subset=["customer_label"]).sort_values(by="recency")
    sns.barplot(y="recency", x="customer_label", hue="customer_label", data=top_recency,
                palette=colors, legend=False, ax=ax[0])
    ax[0].set_title("By Recency (days)", fontsize=18)
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis='x', labelsize=15)
    ax[0].set_ylim(0, rfm_df["recency"].max() * 1.1 - 700)

    rfm_df_freq, frequency_mapping = replace_customer_labels(rfm_df.copy(), "frequency")
    top_frequency = rfm_df_freq.dropna(subset=["customer_label"]).sort_values(by="frequency", ascending=False)
    sns.barplot(y="frequency", x="customer_label", hue="customer_label", data=top_frequency,
                palette=colors, legend=False, ax=ax[1])
    ax[1].set_title("By Frequency", fontsize=18)
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis='x', labelsize=15)
    ax[1].set_ylim(0, rfm_df["frequency"].max() * 1.1)

    rfm_df_mon, monetary_mapping = replace_customer_labels(rfm_df.copy(), "monetary")
    top_monetary = rfm_df_mon.dropna(subset=["customer_label"]).sort_values(by="monetary", ascending=False)
    sns.barplot(y="monetary", x="customer_label", hue="customer_label", data=top_monetary,
                palette=colors, legend=False, ax=ax[2])
    ax[2].set_title("By Monetary", fontsize=18)
    ax[2].set_xlabel(None)
    ax[2].set_ylabel(None)
    ax[2].tick_params(axis='x', labelsize=15)
    ax[2].set_ylim(0, rfm_df["monetary"].max() * 1.1)

    plt.suptitle("Pelanggan Terbaik Berdasarkan Parameter RFM", fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    st.pyplot(fig)

    st.subheader("Mapping Customer ID:")
    st.write("Recency:")
    for customer, label in recency_mapping.items():
        st.write(f"{label} → {customer}")
    st.write("Frequency:")
    for customer, label in frequency_mapping.items():
        st.write(f"{label} → {customer}")
    st.write("Monetary:")
    for customer, label in monetary_mapping.items():
        st.write(f"{label} → {customer}")

elif page == "Analisis Geospasial":
    st.header("Distribusi Pembelian Berdasarkan Kota")

    city_orders = (all_data.groupby("customer_city")["customer_id"]
                   .count()
                   .reset_index()
                   .sort_values(by="customer_id", ascending=False)
                   .head(10))
    city_orders.columns = ["customer_city", "total_orders"]

    fig4, ax4 = plt.subplots(figsize=(12, 6))
    sns.barplot(x="total_orders", y="customer_city", 
                hue="customer_city", data=city_orders,
                palette="Blues_r", legend=False, ax=ax4)  
    ax4.set_xlabel("Jumlah Pesanan")
    ax4.set_ylabel("Kota")
    ax4.set_title("10 Kota dengan Pesanan Terbanyak")
    st.pyplot(fig4)

    st.subheader("Peta Sebaran Pesanan")
    m = folium.Map(location=[-23.5475, -46.6361], zoom_start=4) 

    geo_data = all_data[["geolocation_lat", "geolocation_lng"]].dropna()
    heat_data = [[row["geolocation_lat"], row["geolocation_lng"], 1] for _, row in geo_data.iterrows()]

    if heat_data:
        HeatMap(heat_data, radius=15).add_to(m)
        sao_paulo_data = all_data[all_data["customer_city"] == "sao paulo"]
        if not sao_paulo_data.empty:
            lat_sp = sao_paulo_data["geolocation_lat"].mean()
            lng_sp = sao_paulo_data["geolocation_lng"].mean()
            total_orders_sp = city_orders[city_orders["customer_city"] == "sao paulo"]["total_orders"].values[0]
            folium.Marker(
                [lat_sp, lng_sp],
                popup=f"Sao Paulo: {total_orders_sp} orders",
                icon=folium.Icon(color="red")
            ).add_to(m)
        st_folium(m)  
    else:
        st.write("Data geolokasi tidak tersedia untuk heatmap.")