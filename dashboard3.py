import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import geodatasets

st.title("E-Commerce Dashboard")
st.write("Sidqi Amanullah")

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

st.sidebar.title("Navigasi dan Filter")
page = st.sidebar.selectbox("Pilih Visualisasi", [
    "Kategori Produk Terlaris",
    "Produk dengan Review Terbanyak",
    "Distribusi Skor Review",
    "Kota dengan Pesanan Terbanyak",
    "Analisis RFM",
    "Analisis Geospasial"
])

start_date = st.sidebar.date_input("Tanggal Mulai", min_value=all_data['order_date'].min().date(), 
                                  max_value=all_data['order_date'].max().date())
end_date = st.sidebar.date_input("Tanggal Selesai", min_value=all_data['order_date'].min().date(), 
                                max_value=all_data['order_date'].max().date())

if 'product_category_name' in all_data.columns:
    categories = all_data['product_category_name'].unique()
    selected_categories = st.sidebar.multiselect("Pilih Kategori Produk", categories)
else:
    st.sidebar.warning("Kolom 'product_category_name' tidak ditemukan.")

if 'customer_state' in all_data.columns:
    states = all_data['customer_state'].unique()
    selected_states = st.sidebar.multiselect("Pilih State", states)
else:
    st.sidebar.warning("Kolom 'customer_state' tidak ditemukan.")

filtered_df = all_data.copy()
filtered_df = filtered_df[(filtered_df['order_date'].dt.date >= start_date) & 
                         (filtered_df['order_date'].dt.date <= end_date)]

if 'product_category_name' in filtered_df.columns and selected_categories:
    filtered_df = filtered_df[filtered_df['product_category_name'].isin(selected_categories)]
if 'customer_state' in filtered_df.columns and selected_states:
    filtered_df = filtered_df[filtered_df['customer_state'].isin(selected_states)]

def replace_customer_labels(df, column, top_n=5):
    sort_ascending = (column == "recency")
    top_customers = df.sort_values(by=column, ascending=sort_ascending).head(top_n)
    mapping = {customer: chr(65 + i) for i, customer in enumerate(top_customers["customer_id"])}
    df["customer_label"] = df["customer_id"].map(mapping)
    return df, mapping

if page == "Kategori Produk Terlaris":
    st.header("Kategori Produk dengan Penjualan Terbanyak")
    category_sales = filtered_df.groupby("product_category_name")["order_id"].count().reset_index()
    category_sales.columns = ["product_category_name", "total_sales"]
    category_sales = category_sales.sort_values(by="total_sales", ascending=False).head(10)

    fig = px.bar(category_sales, x="product_category_name", y="total_sales", 
                 title="Kategori Produk dengan Penjualan Terbanyak",
                 color="product_category_name", color_discrete_sequence=px.colors.sequential.Viridis)
    fig.update_layout(xaxis_title="Kategori Produk", yaxis_title="Jumlah Penjualan", showlegend=False)
    st.plotly_chart(fig)

elif page == "Produk dengan Review Terbanyak":
    st.header("10 Produk dengan Review Terbanyak")
    product_reviews = filtered_df.groupby(["product_id", "product_category_name"]).agg(total_reviews=("review_score", "count")).reset_index()
    most_reviewed_products = product_reviews.sort_values(by="total_reviews", ascending=False).head(10)

    fig = px.bar(most_reviewed_products, x="total_reviews", y="product_id", 
                 title="Top 10 Produk dengan Review Terbanyak",
                 color="product_category_name", color_discrete_sequence=px.colors.sequential.Magma)
    fig.update_layout(xaxis_title="Total Reviews", yaxis_title="Product ID", showlegend=True)
    st.plotly_chart(fig)

