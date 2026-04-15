import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_handler import load_data, get_data_summary
from core.agent import get_agent, analyze_query

# Set page configuration using default robust theme
st.set_page_config(page_title="AI Data Analyst Assistant", page_icon="🤖", layout="wide")

def local_css():
    """Inject safe, non-overlapping attractive CSS for a premium look."""
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Attractive Top Header without changing text visibility */
        .premium-header {
            background: linear-gradient(90deg, #1f77b4 0%, #00d2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Make Metric columns look like premium cards */
        [data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.05);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* Subtle divider styling */
        hr {
            border: 0;
            height: 1px;
            background: rgba(128, 128, 128, 0.2);
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    local_css()
    
    st.markdown('<div class="premium-header">🤖 AI Data Analyst Assistant</div>', unsafe_allow_html=True)
    st.write("Easily explore, analyze, and conditionally interact with your datasets using state-of-the-art Generative AI.")

    # Sidebar for file upload
    with st.sidebar:
        st.header("1. Upload Data")
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx', 'xls'])
        
        st.markdown("---")
        st.header("2. AI Configuration")
        import os
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            api_key = st.text_input("Google Gemini API Key", type="password", placeholder="Paste your API key here...")
            if not api_key:
                st.info("ℹ️ Please enter your Gemini API Key to unlock AI capabilities.")
            
        st.markdown("---")
        st.success("✅ **AI Model Active:** The AI Dataframe Agent is ready.")
        st.info("💡 **Tip:** Upload your data to instantly unlock intelligent charts and insights.")

    if uploaded_file is not None:
        with st.spinner("Loading dataset securely into memory..."):
            df, error = load_data(uploaded_file)
            
        if error:
            st.error(error)
            st.stop()
            
        # Initialize the AI Agent securely
        try:
            agent = get_agent(df, api_key=api_key)
        except Exception as e:
            st.error(f"Error starting AI logic: {e}")
            st.stop()

        # Interactive Tabs for Data Exploration
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📈 Statistics", "📊 Visualizations", "💬 Data Chat"])
        
        with tab1:
            st.subheader("Dataset High-Level metrics")
            summary = get_data_summary(df)
            
            # Display Premium metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rows", f"{summary['rows']:,}")
            col2.metric("Total Columns", summary["columns"])
            col3.metric("Missing Values", summary["missing_values"])
            col4.metric("Duplicate Rows", summary["duplicates"])
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Data Preview (Head)")
            st.dataframe(df.head(100), use_container_width=True)
            
            st.subheader("Column Types & Missing Data")
            dtypes_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Missing Values": df.isnull().sum()
            }).reset_index(drop=True)
            st.dataframe(dtypes_df, use_container_width=True)

        with tab2:
            st.subheader("Descriptive Numerical Statistics")
            if len(summary["numeric_cols"]) > 0:
                st.dataframe(df.describe().T, use_container_width=True)
            else:
                st.info("No numeric columns found to generate standard statistics.")

        with tab3:
            st.subheader("Interactive Plotly Visualizations")
            st.write("Hover over data points to see details. Drag to zoom in.")
            
            if len(summary["numeric_cols"]) > 0:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown("**Chart Settings**")
                    plot_type = st.selectbox("Select Plot Type", ["Histogram", "Scatter Plot", "Box Plot", "Correlation Heatmap"])
                    
                with col2:
                    try:
                        if plot_type == "Histogram":
                            selected_col = st.selectbox("Select Column:", summary["numeric_cols"])
                            fig = px.histogram(df, x=selected_col, template="plotly_white", color_discrete_sequence=['#1f77b4'], marginal="box")
                            st.plotly_chart(fig, use_container_width=True)
                            
                        elif plot_type == "Scatter Plot":
                            if len(summary["numeric_cols"]) >= 2:
                                sc1, sc2, sc3 = st.columns(3)
                                col_x = sc1.selectbox("X-axis variable", summary["numeric_cols"], index=0)
                                col_y = sc2.selectbox("Y-axis variable", summary["numeric_cols"], index=1)
                                plot_hue = sc3.selectbox("Hue (Category)", ["None"] + summary["categorical_cols"])
                                
                                hue_val = None if plot_hue == "None" else plot_hue
                                
                                fig = px.scatter(df, x=col_x, y=col_y, color=hue_val, template="plotly_white", opacity=0.7)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("Scatter plots require at least two numeric variables.")
                                
                        elif plot_type == "Correlation Heatmap":
                            st.write("Correlation Matrix for numeric variables:")
                            corr_matrix = df[summary["numeric_cols"]].corr()
                            fig = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", template="plotly_white", color_continuous_scale="RdBu_r")
                            st.plotly_chart(fig, use_container_width=True)
                            
                        elif plot_type == "Box Plot":
                            bx1, bx2 = st.columns(2)
                            col_y = bx1.selectbox("Variable for Box Plot", summary["numeric_cols"])
                            plot_x = bx2.selectbox("Grouping variable (Category)", ["None"] + summary["categorical_cols"])
                            
                            x_val = None if plot_x == "None" else plot_x
                            
                            fig = px.box(df, x=x_val, y=col_y, template="plotly_white", color=x_val)
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error rendering plot: {e}")
            else:
                st.warning("No numeric columns available for visualization.")

        with tab4:
            st.subheader("💬 AI Data Chat")
            st.markdown("Ask complex analytical questions and our internal generative model will manipulate and interpret the data for you.")
            
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
                # Add welcome message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Hi! I am the AI Data Analyst. Ask me complex queries like 'what is the average sales by region?'!"
                })
            
            # Display chat history
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # Chat input for generative AI
            if prompt := st.chat_input("E.g., 'What trends do you see in the data?'"):
                # Record user input
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                # Process and respond using Langchain Agent
                with st.chat_message("assistant"):
                    with st.spinner("AI is analyzing your dataset..."):
                        response = analyze_query(agent, prompt)
                        st.markdown(response)
                        
                st.session_state.messages.append({"role": "assistant", "content": response})

    else:
        # Welcome Screen if no file is uploaded
        st.info("👋 Upload a dataset in the sidebar to begin analyzing with AI!")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🤖 Intelligent Insights")
            st.markdown("Instantly uncover trends, compute statistical summaries, and extract actionable insights from your raw data.")
        with col2:
            st.markdown("### 🛠️ Automated Cleaning")
            st.markdown("Automatically identify missing values, and handle messy data sets with intelligent guidance.")
        with col3:
            st.markdown("### 📊 Interactive Visuals")
            st.markdown("Generate stunning, hoverable charts and graphs to quickly understand correlations and patterns.")

if __name__ == "__main__":
    main()
