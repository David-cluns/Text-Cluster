import pandas as pd
from pyhanlp import *
from collections import Counter
import os
from openai import OpenAI
import json

with open("config.json", "r") as file:
    config = json.load(file)

os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
os.environ['http_proxy'] = config["http_proxy"]
os.environ['https_proxy'] = config["https_proxy"]
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get(config["OPENAI_API_KEY"]),
    base_url=config["base_url"]
)

def use_gpt(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion

def generate_cluster_title(titles):
    
    combined_titles = "\n".join(titles)
    prompt = f"""
    这些是同一个议题下的不同话题标题，请生成一个总结这些标题的代表性中文议题名称，字数不超过10,不要出现“议题”两个字:
    {combined_titles}
    """
    chat_completion=use_gpt(prompt)
    result = chat_completion.choices[0].message.content
    return result


# titles = ['雷军称小米SU7比他想象的成功3到5倍','陈震称小米SU7赛道撞墙再正常不过','官方将处理无资质小米SU7跑网约车平台','小米SU7断电后冰箱最长工作24小时']
# print(generate_cluster_title(titles))


ClusterAnalyzer = JClass('com.hankcs.hanlp.mining.cluster.ClusterAnalyzer')
# 读取数据
file_path = './hottopics_summary.xlsx'
hot_topics = pd.read_excel(file_path)

# 选择‘摘要’列和‘标题’列
summaries = hot_topics['摘要'].dropna()
titles = hot_topics.loc[summaries.index, '标题']  # 确保标题与摘要索引对应

# 确保标题与摘要索引对应
titles = titles.loc[summaries.index]
summaries = summaries.loc[titles.index]


# 定义预处理和分词函数
def preprocess(text):
    if not isinstance(text, str):
        text = str(text)
    # 使用 HanLP 分词
    document = HanLP.segment(text)
    # 提取分词结果，忽略单字
    words = [term.word for term in document if len(term.word.strip()) > 1]
    return words

# 合并标题和摘要，并应用预处理，计算词频并选取词频最高的5个词
top_words_documents = []
for title, summary in zip(titles, summaries):
    combined_text = title + " " + summary
    words = preprocess(combined_text)
    # 计算词频
    word_counts = Counter(words)
    # 选择词频最高的5个词
    top_words = [word for word, count in word_counts.most_common(5)]
    top_words_documents.append(" ".join(top_words))
    # print(f"标题: {title}")
    # print(f"摘要: {summary}")
    # print(f"Top 5 Words: {top_words}")
    # print("\n")



# 创建 ClusterAnalyzer 实例
analyzer = ClusterAnalyzer()
for i, doc in enumerate(top_words_documents):
    analyzer.addDocument(str(i), doc)

# 使用 repeatedBisection 自动进行聚类
cluster_result = analyzer.repeatedBisection(0.8)
print("自动检测到的聚类数量:", len(cluster_result))
for cluster_id, cluster in enumerate(cluster_result):
    print(f"Cluster {cluster_id + 1}:")
    cluster_titles = [titles.iloc[int(doc)] for doc in cluster]
    # 生成并打印这一簇的代表性标题
    # if cluster_titles:  # 确保簇中有标题
    #     representative_title = generate_cluster_title(cluster_titles)
    #     print(f"议题 {cluster_id + 1}: {representative_title}")
    for title in cluster_titles:
        print(title)  # 打印每一簇包含的标题
    print("\n")   
    
    # # 生成并打印这一簇的代表性标题
    # if cluster_titles:  # 确保簇中有标题
    #     representative_title = generate_cluster_title(cluster_titles)
    #     print(f"聚类议题 {cluster_id + 1}: {representative_title}")
    # print("\n")