import os
import json
from openai import OpenAI
from openpyxl import load_workbook
import re
from volcenginesdkarkruntime import Ark

wb_question= load_workbook(r"C:\Users\zhutao\Desktop\TeleMom_question.xlsx")
wb_answer = load_workbook(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
wb_adjudicate = load_workbook(r"C:\Users\zhutao\Desktop\TeleMom_adjudicate.xlsx")

ws_question = wb_question['Sheet1']
ws_answer = wb_answer['Sheet1']
ws_adjudicate = wb_adjudicate['Sheet1']

pattern = r'\{[^}]*\}'#正则表达式，以确保输出格式为JSON

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
model_sep=1#确定当前模型选择顺序，以便后续写入

#先调用deepssek-chatAPI（非思考模式）
for row_idx, row in enumerate(ws_question.iter_rows(min_row=2, values_only=True), start=2):
    type=row[0]#查看问题类型
    if type=='query':#问题是询问的形式
        try:
            client = OpenAI(
                api_key="sk-71b898da1d6746ff9f127c79d92261ac",
                base_url="https://api.deepseek.com")
            messages = [
                {"role": "system",
                 "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                {"role": "user",
                 "content": "Please provide the answers to the following telecommunications related questions. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"Answer\": \"***\"}"},
                {"role": "user", "content": "{\"Question\":\" " + row[1] + "\"}"}
            ]
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False,
                )
            for round in range(4):
                response1 = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system","content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                        {"role": "user","content": "Please provide a confidence score for the answer based on the question and the given answer. The score should be a natural integer between 0 and 10. If the score is greater than or equal to 7, the answer is considered highly credible. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"score\": \"Specific score\"}"},
                        {"role": "user", "content": "{\"Question\":\" " + row[1] + "\",\""+re.match(pattern, response.choices[0].message.content).group()+"\"}"}
                    ],
                    stream=False
                )
                score = json.loads(re.match(pattern, response1.choices[0].message.content).group())
                if int(score["score"]) >=7:
                    answer = json.loads(re.match(pattern, response.choices[0].message.content).group())
                    ws_answer.cell(row=row_idx, column=model_sep*2-1, value=answer["Answer"])
                    wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
                    break
                else:
                    messages.append(response.choices[0].message)
                    messages.append({"role": "user", "content": "Due to low confidence, please re-enter the output.the answers must also be in a JSON format as follows strictly:{\"Answer\": \"***\"}"})
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages,
                        stream=False,
                        temperature = 0.3,
                        presence_penalty = 0.1,
                        frequency_penalty = 0.1
                    )


        except Exception as e:
            # 捕获异常并记录错误，但不中断循环
            error_msg = f"API调用失败: {str(e)}"
            print(f"deepssek-chatAPI第 {row_idx} 行处理失败: {error_msg}")
            ws_answer.cell(row=row_idx, column=model_sep, value=error_msg)
            # 即使出错也保存，确保错误信息被记录
            wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")





    if type=='option':#问题是可供选择的形式
        try:
            client = OpenAI(
                api_key="sk-71b898da1d6746ff9f127c79d92261ac",
                base_url="https://api.deepseek.com")
            messages = [
                {"role": "system",
                 "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                {"role": "user",
                 "content": "Please provide the answers to the following telecommunications related questions. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"Answer\": \"这里填写具体的选项如Option1\"}，{\"Reason\": \"这里填写原因解释\"}"},
                {"role": "user",
                 "content": "{\"Question\":\" " + row[1] + "\"},{\"Option1\":\" " + row[2] + "\"},{\"Option2\":\" " +
                            row[3] + "\"},{\"Option3\":\" " + row[4] + "\"},{\"Option4\":\" " + row[5] + "\"}"}
            ]
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
                )
            for round in range(4):
                response1 = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                        {"role": "user",
                         "content": "Please provide a confidence score for the answer based on the question and the given answer. The score should be a natural integer between 0 and 10. If the score is greater than or equal to 7, the answer is considered highly credible. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"score\": \"Specific score\"}"},
                        {"role": "user", "content": "{\"Question\":\" " + row[1] + "\",\"" + re.match(pattern,response.choices[0].message.content).group() + "\"}"}
                    ],
                    stream=False
                )
                score = json.loads(re.match(pattern, response1.choices[0].message.content).group())
                if int(score["score"]) >= 7:
                    answer = json.loads(re.match(pattern, response.choices[0].message.content).group())
                    ws_answer.cell(row=row_idx, column=model_sep * 2 - 1, value=answer["Answer"])
                    wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
                    break
                else:
                    messages.append(response.choices[0].message)
                    messages.append({"role": "user",
                                     "content": "Due to low confidence, please re-enter the output.the answers must also be in a JSON format as follows strictly:{\"Answer\": \"这里填写具体的选项如Option1\"}，{\"Reason\": \"这里填写原因解释\"}"})
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages,
                        stream=False,
                        temperature=0.3,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )
        except Exception as e:
            # 捕获异常并记录错误，但不中断循环
            error_msg = f"API调用失败: {str(e)}"
            print(f"deepssek-chatAPI第 {row_idx} 行处理失败: {error_msg}")
            ws_answer.cell(row=row_idx, column=1, value=error_msg)
            # 即使出错也保存，确保错误信息被记录
            wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