elif page == "Distribusi Skor Review":
    st.header("Distribusi Skor Review untuk 3 Produk Teratas")
    product_reviews = filtered_df.groupby(["product_id", "product_category_name"]).agg(total_reviews=("review_score", "count")).reset_index()
    top_3_products = product_reviews.sort_values(by="total_reviews", ascending=False).head(3)["product_id"].tolist()

    fig = px.histogram(filtered_df[filtered_df["product_id"].isin(top_3_products)], 
                       x="review_score", color="product_id", barmode="group",
                       title="Distribusi Skor Review untuk 3 Produk Teratas",
                       color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(xaxis_title="Review Score", yaxis_title="Count", bargap=0.2)
    st.plotly_chart(fig)

elif page == "Kota dengan Pesanan Terbanyak":
    st.header("10 Kota dengan Pesanan Terbanyak")
    city_high = filtered_df.groupby("customer_city")["customer_id"].count().reset_index()
    city_high.columns = ["customer_city", "total_orders"]
    top_10_cities = city_high.sort_values(by="total_orders", ascending=False).head(10)

    fig = px.bar(top_10_cities, x="total_orders", y="customer_city", 
                 title="Top 10 Kota dengan Pesanan Terbanyak",
                 color="customer_city", color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(xaxis_title="Total Orders", yaxis_title="Kota", showlegend=False)
    st.plotly_chart(fig)

elif page == "Analisis RFM":
    st.header("Analisis RFM - Pelanggan Terbaik")

    rfm_df = filtered_df.groupby("customer_id", as_index=False).agg({
        "order_date": "max",
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    recent_date = filtered_df["order_date"].max().date()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x.date()).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    st.write(f"Recent Date: {recent_date}")
    st.write("Top 5 Recency Values:")
    st.write(rfm_df.sort_values(by="recency").head(5))

    fig = px.bar(rfm_df.sort_values(by="recency").head(5), x="customer_id", y="recency", 
                 title="Top 5 Pelanggan Berdasarkan Recency",
                 color="recency", color_continuous_scale="Viridis")
    fig.update_layout(xaxis_title="Customer ID", yaxis_title="Recency (days)", showlegend=False)
    st.plotly_chart(fig)

    fig = px.bar(rfm_df.sort_values(by="frequency", ascending=False).head(5), x="customer_id", y="frequency", 
                 title="Top 5 Pelanggan Berdasarkan Frequency",
                 color="frequency", color_continuous_scale="Magma")
    fig.update_layout(xaxis_title="Customer ID", yaxis_title="Frequency", showlegend=False)
    st.plotly_chart(fig)

    fig = px.bar(rfm_df.sort_values(by="monetary", ascending=False).head(5), x="customer_id", y="monetary", 
                 title="Top 5 Pelanggan Berdasarkan Monetary",
                 color="monetary", color_continuous_scale="Blues")
    fig.update_layout(xaxis_title="Customer ID", yaxis_title="Monetary", showlegend=False)
    st.plotly_chart(fig)

    st.subheader("Mapping Customer ID:")
    for col, mapping in [("Recency", replace_customer_labels(rfm_df, "recency")[1]),
                         ("Frequency", replace_customer_labels(rfm_df, "frequency")[1]),
                         ("Monetary", replace_customer_labels(rfm_df, "monetary")[1])]:
        st.write(f"{col}:")
        for customer, label in mapping.items():
            st.write(f"{label} → {customer}")

elif page == "Analisis Geospasial":
    st.header("Distribusi Pembelian Berdasarkan Kota")

    city_orders = (filtered_df.groupby("customer_city")["customer_id"]
                   .count()
                   .reset_index()
                   .sort_values(by="customer_id", ascending=False)
                   .head(10))
    city_orders.columns = ["customer_city", "total_orders"]

    fig = px.bar(city_orders, x="total_orders", y="customer_city", 
                 title="10 Kota dengan Pesanan Terbanyak",
                 color="total_orders", color_continuous_scale="Blues_r")
    fig.update_layout(xaxis_title="Jumlah Pesanan", yaxis_title="Kota", showlegend=False)
    st.plotly_chart(fig)

    st.subheader("Peta Sebaran Pesanan")
    m = folium.Map(location=[-23.5475, -46.6361], zoom_start=4) 

    geo_data = filtered_df[["geolocation_lat", "geolocation_lng"]].dropna()
    heat_data = [[row["geolocation_lat"], row["geolocation_lng"], 1] for _, row in geo_data.iterrows()]

    if heat_data:
        HeatMap(heat_data, radius=15).add_to(m)
        sao_paulo_data = filtered_df[filtered_df["customer_city"] == "sao paulo"]
        if not sao_paulo_data.empty:
            lat_sp = sao_paulo_data["geolocation_lat"].mean()
            lng_sp = sao_paulo_data["geolocation_lng"].mean()
            total_orders_sp = city_orders[city_orders["customer_city"] == "sao paulo"]["total_orders"].values[0]
            folium.Marker(
                [lat_sp, lng_sp],
                popup=f"Sao Paulo: {total_orders_sp} orders",
                icon=folium.Icon(color="red")
            ).add_to(m)
        st_folium(m, width=725, height=500)  
    else:
        st.write("Data geolokasi tidak tersedia untuk heatmap.")