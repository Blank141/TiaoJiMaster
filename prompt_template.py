from langchain.output_parsers import ResponseSchema, StructuredOutputParser, CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

input_response_schemas = [
    ResponseSchema(
        name="政治或管理类综合成绩", 
        description="这个字段表示考生的政治或管理类综合成绩，类型为整型。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="外国语成绩", 
        description="这个字段表示考生的外国语成绩，类型为整型。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="业务课一成绩", 
        description="这个字段表示考生的业务课一成绩或数学成绩，类型为整型。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="业务课二成绩", 
        description="这个字段表示考生的业务课二成绩或专业课成绩，类型为整型。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="总分", 
        description="这个字段表示考生的总分，类型为整型。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="报考单位", 
        description="这个字段表示考生的报考单位，类型为字符串。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="报考专业", 
        description="这个字段表示考生的报考专业，类型为字符串。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="报考学院", 
        description="这个字段表示考生的报考学院，类型为字符串。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="target_school", 
        description="这个字段表示考生想要调剂到的学校，类型为字符串。若考生没有提供该信息，则该字段为空。"
    ),
    ResponseSchema(
        name="target_major", 
        description="这个字段表示考生想要调剂到的专业，类型为字符串。若考生没有提供该信息，则该字段为空。"
    )
]

input_template = "你现在是一位专业的分析师，你需要分析考生的情况，根据考生提供的信息输出考生的客观信息和主观信息，客观信息包含考生的各科成绩，报考院校及专业，主观信息包含考生的想要调剂到的学校，专业等。按照python字典格式输出。只输出考生的主观信息和客观信息，不要涉及无关的内容。\n{format_instructions}\n{input}"

keyword_template = "根据考生提供的主观信息包含调剂学校:{target_school} 和调剂专业:{target_major}这两个信息生成3-8个检索关键词组,以空格间隔,例如:输入:调剂学校:厦门大学 调剂专业:计算机 生成检索关键词组：厦门大学计算机调剂 厦门大学信息学院调剂 厦门大学人工智能调剂 厦门大学计算机调剂政策。只输出检索关键词组，禁止涉及无关的内容。"

ouput_template = """只根据以下信息提供调剂建议:
{context}

考生情况: {situation}

可能的调剂建议示例:
该考生的总分为400,高于北京大学计算机科学与技术专业的录取分数线350
北京大学计算机科学与技术专业在2023年有十个调剂名额,名额较多
该考生的报考学院为人工智能学院,与北京大学计算机科学与技术专业接近或相同
综上所述,建议该考生调剂到北京大学计算机科学与技术专业
北京大学计算机科学与技术专业的调剂政策为:...
北京大学计算机学院的官网链接为:...
"""