model_sep=2#确定当前模型选择顺序，以便后续写入

#先调用deepseek-reasoner（思考模式）
for row_idx, row in enumerate(ws_question.iter_rows(min_row=2, values_only=True), start=2):
    type=row[0]#查看问题类型
    if type=='query':#问题是询问的形式
        try:
            client = OpenAI(
                api_key="sk-71b898da1d6746ff9f127c79d92261ac",
                base_url="https://api.deepseek.com")
            messages = [
                {"role": "system",
                 "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                {"role": "user",
                 "content": "Please provide the answers to the following telecommunications related questions. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"Answer\": \"***\"}"},
                {"role": "user", "content": "{\"Question\":\" " + row[1] + "\"}"}
            ]
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages,
                stream=False
                )
            for round in range(4):
                response1 = client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                        {"role": "user",
                         "content": "Please provide a confidence score for the answer based on the question and the given answer. The score should be a natural integer between 0 and 10. If the score is greater than or equal to 7, the answer is considered highly credible. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"score\": \"Specific score\"}"},
                        {"role": "user", "content": "{\"Question\":\" " + row[1] + "\",\"" + re.match(pattern,response.choices[0].message.content).group() + "\"}"}
                    ],
                    stream=False
                )
                score = json.loads(re.match(pattern, response1.choices[0].message.content).group())
                if int(score["score"]) >= 7:
                    answer = json.loads(re.match(pattern, response.choices[0].message.content).group())
                    ws_answer.cell(row=row_idx, column=model_sep * 2 - 1, value=answer["Answer"])
                    wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
                    break
                else:
                    messages.append(response.choices[0].message)
                    messages.append({"role": "user",
                                     "content": "Due to low confidence, please re-enter the output.the answers must also be in a JSON format as follows strictly:{\"Answer\": \"***\"}"})
                    response = client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=messages,
                        stream=False,
                        temperature=0.3,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )


        except Exception as e:
            # 捕获异常并记录错误，但不中断循环
            error_msg = f"API调用失败: {str(e)}"
            print(f"deepseek-reasoner第 {row_idx} 行处理失败: {error_msg}")
            ws_answer.cell(row=row_idx, column=model_sep, value=error_msg)
            # 即使出错也保存，确保错误信息被记录
            wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")

    if type=='option':#问题是可供选择的形式
        try:
            client = OpenAI(
                api_key="sk-71b898da1d6746ff9f127c79d92261ac",
                base_url="https://api.deepseek.com")

            messages = [
                {"role": "system",
                 "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                {"role": "user",
                 "content": "Please provide the answers to the following telecommunications related questions. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"Answer\": \"这里填写具体的选项如Option1\"}，{\"Reason\": \"这里填写原因解释\"}"},
                {"role": "user",
                 "content": "{\"Question\":\" " + row[1] + "\"},{\"Option1\":\" " + row[2] + "\"},{\"Option2\":\" " +
                            row[3] + "\"},{\"Option3\":\" " + row[4] + "\"},{\"Option4\":\" " + row[5] + "\"}"}
            ]
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages,
                stream=False
            )
            for round in range(4):
                response1 = client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                        {"role": "user",
                         "content": "Please provide a confidence score for the answer based on the question and the given answer. The score should be a natural integer between 0 and 10. If the score is greater than or equal to 7, the answer is considered highly credible. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"score\": \"Specific score\"}"},
                        {"role": "user", "content": "{\"Question\":\" " + row[1] + "\",\"" + re.match(pattern,response.choices[0].message.content).group() + "\"}"}
                    ],
                    stream=False
                )
                score = json.loads(re.match(pattern, response1.choices[0].message.content).group())
                if int(score["score"]) >= 7:
                    answer = json.loads(re.match(pattern, response.choices[0].message.content).group())
                    ws_answer.cell(row=row_idx, column=model_sep * 2 - 1, value=answer["Answer"])
                    wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
                    break
                else:
                    messages.append(response.choices[0].message)
                    messages.append({"role": "user",
                                     "content": "Due to low confidence, please re-enter the output.the answers must also be in a JSON format as follows strictly:{\"Answer\": \"Fill in specific options here, such as Option1\"}，{\"Reason\": \"Fill in the reason explanation here\"}"})
                    response = client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=messages,
                        stream=False,
                        temperature=0.3,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )
        except Exception as e:
            # 捕获异常并记录错误，但不中断循环
            error_msg = f"API调用失败: {str(e)}"
            print(f"deepseek-reasoner第 {row_idx} 行处理失败: {error_msg}")
            ws_answer.cell(row=row_idx, column=1, value=error_msg)
            # 即使出错也保存，确保错误信息被记录
            wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

model_sep = 3  # 确定当前模型选择顺序，以便后续写入

