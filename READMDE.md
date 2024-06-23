# Text-Cluster：借助pyhanlp对新闻标题按议题实现文本聚类

## 背景

利用[HanLp](https://github.com/hankcs/HanLP/wiki/%E6%96%87%E6%9C%AC%E8%81%9A%E7%B1%BB)进行文本聚类，对热榜话题按照议题聚类。这里其实可以把议题理解为主题，例如：

- 议题（主题）：中专女生姜萍闯进全球数学竞赛12强
  - 热榜话题1：北大博士挑战姜萍竞赛题7题仅对1道
  - 热榜话题2：牛津数学女博士评姜萍
  - 热榜话题3：清华数学系博士称赞姜萍
  - ……

实际上，该功能对于专业舆情分析平台来说非常重要。用户可从宏观角度了解来自各大榜单的热点汇聚以及某热点主题的发展脉络。



## 实现逻辑

1. 本项目主要借助了`pyhanlp`库。`pyhanlp`是`HanLP`（一款中文语言处理工具包）的Python接口，其中的`ClusterAnalyzer`类用于进行文本聚类。

   - 创建ClusterAnalyzer实例

     ```python
     ClusterAnalyzer = JClass('com.hankcs.hanlp.mining.cluster.ClusterAnalyzer')
     analyzer = ClusterAnalyzer()
     ```

     PS：HanLP实现文本聚类使用的的编程语言为Java，因此需要加载java类。

2. 将待聚类的文档（我的处理是取了热榜上的每个话题标题和摘要进行分词，去除停用词后取词频Top5的词作为该话题的文档）添加到`ClusterAnalyzer`中。

   ```python
   for i, doc in enumerate(top_words_documents):
       analyzer.addDocument(str(i), doc)
   ```

3. 使用`repeatedBisection`方法执行**重复二分聚类**算法进行文本聚类。这个算法通过递归地将文档集合分成两个子集来创建层次聚类。参数`0.8`是相似度阈值（可自行调节），用于决定文档是否属于同一类。

   ```python
   cluster_result = analyzer.repeatedBisection(0.8)
   ```



## Tips

实际上对于文本聚类任务来说，最终聚类出来的主题是没有主题名的。例如，我在使用`HanLp`完成聚类后：

- Cluster 1：
  - 雷军称小米SU7比他想象的成功3到5倍
  - 陈震称小米SU7赛道撞墙再正常不过
  - 官方将处理无资质小米SU7跑网约车平台
  - 小米SU7断电后冰箱最长工作24小时

即缺一个对下面这四个话题标题的总结性议题名来代替这个没有语义意义的`Cluster 1`。因此，对于这种文本数据的处理，我立刻想到的是借助GPT。所以，我调用了gpt-3.5-turbo接口，调整好prompt后对将聚类后的每一簇下的话题标题作为输入，返回总结这些标题的代表性议题名称。

注意：如果要使用该方法需在[config](./config.json)文件中输入自己的API密钥和代理等信息。当然，如果没有取总结议题名的需求，也可以完成基本的聚类功能。注释下列行即可：

```python
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
```

