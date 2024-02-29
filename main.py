import os

from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.language_models.chat_models import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser, CommaSeparatedListOutputParser
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from Data.fetch_data import search_keyword, read_web_data
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter
from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter

from prompt_template import input_response_schemas, input_template, keyword_template, ouput_template

os.environ["QIANFAN_AK"] = "QIANFAN_AK"
os.environ["QIANFAN_SK"] = "QIANFAN_SK"

llm = QianfanChatEndpoint(
    streaming=True,
    model="ERNIE-Bot",
)
embed = QianfanEmbeddingsEndpoint()


#STEP 1: 输入考生信息及调剂需求
print("请输入你的信息包含你的各科成绩，报考院校及专业等信息以及你想要调剂到的院校及专业方向信息。\n例如：\n政治或管理类综合成绩  70 外国语成绩  80 业务课一成绩/数学  86 业务课二成绩/专业课  120总分  356报考单位 南京大学(10284)报考专业 计算机科学与技术(081200)报考学院 人工智能学院, 我想要调剂到国内985院校的计算机相关专业")

input_info = "政治或管理类综合成绩  70 外国语成绩  80 业务课一成绩/数学  86 业务课二成绩/专业课  120总分  356报考单位 南京大学(10284)报考专业 计算机科学与技术(081200)报考学院 人工智能学院, 我想要调剂到厦门大学的计算机相关专业"

dict_output = StructuredOutputParser.from_response_schemas(input_response_schemas)
format_instructions = dict_output.get_format_instructions()
input_prompt = PromptTemplate(
    template=input_template,
    input_variables=["input"],
    partial_variables={"format_instructions": format_instructions},
)
input_chain = input_prompt | llm | dict_output
input_res = input_chain.invoke({"input": input_info})
print(input_res)

#STEP 2: 搜索调剂信息
list_output = CommaSeparatedListOutputParser()
format_instructions = list_output.get_format_instructions()
keyword_prompt = PromptTemplate(
    template=keyword_template,
    input_variables=["target_school", "target_major"],
    partial_variables={"format_instructions": format_instructions},
)

search_chain = keyword_prompt | llm | list_output

if input_res["target_school"] or input_res["target_major"]:
    search_keywords = search_chain.invoke({"target_school": input_res["target_school"], "target_major": input_res["target_major"]})
    for keyword in search_keywords:
        Links = search_keyword(keyword, 5)

## 将WebData存入LocalData中的向量数据库, 清空WebData文件夹    
web_data = "./Data/WebData"
docs = read_web_data(web_data)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 100,
    chunk_overlap  = 0,
    length_function = len,
)
texts = []
for doc in docs:
    texts = texts + text_splitter.split_text(doc)
vector = FAISS.from_texts(texts, embed)
vector.save_local(folder_path="./Data/LocalData",index_name="db")
db = FAISS.load_local(folder_path="./Data/LocalData", index_name="db", embeddings=embed)

#STEP 3:匹配调剂信息，输出调剂建议及理由 
retriever = db.as_retriever()
ouput_prompt = ChatPromptTemplate.from_template(ouput_template)

output_chain = (
    {
        "context": itemgetter("situation") | retriever,
        "situation": itemgetter("situation"),
    }
    | ouput_prompt
    | llm
    | StrOutputParser()
)
res = output_chain.invoke({"situation": "政治或管理类综合成绩  70 外国语成绩  80 业务课一成绩/数学  86 业务课二成绩/专业课  120总分  356报考单位 南京大学(10284)报考专业 计算机科学与技术(081200)报考学院 人工智能学院"})
print(res)