# 调用doubao-seed-1-6-251015
for row_idx, row in enumerate(ws_question.iter_rows(min_row=2, values_only=True), start=2):
    type = row[0]  # 查看问题类型
    if type == 'query':  # 问题是询问的形式
        try:
            client = OpenAI(
                # 此为默认路径，您可根据业务所在地域进行配置
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
                api_key="24dc010a-2688-4c5d-a062-c6fff61291e7",
            )
            messages = [
                {"role": "system",
                 "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                {"role": "user",
                 "content": "Please provide the answers to the following telecommunications related questions. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"Answer\": \"***\"}"},
                {"role": "user", "content": "{\"Question\":\" " + row[1] + "\"}"}
            ]
            response = client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=messages,
                stream=False
            )
            for round in range(4):
                response1 = client.chat.completions.create(
                    model="doubao-seed-1-6-251015",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                        {"role": "user",
                         "content": "Please provide a confidence score for the answer based on the question and the given answer. The score should be a natural integer between 0 and 10. If the score is greater than or equal to 7, the answer is considered highly credible. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"score\": \"Specific score\"}"},
                        {"role": "user", "content": "{\"Question\":\" " + row[1] + "\",\"" + re.match(pattern,response.choices[0].message.content).group() + "\"}"}
                    ],
                    stream=False
                )
                score = json.loads(re.match(pattern, response1.choices[0].message.content).group())
                if int(score["score"]) >= 7:
                    answer = json.loads(re.match(pattern, response.choices[0].message.content).group())
                    ws_answer.cell(row=row_idx, column=model_sep * 2 - 1, value=answer["Answer"])
                    wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
                    break
                else:
                    messages.append(response.choices[0].message)
                    messages.append({"role": "user",
                                     "content": "Due to low confidence, please re-enter the output.the answers must also be in a JSON format as follows strictly:{\"Answer\": \"***\"}"})
                    response = client.chat.completions.create(
                        model="doubao-seed-1-6-251015",
                        messages=messages,
                        stream=False,
                        temperature=0.3,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )


        except Exception as e:
            # 捕获异常并记录错误，但不中断循环
            error_msg = f"API调用失败: {str(e)}"
            print(f"doubao-seed-1-6-251015第 {row_idx} 行处理失败: {error_msg}")
            ws_answer.cell(row=row_idx, column=model_sep, value=error_msg)
            # 即使出错也保存，确保错误信息被记录
            wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")

    if type == 'option':  # 问题是可供选择的形式
        try:
            client = Ark(
                api_key="24dc010a-2688-4c5d-a062-c6fff61291e7",
                # The base URL for model invocation .
                base_url="https://ark.cn-beijing.volces.com/api/v3", )
            messages = [
                {"role": "system",
                 "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                {"role": "user",
                 "content": "Please provide the answers to the following telecommunications related questions. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"Answer\": \"这里填写具体的选项如Option1\"}，{\"Reason\": \"这里填写原因解释\"}"},
                {"role": "user",
                 "content": "{\"Question\":\" " + row[1] + "\"},{\"Option1\":\" " + row[2] + "\"},{\"Option2\":\" " +
                            row[3] + "\"},{\"Option3\":\" " + row[4] + "\"},{\"Option4\":\" " + row[5] + "\"}"}
            ]
            response = client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=messages,
                stream=False
            )
            for round in range(4):
                response1 = client.chat.completions.create(
                    model="doubao-seed-1-6-251015",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert in an telecommunication technical committee. Your role is to give suggestion to the adjudicator who make final decisions."},
                        {"role": "user",
                         "content": "Please provide a confidence score for the answer based on the question and the given answer. The score should be a natural integer between 0 and 10. If the score is greater than or equal to 7, the answer is considered highly credible. The questions will be in a JSON format, the answers must also be in a JSON format as follows strictly:{\"score\": \"Specific score\"}"},
                        {"role": "user", "content": "{\"Question\":\" " + row[1] + "\",\"" + re.match(pattern,response.choices[0].message.content).group() + "\"}"}
                    ],
                    stream=False
                )
                score = json.loads(re.match(pattern, response1.choices[0].message.content).group())
                if int(score["score"]) >= 7:
                    answer = json.loads(re.match(pattern, response.choices[0].message.content).group())
                    ws_answer.cell(row=row_idx, column=model_sep * 2 - 1, value=answer["Answer"])
                    wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")
                    break
                else:
                    messages.append(response.choices[0].message)
                    messages.append({"role": "user",
                                     "content": "Due to low confidence, please re-enter the output.the answers must also be in a JSON format as follows strictly:{\"Answer\": \"Fill in specific options here, such as Option1\"}，{\"Reason\": \"Fill in the reason explanation here\"}"})
                    response = client.chat.completions.create(
                        model="doubao-seed-1-6-251015",
                        messages=messages,
                        stream=False,
                        temperature=0.3,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )
        except Exception as e:
            # 捕获异常并记录错误，但不中断循环
            error_msg = f"API调用失败: {str(e)}"
            print(f"doubao-seed-1-6-251015第 {row_idx} 行处理失败: {error_msg}")
            ws_answer.cell(row=row_idx, column=1, value=error_msg)
            # 即使出错也保存，确保错误信息被记录
            wb_answer.save(r"C:\Users\zhutao\Desktop\TeleMom_answer.xlsx")



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#以下是