import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        st.text("✅ File successfully read!")
        st.text_area("📜 File Preview", data[:1000])

        df = preprocessor.preprocess(data)

        if df.empty:
            st.error("🚨 Parsed dataframe is empty or improperly formatted. Please check the file format.")
        else:
            user_list = df['user'].unique().tolist()

            if 'group_notification' in user_list:
                user_list.remove('group_notification')

            user_list.sort()
            user_list.insert(0, "Overall")

            selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

            if st.sidebar.button("Show Analysis"):
                num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

                st.title("Top Statistics")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.header("Total Messages")
                    st.title(num_messages)
                with col2:
                    st.header("Total Words")
                    st.title(words)
                with col3:
                    st.header("Media Shared")
                    st.title(num_media_messages)
                with col4:
                    st.header("Links Shared")
                    st.title(num_links)

                st.title("Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                st.title("Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                st.title('Activity Map')
                col1, col2 = st.columns(2)

                with col1:
                    st.header("Most busy day")
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                with col2:
                    st.header("Most busy month")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                st.title("Weekly Activity Map")
                user_heatmap = helper.activity_heatmap(selected_user, df)

                if not user_heatmap.empty:
                    fig, ax = plt.subplots()
                    sns.heatmap(user_heatmap, ax=ax, cmap="coolwarm")
                    st.pyplot(fig)
                else:
                    st.warning("No data available for heatmap.")

                if selected_user == 'Overall':
                    st.title('Most Busy Users')
                    x, new_df = helper.most_busy_users(df)

                    col1, col2 = st.columns(2)
                    with col1:
                        fig, ax = plt.subplots()
                        ax.bar(x.index, x.values, color='red')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)

                    with col2:
                        st.dataframe(new_df)

                st.title("Wordcloud")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(df_wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)

                st.title('Most Common Words')
                most_common_df = helper.most_common_words(selected_user, df)

                if not most_common_df.empty:
                    fig, ax = plt.subplots()
                    ax.barh(most_common_df.iloc[:, 0], most_common_df.iloc[:, 1], color='blue')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.warning("No common words found.")

                st.title("Emoji Analysis")
                emoji_df = helper.emoji_helper(selected_user, df)

                if not emoji_df.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(emoji_df)

                    with col2:
                        fig, ax = plt.subplots()
                        ax.pie(emoji_df.iloc[:5, 1], labels=emoji_df.iloc[:5, 0], autopct="%0.2f")
                        st.pyplot(fig)
                else:
                    st.warning("No emoji data available.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
